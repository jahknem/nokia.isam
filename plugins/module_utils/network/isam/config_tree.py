# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parse the access-side flat root ('info configure [detail] flat') into a tree.

Lossless: every configure line is kept (raw, secrets masked). Paths and attributes
come ONLY from compiled CLI grammar or explicit resource metadata. Unknown paths
are quarantined under __unclassified__; unknown tails are retained as unparsed
lines on the known node. Neither names nor subnodes are guessed or learned from
neighboring lines. The semantic object graph lives separately in topology/.
Losslessness concerns the input, not device capture completeness: the flat source
omits evidenced IHUB port/LAG/service sections. Their read-only typed projections
live in ihub_config.py and use separately declared hierarchical sources.

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


def _tokens(line):
    return _TOKEN_RE.findall(line)


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


def _parse_attrs(tokens, attrs):
    """Parse only declared fields; return (attributes, unconsumed tail).

    Stop at the first unknown token. Skipping it could mistake an unknown value
    for a known attribute and fabricate configuration.
    """
    out = {}
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "no" and i + 1 < len(tokens) and tokens[i + 1] in attrs:
            out[tokens[i + 1]] = False
            i += 2
            continue
        if t not in attrs:
            break
        if attrs[t].get("value", False):
            if i + 1 >= len(tokens):
                break
            out[t] = _unquote(tokens[i + 1])
            i += 2
        else:
            out[t] = True
            i += 1
    return out, tokens[i:]


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
    candidates = []
    for metadata in resource_grammar():
        consumed = _consume_path(tokens, metadata["path"])
        if consumed is not None:
            path, rest, shape = consumed
            if path == ["system", "security"] and rest and rest[0] != "no" and rest[0] not in metadata["attrs"]:
                continue
            if shape == ("system", "id") and len(path) == 3 and path[-1] in metadata["attrs"]:
                continue  # legacy 'system id name X' has no node-id identity
            if metadata["positionals"] and rest:
                rest = [metadata["positionals"][0], rest[0]] + rest[1:]
            candidates.append(_Line(order, stored, list(path), list(rest), tuple(shape), metadata["attrs"], "resource"))
    for node, metadata in CONFIG_GRAMMAR.items():
        consumed = _consume_path(tokens, metadata["path"])
        if consumed is not None:
            path, rest, shape = consumed
            candidates.append(_Line(order, stored, list(path), list(rest), tuple(shape), metadata["attrs"], "grammar"))
    if candidates:
        # Deepest declared path wins. Explicit resource metadata wins equal
        # paths, but never invents a deeper child from neighboring output.
        return max(candidates, key=lambda line: (len(line.path), line.source == "resource"))
    return _Line(order, stored, ["__unclassified__", str(order)], [], ("unclassified",), {}, "unclassified")


def _nest(tree, line):
    node = tree
    for token in line.path:
        node = node.setdefault(token, {})
    leaf = node.setdefault("__config__", {"attrs": {}, "lines": [], "node": " ".join(line.shape),
                                          "source": line.source.split("+")[0]})
    attributes, unparsed = _parse_attrs(line.rest, line.attrs)
    for k, v in attributes.items():
        leaf["attrs"][k] = _redact(k, v)
    leaf["lines"].append(line.stored)
    if unparsed or line.source == "unclassified":
        leaf.setdefault("unparsed", []).append(line.stored)


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
    "source": "grammar" | "resource" | "unclassified"}} under declared CLI paths.
    Unknown syntax remains redacted in lines/unparsed, never guessed into attrs.
    """
    lines = _parsed_lines(text)
    tree = {}
    for line in lines:
        _nest(tree, line)
    return tree


def nesting_stats(text):
    """Line counts by declared path source (grammar / resource / unclassified)."""
    lines = _parsed_lines(text)
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
         "unclaimed": {node: n_lines},
         "unparsed": {node: n_lines}}

    'node' is the leaf's keyword path (e.g. 'qos interface queue'); an attribute is
    unmodelled when its snake_case name is not an option anywhere in the family argspec.
    Only keyword-shaped names leave the report. A token that is not
    (a value the tree parsed into a name position) is counted per family under
    "value_like" and never shown; path parts of that kind become "<value>".
    Unknown tokens are never interpreted as attribute names. Their redacted
    lines are counted separately in unparsed, without exposing unknown values.
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
    unparsed = {}

    def walk(node):
        for key, value in node.items():
            if key != "__config__":
                walk(value)
                continue
            lines = value.get("lines") or []
            if not lines:
                continue
            node_name = _safe_node(value.get("node", ""))
            if value.get("unparsed"):
                unparsed[node_name] = unparsed.get(node_name, 0) + len(value["unparsed"])
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
    return {"families": families, "unclaimed": unclaimed, "unparsed": unparsed}
