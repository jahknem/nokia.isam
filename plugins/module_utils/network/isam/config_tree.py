# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parse a whole ISAM configuration ('info configure [detail] flat') into a nested tree.

Lossless: every configure line is kept (raw, secrets masked) at the leaf of its CLI path.
The path/attribute split works in three layers:

1. Grammar: nodes compiled from the CLI help (config_grammar.py) give the exact path
   structure (keywords, identity slots) and the attribute keywords.
2. Heuristic frame: lines without a grammar node are split at the first identity token
   (an index such as 1/1/3/1, a number, a quoted string) or the first 'no'.
Resource schemas supplement missing grammar for security, profiles and timing nodes;
their explicit identity slots also cover lowercase names and compound identities.

3. Learned sub-nodes: a keyword after the node identity that the grammar does not know
   and that is followed by 'no <attr>' or by an index, on a line that is not the first
   line of its node (or that repeats per node, e.g. 'queue 0', 'queue 1'), is a sub-node
   (e.g. 'equipment ont interface <id> tc-layer', 'qos interface <id> queue <n>').
   The decision is learned per node type across the whole capture, so it is consistent.

Secrets are masked in the tokens *before* any structuring, so neither path keys, nor
attribute values, nor stored lines can carry a cleartext secret or encrypted
credential. Only device-masked ('plain:******') placeholders are kept.

This is the schema-less "root" view; the resource families remain the typed view of the
parts they model. gap_report compares the two.
"""
from __future__ import absolute_import, division, print_function

import re

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_grammar import CONFIG_GRAMMAR
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    split_snmp_version,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree_metadata import (
    modelled_name,
    resource_grammar,
)

REDACTED = "<redacted>"
_TOKEN_RE = re.compile(r'"[^"]*"|\S+')
# Keywords whose following token is a secret value. Exact names (plus -pwd/-password/
# -secret endings) rather than suffixes such as "auth"/"key": alarm names like
# "reg-auth" or "ground-key" are identities, and masking after them destroyed data.
_SECRET_WORDS = frozenset(("password", "passwd", "secret", "community", "key", "auth-key", "priv-key",
                           "auth-password", "priv-password", "encryption-key", "shared-secret", "psk"))
_SECRET_ENDINGS = ("-pwd", "-password", "-passwd", "-secret")


def _is_secret(word):
    word = str(word).lower()
    return word in _SECRET_WORDS or word.endswith(_SECRET_ENDINGS)
_INDEX = re.compile(r"^[\d/:.\-]+$|^\d")
_WORD = re.compile(r"^[a-z][a-z0-9_/-]*$")
_MASKED = ("plain:", "encrypted:")
_MAX_SUBNODE_DEPTH = 4
_MAX_WORD_PATH = 4


def _tokens(line):
    return _TOKEN_RE.findall(line)


def _is_identity(token):
    return token.startswith('"') or bool(_INDEX.match(token)) or token == REDACTED


def _looks_like_identity(token):
    """Identity for the heuristic frame: an index/number/quoted/masked token, a mixed-case
    name ('RADPol') or an index with a type prefix ('stacked:552:0', 'lt:1/1/2')."""
    if token == "no":
        return False
    return (_is_identity(token) or token.lower() != token
            or (":" in token and any(c.isdigit() for c in token) and not token.startswith(_MASKED)))


def _is_word(token):
    return token != "no" and bool(_WORD.match(token))


def _node_for(keywords):
    """Longest grammar node whose keyword path prefixes the line's leading keywords."""
    best = None
    for node in CONFIG_GRAMMAR:
        n = len(node)
        if n <= len(keywords) and tuple(keywords[:n]) == node:
            if best is None or n > len(best):
                best = node
    return best


def _leading_keywords(tokens):
    out = []
    for t in tokens:
        if t == "no" or _is_identity(t):
            break
        out.append(t)
    return out


def _split(tokens, attrs):
    """Split tokens into (path, attribute tokens) at the first known attribute keyword."""
    names = set(attrs)
    for i, t in enumerate(tokens):
        if t in names or (t == "no" and i + 1 < len(tokens) and tokens[i + 1] in names):
            return tokens[:i], tokens[i:]
    return tokens, []


