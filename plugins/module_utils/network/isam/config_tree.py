# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parse a whole ISAM configuration ('info configure [detail] flat') into a nested tree.

Lossless: every configure line is kept (raw) and nested by its CLI path; attributes are
split from the path using the compiled CLI grammar (config_grammar.py). Lines whose node
has no grammar fall back to a keyword/identity heuristic and are still kept verbatim, so
nothing is dropped. Secret attribute values are redacted by name.

This is the schema-less "root" view; the resource families remain the typed view of the
parts they model. Comparing the two shows what is not yet modelled (see gap_report).
"""
from __future__ import absolute_import, division, print_function

import re

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_grammar import CONFIG_GRAMMAR

_TOKEN_RE = re.compile(r'"[^"]*"|\S+')
_SECRET = re.compile(r"(pwd|password|secret|community|key|auth)$", re.I)
_INDEX = re.compile(r"^[\d/:.\-]+$|^\d")


def _tokens(line):
    return _TOKEN_RE.findall(line)


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
        if t.startswith('"') or _INDEX.match(t):
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
    """Walk the grammar path structure over the line tokens; return (path, rest).

    Keywords must match; identity/value slots consume one token each. The rest are
    attributes (known or not). Returns None if the line does not fit the structure.
    """
    path = []
    i = 0
    for item in structure:
        if i >= len(tokens):
            return None
        if item[0] == "kw":
            if tokens[i] != item[1]:
                return None
            path.append(tokens[i])
        else:  # id / val: one identity or positional value token
            path.append(tokens[i])
        i += 1
    return path, tokens[i:]


def _parse_attrs(tokens, attrs):
    """Attribute tokens -> {name: value}. 'no X' -> False; bare flag -> True; else value."""
    out = {}
    i = 0
    names = set(attrs)
    while i < len(tokens):
        t = tokens[i]
        if t == "no" and i + 1 < len(tokens):
            out[tokens[i + 1]] = False
            i += 2
            continue
        if t in attrs:
            takes_value = attrs[t].get("value", False)
        else:
            # Unknown attribute: infer a value unless the next token starts another
            # attribute (a known keyword or 'no'). Raw line is kept regardless.
            takes_value = i + 1 < len(tokens) and tokens[i + 1] != "no" and tokens[i + 1] not in names
        if takes_value and i + 1 < len(tokens) and tokens[i + 1] not in names and tokens[i + 1] != "no":
            out[t] = _unquote(tokens[i + 1])
            i += 2
        else:
            out[t] = True
            i += 1
    return out


def _unquote(v):
    return v[1:-1] if len(v) >= 2 and v.startswith('"') and v.endswith('"') else v


def _redact(name, value):
    if _SECRET.search(name) and isinstance(value, str) and not value.startswith(("plain:", "encrypted:")):
        return "<redacted>"
    return value


def _redact_tokens(tokens):
    """Mask secret values in a raw token list (community/password/secret/... followed by
    a cleartext value). Device-masked (plain:) and hashed (encrypted:) values are kept."""
    out = list(tokens)
    for i, token in enumerate(out):
        if _SECRET.search(token) and i + 1 < len(out):
            nxt = out[i + 1]
            if not nxt.startswith(("plain:", "encrypted:")) and nxt != "no":
                out[i + 1] = "<redacted>"
    return out


def _nest(tree, path, attributes, raw):
    node = tree
    for token in path:
        node = node.setdefault(token, {})
    leaf = node.setdefault("__config__", {"attrs": {}, "lines": []})
    for k, v in attributes.items():
        leaf["attrs"][k] = _redact(k, v)
    leaf["lines"].append(raw)


def parse_config_tree(text):
    """Nested tree of the whole flat configuration. Lossless (raw lines kept)."""
    tree = {}
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line.startswith("configure "):
            continue
        tokens = _tokens(line)[1:]  # drop 'configure'
        stored = "configure " + " ".join(_redact_tokens(tokens))  # secrets masked
        keywords = _leading_keywords(tokens)
        node = _node_for(keywords)
        attrs = CONFIG_GRAMMAR[node]["attrs"] if node else {}
        if node:
            consumed = _consume_path(tokens, CONFIG_GRAMMAR[node]["path"])
            if consumed is None:
                path, attr_tokens = _split(tokens, attrs)
            else:
                path, attr_tokens = consumed
            attributes = _parse_attrs(attr_tokens, attrs)
            _nest(tree, path, attributes, stored)
        else:
            # No grammar (an unmodelled region): keep it losslessly at branch granularity
            # with the raw tokens, rather than guessing attribute structure. It becomes a
            # proper subtree once a family/grammar entry exists. gap_report flags it.
            path = tokens[:2]
            leaf = tree
            for token in path:
                leaf = leaf.setdefault(token, {})
            entry = leaf.setdefault("__config__", {"attrs": {}, "lines": [], "raw_tokens": []})
            entry["lines"].append(stored)
            entry["raw_tokens"].append(_redact_tokens(tokens[2:]))
    return tree


def gap_report(tree):
    """What the root tree contains that the resource families do not model.

    Returns {node_path: {"unclaimed": bool, "unmodelled_attrs": [...]}} using the family
    prefixes and the grammar. 'unclaimed' nodes have no resource family at all.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
        RESOURCE_CONFIG_PREFIXES,
    )

    prefixes = ["configure " + " ".join(node) + " " for node in CONFIG_GRAMMAR]
    report = {}

    def walk(node, path):
        for key, value in node.items():
            if key == "__config__":
                cli = "configure " + " ".join(path) + " "
                claimed = any(cli.startswith(p) for ps in RESOURCE_CONFIG_PREFIXES.values() for p in ps)
                if value.get("raw_tokens"):
                    report[" ".join(path)] = {"unclaimed": not claimed, "unmodelled_attrs": [], "no_grammar": True}
                    continue
                grammar_node = _node_for(path)
                known = set(CONFIG_GRAMMAR[grammar_node]["attrs"]) if grammar_node else set()
                unmodelled = sorted(k for k in value["attrs"] if k not in known)
                if not claimed or unmodelled:
                    report[" ".join(path)] = {"unclaimed": not claimed, "unmodelled_attrs": unmodelled}
                continue
            walk(value, path + [key])

    walk(tree, [])
    return report
