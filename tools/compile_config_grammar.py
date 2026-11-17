#!/usr/bin/env python
"""Compile the rm_models CLI syntaxes into a shipped grammar for the root config tree.

Reads every rm_models/configure/**/parsed.json 'syntax' string and extracts, per CLI
node: the fixed path keywords (with identity slots) and the attribute keywords (whether
each takes a value and can be negated with 'no'). Writes a dependency-free data module
plugins/module_utils/network/isam/config_grammar.py used by the root parser at runtime.

rm_models is not shipped; this compiled grammar is. Run after the CLI model changes.
"""
from __future__ import absolute_import, division, print_function

import glob
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _tokens(syntax):
    """Split a syntax string into words and the grouping punctuation."""
    syntax = syntax.lstrip("> ").strip()
    return re.findall(r"\(|\)|\[|\]|\||<[^>]*>|[^\s()\[\]|<>]+", syntax)


def parse_syntax(syntax):
    """Return (path, attrs).

    path: ordered structure of the node, as ('kw', word) fixed keywords, ('id',)
          identity slots and ('val',) typed positional values, up to the attributes.
    attrs: {name: {"value": bool, "negatable": bool}} from the bracketed groups.
    """
    toks = _tokens(syntax)
    path = []
    i = 0
    while i < len(toks):
        t = toks[i]
        if t == "[":
            break
        if t == "|":
            i += 1
            continue
        if t == "(":
            inner, i = _balanced(toks, i, "(", ")")
            # Form B '( custom-profile (name) [...] )': a keyword plus a nested identity.
            # Form A '(ont-idx)': a bare identity placeholder.
            if "(" in inner:
                kw = [w for w in inner if re.fullmatch(r"[a-z][a-z0-9-]*", w) and w != "no"]
                if kw:
                    path.append(("kw", kw[0]))
                path.append(("id",))
            else:
                path.append(("id",))
            continue
        if t.startswith("<"):
            path.append(("val",))
            i += 1
            continue
        if t == "configure":
            i += 1
            continue
        if re.fullmatch(r"[a-z][a-z0-9-]*", t):
            path.append(("kw", t))
            i += 1
            continue
        i += 1
    attrs = _attr_groups(toks)
    # The create/delete alternation '( no X (id) ) | ( X (id) [...] )' yields the same
    # (keyword, identity) pair twice; collapse consecutive repeats.
    cleaned = []
    for item in path:
        if len(cleaned) >= 2 and item == cleaned[-2] and cleaned[-1] == ("id",) and item[0] == "kw":
            cleaned.pop()  # drop the duplicate keyword; its identity slot stays once
            continue
        cleaned.append(item)
    return cleaned, attrs


def _balanced(toks, i, open_, close):
    depth = 0
    start = i
    while i < len(toks):
        if toks[i] == open_:
            depth += 1
        elif toks[i] == close:
            depth -= 1
            if depth == 0:
                return toks[start + 1:i], i + 1
        i += 1
    return toks[start + 1:], i


def _structure(inner):
    """Keywords + identity slots inside a ( ) branch, ignoring nested [ ] attrs."""
    path = []
    attrs = {}
    i = 0
    while i < len(inner):
        t = inner[i]
        if t == "[":
            _, i = _balanced(inner, i, "[", "]")
            continue
        if t == "(":
            sub, i = _balanced(inner, i, "(", ")")
            p, a = _structure(sub)
            path.extend(p)
            attrs.update(a)
            continue
        if t == "no" or t == "|":
            i += 1
            continue
        if t.startswith("<"):
            path.append(("val",))
            i += 1
            continue
        if re.fullmatch(r"[a-z][a-z0-9-]*", t):
            # a keyword followed by (identity) is a node keyword; a bare word that is
            # an identity placeholder name like 'index'/'ont-idx' is an identity slot.
            path.append(("kw", t))
            i += 1
            continue
        i += 1
    return path, attrs


def _attr_groups(toks):
    """Extract attribute names from [ ... ] groups: '[ no X | X <Type> ]', '[ [no] X ]'."""
    attrs = {}
    i = 0
    while i < len(toks):
        if toks[i] == "[":
            inner, i = _balanced(toks, i, "[", "]")
            # split on top-level '|'
            words = [w for w in inner if w not in ("[", "]", "|", "no") and not w.startswith("<") and w not in ("(", ")")]
            negatable = "no" in inner
            names = [w for w in words if re.fullmatch(r"[a-z][a-z0-9-]*", w)]
            takes_value = any(w.startswith("<") for w in inner)
            for n in names:
                meta = attrs.setdefault(n, {"value": False, "negatable": False})
                meta["value"] = meta["value"] or takes_value
                meta["negatable"] = meta["negatable"] or negatable
            continue
        i += 1
    return attrs


def main():
    nodes = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "rm_models/configure/**/parsed.json"), recursive=True)):
        try:
            data = json.load(open(path))
        except Exception:
            continue
        syntax = data.get("syntax") or ""
        if not syntax.startswith("> configure"):
            continue
        rel = os.path.relpath(path, os.path.join(ROOT, "rm_models/configure"))
        cli_path = os.path.dirname(rel).split(os.sep)
        cli_path = [p for p in cli_path if p and p != "."]
        try:
            p, attrs = parse_syntax(syntax)
        except Exception:
            continue
        nodes[tuple(cli_path)] = {"path": p, "attrs": attrs}
    out = os.path.join(ROOT, "plugins/module_utils/network/isam/config_grammar.py")
    with open(out, "w") as fh:
        fh.write('"""Compiled CLI grammar (from rm_models syntaxes); see tools/compile_config_grammar.py.\n\n')
        fh.write('node path -> attribute keywords. Generated; do not edit by hand.\n"""\n\n')
        fh.write("from __future__ import absolute_import, division, print_function\n\n__metaclass__ = type\n\n")
        fh.write("CONFIG_GRAMMAR = {\n")
        for key in sorted(nodes):
            fh.write("    %r: %r,\n" % (key, nodes[key]))
        fh.write("}\n")
    print("compiled %d nodes -> %s" % (len(nodes), out))


if __name__ == "__main__":
    main()