def _consume_path(tokens, structure):
    """Walk the grammar path structure over the line tokens; return (path, rest, shape).

    Keywords must match; identity/value slots consume one token each. The rest are
    attributes (known or not). Returns None if the line does not fit the structure.
    """
    path = []
    shape = []
    i = 0
    for item in structure:
        if i >= len(tokens):
            return None
        if item[0] == "kw":
            if tokens[i] != item[1]:
                return None
            shape.append(tokens[i])
        path.append(tokens[i])
        i += 1
    return path, tokens[i:], tuple(shape)


def _heuristic_frame(tokens):
    """(path, rest, shape) for a line without a grammar node.

    The path runs over the leading keywords and the first identity token; keyword +
    identity pairs after it are left to the sub-node learning. A line with no identity
    at all is split before a secret keyword / 'no' / its last 'name value' pair, but
    after at most _MAX_WORD_PATH keywords.
    """
    kws = []
    i = 0
    while i < len(tokens) and tokens[i] != "no" and not _looks_like_identity(tokens[i]):
        if i >= 2 and _is_secret(tokens[i]) and tokens[i] != "community" and i + 1 < len(tokens):
            break  # 'operator x password encrypted:..': password is an attribute
        kws.append(tokens[i])
        i += 1
    if i < len(tokens) and kws and _looks_like_identity(tokens[i]):
        return kws + [tokens[i]], tokens[i + 1:], tuple(kws)
    if i == len(tokens) and len(kws) >= 2:
        cut = max(1, min(len(kws) - 2, _MAX_WORD_PATH))
        return kws[:cut], tokens[cut:], tuple(kws[:cut])
    if not kws:
        return tokens[:1], tokens[1:], tuple(tokens[:1])
    cut = min(len(kws), _MAX_WORD_PATH)
    return kws[:cut], tokens[cut:], tuple(kws[:cut])


def _parse_attrs(tokens, attrs, names=None):
    """Attribute tokens -> {name: value}. 'no X' -> False; bare flag -> True; else value.

    attrs: grammar metadata (exact); names: further tokens known to be attribute names
    for this node type (learned from 'no <name>' in the capture), never taken as values.
    """
    out = {}
    i = 0
    names = set(attrs) | set(names or ())
    while i < len(tokens):
        t = tokens[i]
        if t == "no" and i + 1 < len(tokens):
            out[tokens[i + 1]] = False
            i += 2
            continue
        nxt = tokens[i + 1] if i + 1 < len(tokens) else None
        if t in attrs:
            takes_value = attrs[t].get("value", False)
        else:
            # Unknown attribute: infer a value unless the next token starts another
            # attribute (a known/learned name or 'no'). Raw line is kept regardless.
            takes_value = nxt is not None
        if takes_value and nxt is not None and nxt not in names and nxt != "no":
            out[t] = _unquote(nxt)
            i += 2
        else:
            out[t] = True
            i += 1
    return out


def _unquote(v):
    return v[1:-1] if len(v) >= 2 and v.startswith('"') and v.endswith('"') else v


def _redact(name, value):
    if isinstance(value, str) and (value.lower().startswith("encrypted:") or
                                 (_is_secret(name) and not _is_masked_placeholder(value))):
        return REDACTED
    return value


def _is_masked_placeholder(value):
    return bool(re.fullmatch(r"plain:\*+", _unquote(value)))


# A secret seen on one line is masked wherever else it appears inside a token. Very
# short values are left out: masking every occurrence of e.g. 'ab' would destroy
# unrelated data, and real secrets are longer.
_MIN_KNOWN_SECRET = 3


def _is_policy_node(tokens, i):
    """'system security password ...' is the password policy node, not a credential."""
    return i == 2 and list(tokens[:3]) == ["system", "security", "password"]


def _holds_secret(tokens, i):
    """Whether tokens[i + 1] is a cleartext secret: the value of a secret keyword."""
    if i + 1 >= len(tokens) or _is_policy_node(tokens, i) or not _is_secret(tokens[i]):
        return False
    return tokens[i + 1] != "no" and not _is_masked_placeholder(tokens[i + 1])


