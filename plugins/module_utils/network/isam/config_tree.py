# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parse the access-side flat root ('info configure [detail] flat') into a tree.

Line-complete (masked): every 'configure ...' line of the input is stored once on
some leaf, its tokens re-joined with single blanks and secrets masked. Other lines
(echo, '#' delimiters, blanks) are not configuration and are not kept. Paths and
attributes come ONLY from compiled CLI grammar or explicit resource metadata.
Unknown paths are quarantined under __unclassified__; unknown tails are retained as
unparsed lines on the known node. Neither names nor subnodes are guessed or learned
from neighboring lines. The semantic object graph lives separately in topology/.
Completeness concerns the input, not device capture completeness: the flat source
omits evidenced IHUB port/LAG/service sections. Their read-only typed projections
live in ihub_config.py and use separately declared hierarchical sources.

Secrets are masked in the tokens *before* any structuring, so path keys, attribute
values and stored lines all see the same masked tokens. The masking is heuristic,
not a guarantee: it covers values behind secret keywords, any plain:/encrypted:
credential (also behind 'md5:'-style prefixes or fused 'keyword=value'), and reuse
of such a secret as a whole token or ':'/'='-delimited segment elsewhere. A secret
under an unrecognised keyword, or embedded in free text, can still pass. Only
device-masked ('plain:******') placeholders are kept. Each distinct secret becomes
one numbered placeholder ('<redacted:N>'), so instances whose identity is a secret
stay distinct; equal numbers reveal only that two values were equal.

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
# A token is a run of unquoted characters and quoted strings, so a quoted value
# glued to a prefix (password="plain:x", plain:"two words") stays one token.
# An unbalanced quote falls back to a plain whitespace-delimited token.
_TOKEN_RE = re.compile(r'(?:[^\s"]+|"[^"]*")+|\S+')
# Keywords whose following token is a secret value. Exact names plus endings,
# rather than loose suffixes such as "auth"/"key": alarm names like "reg-auth" or
# "ground-key" are identities, and masking after them destroyed data. A "-key"
# ending is a secret only behind a credential qualifier (md5-key, secret-key, ...);
# "key-type" or "ground-key" are not.
_SECRET_WORDS = frozenset(("password", "passwd", "secret", "community", "key", "auth-key", "priv-key",
                           "auth-password", "priv-password", "encryption-key", "shared-secret", "psk"))
_SECRET_COMPACT = frozenset(("password", "passwd", "secret", "community"))  # pass-word, sec_ret
_SECRET_ENDINGS = ("-pwd", "-password", "-passwd", "-secret", "-community", "-psk")
_SECRET_KEY = re.compile(r"(?:[a-z0-9]+-)*(?:md5|sha|sha1|sha256|sha512|hmac|secret|shared|pre-shared|auth|"
                         r"authentication|priv|privacy|encryption|crypto|psk|wpa|wpa2)-key")
# Enumerated keyword values a secret parameter accepts that are not secrets
# themselves (e.g. 'operator X password prompt' asks for the password
# interactively). They stay readable and are never masked elsewhere.
_NON_SECRET_VALUES = frozenset(("prompt", "none", "no", "plain", "encrypted", "default", "disable",
                                "disabled", "enable", "enabled", "null", "not-applicable", "auto"))
# 'plain:' / 'encrypted:' credential markers, at the token start or after ':', '='
# or a quote (md5:plain:x, sha1:encrypted:0x.., password="plain:x").
_CREDENTIAL = re.compile(r'(?i)(?:^|(?<=[:="]))(?:plain|encrypted):')
_PLACEHOLDER = re.compile(r"<redacted(?::\d+)?>")


def _is_secret(word):
    word = str(word).lower().replace("_", "-")
    if word in _SECRET_WORDS or word.replace("-", "") in _SECRET_COMPACT or word.endswith(_SECRET_ENDINGS):
        return True
    return bool(_SECRET_KEY.fullmatch(word))


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
    if not isinstance(value, str) or _PLACEHOLDER.fullmatch(value):
        return value
    if _CREDENTIAL.search(_unquote(value)) and not _is_masked_placeholder(value):
        return REDACTED
    if _is_secret(name) and not _is_masked_placeholder(value) and value not in _NON_SECRET_VALUES:
        return REDACTED
    return value


def _is_masked_placeholder(value):
    """A device-masked credential: 'plain:******' (optionally behind 'md5:' etc.)."""
    match = _CREDENTIAL.search(_unquote(value))
    if match is None or match.group(0).lower() != "plain:":
        return False
    return bool(re.fullmatch(r"\*+", _unquote(value)[match.end():].strip('"')))


# A secret seen on one line is masked wherever else it appears as a whole token or
# a ':'/'='-delimited segment of one (e.g. a community inside 'v2c:<community>').
# Substrings and '-' segments are not matched: a community 'public' must not turn a
# VLAN name 'public-internet' into a different identity. Very short and purely
# numeric values are not propagated: 'key 100' would otherwise mask every VLAN 100.
_MIN_KNOWN_SECRET = 4


def _is_policy_node(tokens, i):
    """'system security password ...' is the password policy node, not a credential."""
    return i == 2 and list(tokens[:3]) == ["system", "security", "password"]


def _holds_secret(tokens, i):
    """Whether tokens[i + 1] is a secret: the value of a secret keyword."""
    if i + 1 >= len(tokens) or _is_policy_node(tokens, i) or not _is_secret(tokens[i]):
        return False
    value = tokens[i + 1]
    return (value not in _NON_SECRET_VALUES and not _is_masked_placeholder(value)
            and not _PLACEHOLDER.fullmatch(value))


def _fused(token):
    """('password=', 'value') for a fused 'keyword=value' token with a secret keyword."""
    keyword, sep, value = token.partition("=")
    if sep and value and _is_secret(keyword):
        return keyword + sep, value
    return None


def _cleartext(value):
    """The secret part of a value: unquoted, after any 'md5:plain:' style prefix."""
    value = _unquote(value)
    marker = None
    for marker in _CREDENTIAL.finditer(value):
        pass
    if marker is not None and marker.group(0).lower() == "plain:":
        value = _unquote(value[marker.end():])
    return value


def _registrable(value):
    return (len(value) >= _MIN_KNOWN_SECRET and not value.isdigit() and value.lower() not in _NON_SECRET_VALUES
            and not _CREDENTIAL.search(value) and not _PLACEHOLDER.fullmatch(value) and not re.fullmatch(r"\*+", value))


def _known_secrets(token_lists):
    """Cleartext secret values seen anywhere in the input (to mask their reuse)."""
    known = set()
    for tokens in token_lists:
        for i, token in enumerate(tokens):
            candidates = []
            if _holds_secret(tokens, i):
                candidates.append(tokens[i + 1])
            fused = _fused(token)
            if fused:
                candidates.append(fused[1])
            if token == "snmp-version" and i + 1 < len(tokens):
                parts = split_snmp_version(_unquote(tokens[i + 1]))
                if parts:
                    candidates.append(parts[1])
            match = _CREDENTIAL.search(token)
            if match and not _is_masked_placeholder(token):
                candidates.append(token[match.start():])
            known.update(v for v in (_cleartext(c) for c in candidates) if _registrable(v))
    return known


class _Masker(object):
    """Masks secrets with numbered placeholders, one number per distinct secret.

    Distinct numbers keep instances distinct when a secret is part of an identity
    (two SNMP communities with the same host address stay two tree leaves).
    """

    def __init__(self, known=()):
        self.known = frozenset(known)
        self.numbers = {}

    def placeholder(self, value):
        key = _cleartext(value)
        if key not in self.numbers:
            self.numbers[key] = len(self.numbers) + 1
        return "<redacted:%d>" % self.numbers[key]

    def credential(self, token):
        """Mask a token's plain:/encrypted: credential, keeping a 'md5:' style prefix."""
        if _PLACEHOLDER.fullmatch(token) or _is_masked_placeholder(token):
            return token
        inner = _unquote(token)
        match = _CREDENTIAL.search(inner)
        if not match:
            return token
        prefix = inner[:match.start()]
        if prefix.endswith('"'):
            prefix = prefix[:-1]
        return prefix + self.placeholder(inner[match.start():])

    def segments(self, token):
        """Mask known secrets as a whole token or ':'/'='-delimited segments."""
        if not self.known or _PLACEHOLDER.fullmatch(token):
            return token
        if _unquote(token) in self.known:
            return self.placeholder(token)
        parts = re.split(r"([:=])", token)
        masked = [self.placeholder(part) if part in self.known or _unquote(part) in self.known else part
                  for part in parts]
        return "".join(masked)

    def tokens(self, tokens):
        out = list(tokens)
        for i, token in enumerate(out):
            if _PLACEHOLDER.fullmatch(token):
                continue
            if token == "snmp-version" and i + 1 < len(out):
                parts = split_snmp_version(_unquote(out[i + 1]))
                if parts:
                    out[i + 1] = parts[0] + self.placeholder(parts[1])
            elif _holds_secret(out, i):
                out[i + 1] = self.placeholder(out[i + 1])
            fused = _fused(token)
            if fused and not _is_masked_placeholder(fused[1]) and fused[1] not in _NON_SECRET_VALUES:
                out[i] = fused[0] + self.placeholder(fused[1])
                continue
            out[i] = self.segments(self.credential(out[i]))
        return out


def _redact_tokens(tokens, known=()):
    """Mask secrets in one line's tokens before structuring, even at unknown CLI paths.

    Heuristic, not a proof: values behind secret keywords, any plain:/encrypted:
    credential (also behind 'md5:'/'sha1:' prefixes or fused 'kw=value'), and the
    ``known`` cleartext secrets seen elsewhere in the same input are masked. Only
    device-masked placeholders ('plain:******') are kept.
    """
    return _Masker(known).tokens(tokens)


def redacted_token_lines(text):
    """Token lists (without 'configure') of every configure line, secrets masked.

    Two passes: secrets found anywhere (behind secret keywords or as credentials)
    are collected first, then masked wherever they reappear as a whole token or a
    ':'/'='-delimited segment. One distinct secret maps to one numbered placeholder
    ('<redacted:N>') across the whole input.
    """
    raw = []
    for line in str(text or "").splitlines():
        line = line.strip()
        if line.startswith("configure "):
            raw.append(_tokens(line)[1:])
    masker = _Masker(_known_secrets(raw))
    return [masker.tokens(tokens) for tokens in raw]


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
    """Nested tree of the whole flat configuration. Line-complete (masked).

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