def _known_secrets(token_lists):
    """Cleartext secret values seen behind a secret keyword anywhere in the input."""
    known = set()
    for tokens in token_lists:
        for i in range(len(tokens)):
            if _holds_secret(tokens, i):
                value = _unquote(tokens[i + 1])
                if not value.lower().startswith("encrypted:") and len(value) >= _MIN_KNOWN_SECRET:
                    known.add(value)
    return known


def _redact_tokens(tokens, known=()):
    """Strip encrypted credentials before structuring, even at unknown CLI paths.

    Secret values are masked; only actual device-masked placeholders are retained.
    ``known`` are cleartext secrets seen elsewhere in the same input (e.g. an SNMP
    community): they are masked wherever they reappear inside another token.
    """
    out = [REDACTED if _unquote(t).lower().startswith("encrypted:") else t for t in tokens]
    for i, token in enumerate(out):
        if token == "snmp-version" and i + 1 < len(out):
            parts = split_snmp_version(_unquote(out[i + 1]))
            if parts:
                out[i + 1] = parts[0] + REDACTED
        elif _holds_secret(out, i):
            out[i + 1] = REDACTED
    for secret in sorted(known, key=len, reverse=True):
        out = [t.replace(secret, REDACTED) if secret in t and t != REDACTED else t for t in out]
    return out


def redacted_token_lines(text):
    """Token lists (without 'configure') of every configure line, secrets masked.

    Two passes: secrets found behind secret keywords on any line are masked wherever
    else they appear, so a secret embedded in another value never survives.
    """
    raw = []
    for line in str(text or "").splitlines():
        line = line.strip()
        if line.startswith("configure "):
            raw.append(_tokens(line)[1:])
    known = _known_secrets(raw)
    return [_redact_tokens(tokens, known) for tokens in raw]


class _Line(object):
    __slots__ = ("order", "stored", "path", "rest", "shape", "attrs", "source")

    def __init__(self, order, stored, path, rest, shape, attrs, source):
        self.order = order
        self.stored = stored
        self.path = path
        self.rest = rest
        self.shape = shape
        self.attrs = attrs
        self.source = source


def _frame(order, tokens, stored):
    for metadata in resource_grammar():
        consumed = _consume_path(tokens, metadata["path"])
        if consumed is not None:
            path, rest, shape = consumed
            if path == ["system", "security"] and rest and rest[0] != "no" and rest[0] not in metadata["attrs"]:
                continue  # unknown security child: retain heuristic nesting
            if shape == ("system", "id") and len(path) == 3 and path[-1] in metadata["attrs"]:
                continue  # legacy 'system id name X' has no node-id identity
            if metadata["positionals"] and rest:
                rest = [metadata["positionals"][0], rest[0]] + rest[1:]
            return _Line(order, stored, list(path), list(rest), tuple(shape), metadata["attrs"], "resource")
    node = _node_for(_leading_keywords(tokens))
    if node:
        attrs = CONFIG_GRAMMAR[node]["attrs"]
        consumed = _consume_path(tokens, CONFIG_GRAMMAR[node]["path"])
        if consumed is None:
            path, rest = _split(tokens, attrs)
            shape = node
        else:
            path, rest, shape = consumed
        return _Line(order, stored, list(path), list(rest), tuple(shape), attrs, "grammar")
    path, rest, shape = _heuristic_frame(tokens)
    return _Line(order, stored, list(path), list(rest), tuple(shape), {}, "heuristic")


def _negated_names(lines):
    """{shape: names seen as 'no <name>'} -- attribute names, never sub-nodes or values."""
    names = {}
    for line in lines:
        bucket = names.setdefault(line.shape, set(line.attrs))
        rest = line.rest
        for i in range(len(rest) - 1):
            if rest[i] == "no":
                bucket.add(rest[i + 1])
    return names


def _learn_subnodes(lines, names):
    """Per shape: {keyword: takes_identity} for keywords that open a sub-node."""
    groups = {}
    for line in lines:
        groups.setdefault((line.shape, tuple(line.path)), []).append(line)
    learned = {}
    for (shape, _path), members in groups.items():
        first = min(m.order for m in members)
        seen = {}
        for m in members:
            rest = m.rest
            if not rest:
                continue
            k = rest[0]
            if not _is_word(k) or k in m.attrs or k in names.get(shape, ()):
                continue
            nxt = rest[1] if len(rest) > 1 else None
            seen.setdefault(k, set()).add(nxt)
            if m.order == first:
                continue
            if nxt == "no":
                learned.setdefault(shape, {}).setdefault(k, False)
            elif nxt is not None and _is_identity(nxt):
                learned.setdefault(shape, {})[k] = True
            elif nxt is not None and _is_word(nxt) and len(rest) > 2 and rest[2] == "no" \
                    and nxt not in names.get(shape, ()):
                learned.setdefault(shape, {}).setdefault(k, False)  # 'utilization threshold no x'
        for k, followers in seen.items():
            followers.discard("no")
            followers.discard(None)
            if len(followers) >= 2:  # repeated per node: a list sub-node ('queue 0', 'queue 1')
                learned.setdefault(shape, {})[k] = True
    return learned


def _structure(lines):
    """Extend line frames by learned sub-nodes, level by level."""
    active = list(lines)
    for _depth in range(_MAX_SUBNODE_DEPTH):
        names = _negated_names(active)
        learned = _learn_subnodes(active, names)
        if not learned:
            break
        changed = []
        for line in active:
            subs = learned.get(line.shape)
            if not subs or not line.rest or line.rest[0] not in subs:
                continue
            k = line.rest[0]
            line.path.append(k)
            line.rest = line.rest[1:]
            if subs[k] and line.rest and line.rest[0] != "no" and (_is_identity(line.rest[0]) or _is_word(line.rest[0])):
                line.path.append(line.rest[0])
                line.rest = line.rest[1:]
            line.shape = line.shape + (k,)
            line.attrs = {}
            line.source += "+subnode"
            changed.append(line)
        if not changed:
            break
        active = changed
    return _negated_names(lines)


def _nest(tree, line, names):
    node = tree
    for token in line.path:
        node = node.setdefault(token, {})
    leaf = node.setdefault("__config__", {"attrs": {}, "lines": [], "node": " ".join(line.shape),
                                          "source": line.source.split("+")[0]})
    attributes = _parse_attrs(line.rest, line.attrs, names.get(line.shape))
    for k, v in attributes.items():
        leaf["attrs"][k] = _redact(k, v)
    leaf["lines"].append(line.stored)


def _parsed_lines(text):
    lines = []
    for tokens in redacted_token_lines(text):  # secrets masked before any structuring
        if not tokens:
            continue
        lines.append(_frame(len(lines), tokens, "configure " + " ".join(tokens)))
    return lines


def parse_config_tree(text):
    """Nested tree of the whole flat configuration. Lossless (raw lines kept, masked).

    Leaves are {"__config__": {"attrs": {...}, "lines": [...], "node": "<keyword path>",
    "source": "grammar" | "resource" | "heuristic"}} under the CLI path (keywords and identities).
    """
    lines = _parsed_lines(text)
    names = _structure(lines)
    tree = {}
    for line in lines:
        _nest(tree, line, names)
    return tree


def nesting_stats(text):
    """Line counts by how the path was found (grammar / heuristic, with learned sub-nodes)."""
    lines = _parsed_lines(text)
    _structure(lines)
    stats = {}
    for line in lines:
        stats[line.source] = stats.get(line.source, 0) + 1
    return stats


# ------------------------------------------------------------------------- gap report

_FAMILY_ARGSPEC_ALIASES = {
    "efm_oam_interface": "efm_oam",
    "isam_equipment": "isam_equipment",
}


def _snake(name):
    return name.replace("-", "_").replace("/", "_")


def _argspec_option_names(spec):
    """Every option name of an argspec (nested), with its aliases, in snake_case.

    Some families keep the CLI spelling as option key (qos_profiles `q0-priority`) or
    reach it through an alias; all of these count as modelled.
    """
    names = set()
    for key, value in (spec or {}).items():
        names.add(_snake(key))
        if isinstance(value, dict):
            names |= {_snake(alias) for alias in value.get("aliases") or []}
            names |= _argspec_option_names(value.get("options"))
    return names


def load_argspec_names(families=None):
    """{family: set(option names) or None} from plugins/module_utils/network/isam/argspec."""
    import importlib

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
        RESOURCE_CONFIG_PREFIXES,
    )

    out = {}
    for family in families or RESOURCE_CONFIG_PREFIXES:
        candidates = [_FAMILY_ARGSPEC_ALIASES.get(family), family]
        if family.startswith("isam_"):
            candidates.append(family[len("isam_"):])
        out[family] = None
        for mod in [c for c in candidates if c]:
            try:
                module = importlib.import_module(
                    "ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.%s.%s" % (mod, mod))
            except ImportError:
                continue
            for value in vars(module).values():
                spec = getattr(value, "argument_spec", None)
                if isinstance(spec, dict):
                    out[family] = _argspec_option_names(spec)
                    break
            if out[family] is not None:
                break
    return out


def _owner(line, prefixes, excludes):
    best = None
    for family, family_prefixes in prefixes.items():
        if any(line.startswith(p) for p in excludes.get(family, ())):
            continue
        for p in family_prefixes:
            if line.startswith(p) and (best is None or len(p) > best[1]):
                best = (family, len(p))
    return best[0] if best else None


_KEYWORD = re.compile(r"^[a-z][a-z0-9_-]*$")


def _safe_name(name):
    """Only CLI-keyword-shaped strings may leave the report; values never do."""
    return isinstance(name, str) and bool(_KEYWORD.match(name)) and len(name) <= 64


def _safe_node(node_name):
    return " ".join(part if _safe_name(part) else "<value>" for part in str(node_name).split())


def gap_report(tree, argspec_names=None, prefixes=None, excludes=None):
    """What the root tree contains that the resource families do not model.

    Pure over its inputs (argspec_names/prefixes/excludes default to the collection's).
    Returns::

        {"families": {family: {"argspec": bool, "lines": n,
                               "unmodelled": {node: [attr, ...]}}},
         "unclaimed": {node: n_lines}}

    'node' is the leaf's keyword path (e.g. 'qos interface queue'); an attribute is
    unmodelled when its snake_case name is not an option anywhere in the family argspec.
    Only keyword-shaped names leave the report. A token that is not
    (a value the tree parsed into a name position) is counted per family under
    "value_like" and never shown; path parts of that kind become "<value>".
    Heuristic nodes may still mistake an unknown lowercase identity/value for a
    keyword. This is a diagnostic, not a general-purpose anonymisation guarantee.
    """
    if prefixes is None or excludes is None:
        from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
            RESOURCE_CONFIG_EXCLUDES,
            RESOURCE_CONFIG_PREFIXES,
        )

        prefixes = RESOURCE_CONFIG_PREFIXES if prefixes is None else prefixes
        excludes = RESOURCE_CONFIG_EXCLUDES if excludes is None else excludes
    if argspec_names is None:
        argspec_names = load_argspec_names(list(prefixes))

    families = {}
    unclaimed = {}

    def walk(node):
        for key, value in node.items():
            if key != "__config__":
                walk(value)
                continue
            lines = value.get("lines") or []
            if not lines:
                continue
            node_name = _safe_node(value.get("node", ""))
            owner = _owner(lines[0] + " ", prefixes, excludes)
            if owner is None:
                unclaimed[node_name] = unclaimed.get(node_name, 0) + len(lines)
                continue
            known = argspec_names.get(owner)
            entry = families.setdefault(owner, {"argspec": known is not None, "lines": 0, "unmodelled": {}, "value_like": 0})
            entry["lines"] += len(lines)
            names = list(value.get("attrs", {}))
            entry["value_like"] += sum(1 for a in names if not _safe_name(a))
            missing = sorted(a for a in names if _safe_name(a) and (
                known is None or (_snake(a) not in known and not modelled_name(owner, node_name, a, known))
            ))
            if missing:
                bucket = entry["unmodelled"].setdefault(node_name, [])
                entry["unmodelled"][node_name] = sorted(set(bucket) | set(missing))

    walk(tree)
    return {"families": families, "unclaimed": unclaimed}
