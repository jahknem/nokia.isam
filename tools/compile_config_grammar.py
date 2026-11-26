#!/usr/bin/env python
"""Compile the rm_models CLI syntaxes into a shipped grammar for the root config tree.

Reads every rm_models/configure/**/help.txt (falling back to parsed.json 'raw') and
extracts the "Command Syntax" block(s). The device help is hard-wrapped at 80 columns,
so a line that fills the terminal width is continued *without* a separator (the wrap
can split a word, e.g. 'xg-pm-collec' + 't'), while shorter lines are soft word wraps.
parsed.json 'syntax' is not used: it is empty for most nodes and keeps wrap artefacts.

Per CLI node the compiler records the path structure (fixed keywords, identity slots and
identity values) and the attribute keywords (whether each takes a value and can be
negated with 'no'). It writes a dependency-free data module
plugins/module_utils/network/isam/config_grammar.py used by the root parser at runtime.

Path/attribute rules:
  * '( no X (id) ... ) | ( X (id) ... )' create/delete alternation: everything in the
    'no' branch is identity (path); mandatory 'kw <Type>' pairs that only appear in the
    create branch are attributes.
  * Outside an alternation, 'kw <Type>' chained directly after an identity slot is an
    identity extension (e.g. 'qos tca (index) queue <q>'); before any identity it is a
    mandatory attribute (e.g. 'alarm log-sev-level <sev>').
  * '[ ... ]' groups are attributes.

rm_models is not shipped; this compiled grammar is. Run after the CLI model changes:
    python tools/compile_config_grammar.py
"""
from __future__ import absolute_import, division, print_function

import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WRAP = 80
_WORD = re.compile(r"[a-z][a-z0-9_/-]*$")


# --------------------------------------------------------------------------- extraction

def extract_syntaxes(help_text, width=WRAP):
    """Return the joined syntax strings of a help text's 'Command Syntax' section.

    A physical line of >= width characters that does not end in a blank is a terminal
    hard wrap: the next line is appended verbatim (even if it starts with '>'). Other
    lines are word wraps and are joined with a single space. A new block starts at '> '.
    """
    text = help_text.replace("\r", "")
    if "Command Syntax" not in text:
        return []
    section = text.split("Command Syntax", 1)[1]
    section = re.split(r"\n(?:Command Parameters|Command Output)\b", section, maxsplit=1)[0]
    blocks = []
    cur = None
    hard = False
    for line in section.split("\n"):
        if cur is not None and hard:
            cur += line
        elif line.startswith("> "):
            if cur is not None:
                blocks.append(cur)
            cur = line
        elif cur is not None and line.strip():
            cur = cur.rstrip() + " " + line.strip()
        elif cur is not None:
            blocks.append(cur)
            cur = None
        # The help formatter word-wraps with a trailing blank (even on a full 80-column
        # line); only a full line *without* one is a terminal hard wrap.
        hard = len(line) >= width and not line[-1:].isspace()
    if cur is not None:
        blocks.append(cur)
    return [re.sub(r"\s+", " ", b).strip() for b in blocks if b.strip().startswith("> configure")]


# ------------------------------------------------------------------------------ parsing

def _tokens(syntax):
    """Split a syntax string into words, <Type> placeholders and grouping punctuation."""
    syntax = syntax.strip()
    if syntax.startswith(">"):
        syntax = syntax[1:]
    return re.findall(r"\(|\)|\[|\]|\||<[^>]*>|[^\s()\[\]|<>]+", syntax)


def _balanced(toks, i, open_, close):
    """toks[i] == open_; return (inner tokens, index after the matching close)."""
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


def _is_word(tok):
    return bool(_WORD.match(tok)) and tok != "no"


def _is_slot(toks, i):
    """'(name)' identity placeholder at toks[i]?"""
    return (i + 2 < len(toks) and toks[i] == "(" and toks[i + 2] == ")"
            and _is_word(toks[i + 1]))


def _add_attr(attrs, name, value=False, negatable=False, required=False):
    meta = attrs.setdefault(name, {"value": False, "negatable": False})
    meta["value"] = meta["value"] or bool(value)
    meta["negatable"] = meta["negatable"] or bool(negatable)
    if required:
        meta["required"] = True


def _attr_group(inner, attrs):
    """Attributes of one '[ ... ]' group (recursing into nested groups)."""
    i = 0
    while i < len(inner):
        t = inner[i]
        if t == "[":
            sub, j = _balanced(inner, i, "[", "]")
            if [w for w in sub if w != "|"] == ["no"]:  # '[ no ] X'
                if j < len(inner) and _is_word(inner[j]):
                    _add_attr(attrs, inner[j], value=j + 1 < len(inner) and inner[j + 1].startswith("<"),
                              negatable=True)
                    j += 1
            else:
                _attr_group(sub, attrs)
            i = j
            continue
        if _is_word(t):
            negated = i > 0 and inner[i - 1] == "no"
            takes = i + 1 < len(inner) and inner[i + 1].startswith("<")
            _add_attr(attrs, t, value=takes, negatable=negated)
        i += 1


def _walk(toks, path, attrs, in_alternation_create=False, skip=None):
    """Walk a token run: path items appended to 'path', attributes to 'attrs'.

    skip: identity path already taken from the 'no' branch; matching leading items of
    the create branch are not duplicated.
    """
    i = 0
    skip = list(skip or [])
    seen_attr = False
    while i < len(toks):
        t = toks[i]
        if t == "[":
            inner, i = _balanced(toks, i, "[", "]")
            _attr_group(inner, attrs)
            seen_attr = True
            continue
        if t == "(" and _is_slot(toks, i):
            if skip and skip[0] == ("id",):
                skip.pop(0)
            elif not seen_attr:
                path.append(("id",))
            i += 3
            continue
        if t == "(":
            inner, j = _balanced(toks, i, "(", ")")
            # look for a create/delete alternation: ( no ... ) | ( ... )
            if inner and inner[0] == "no" and j < len(toks) and toks[j] == "|" and j + 1 < len(toks) and toks[j + 1] == "(":
                create, k = _balanced(toks, j + 1, "(", ")")
                ident = []
                _walk(inner[1:], ident, {})
                path.extend(ident)
                _walk(create, path, attrs, in_alternation_create=True, skip=ident)
                i = k
                continue
            if all(_is_word(w) or w == "|" for w in inner):
                # '(restart)' / '( a | b )': a flag or enumerated action
                for w in inner:
                    if _is_word(w):
                        _add_attr(attrs, w)
                seen_attr = True
                i = j
                continue
            _walk(inner, path, attrs, in_alternation_create, skip)
            i = j
            continue
        if t in ("|", ")", "]", "configure", "no"):
            i += 1
            continue
        if t.startswith("<"):
            if not seen_attr:
                path.append(("val",))
            i += 1
            continue
        if _is_word(t):
            nxt = toks[i + 1] if i + 1 < len(toks) else ""
            if skip and skip[0] == ("kw", t):
                skip.pop(0)
                if nxt.startswith("<") and skip and skip[0] == ("val",):
                    skip.pop(0)
                    i += 2
                else:
                    i += 1
                continue
            if nxt.startswith("<"):
                chained = bool(path) and path[-1][0] in ("id", "val")
                if in_alternation_create or seen_attr or not chained:
                    _add_attr(attrs, t, value=True, required=True)
                    seen_attr = True
                else:
                    path.extend([("kw", t), ("val",)])
                i += 2
                continue
            if seen_attr:
                _add_attr(attrs, t)
            else:
                path.append(("kw", t))
            i += 1
            continue
        i += 1


def parse_syntax(syntax):
    """Return (path, attrs) for one syntax string.

    path: ordered structure as ('kw', word) fixed keywords, ('id',) identity slots and
          ('val',) identity values.
    attrs: {name: {"value": bool, "negatable": bool[, "required": True]}}.
    """
    path = []
    attrs = {}
    _walk(_tokens(syntax), path, attrs)
    return path, attrs


def node_key(path):
    """Grammar key: the leading fixed keywords of the path."""
    key = []
    for item in path:
        if item[0] != "kw":
            break
        key.append(item[1])
    return tuple(key)


def compile_nodes(model_root):
    """{node key: {"path": [...], "attrs": {...}}} from every help text under model_root."""
    nodes = {}
    skipped = []
    for help_path in sorted(glob.glob(os.path.join(model_root, "**", "help.txt"), recursive=True)):
        with open(help_path, errors="replace") as fh:
            text = fh.read()
        syntaxes = extract_syntaxes(text)
        if not syntaxes:
            parsed = os.path.join(os.path.dirname(help_path), "parsed.json")
            if os.path.exists(parsed):
                try:
                    with open(parsed) as fh:
                        syntaxes = extract_syntaxes(json.load(fh).get("raw") or "")
                except ValueError:
                    pass
        if not syntaxes:
            continue
        rel = os.path.dirname(os.path.relpath(help_path, model_root))
        for syntax in syntaxes:
            path, attrs = parse_syntax(syntax)
            key = node_key(path)
            if not key:
                skipped.append(rel)
                continue
            if key in nodes:
                for name, meta in attrs.items():
                    _add_attr(nodes[key]["attrs"], name, **meta)
            else:
                nodes[key] = {"path": path, "attrs": attrs}
    return nodes, skipped


def render(nodes):
    out = ['"""Compiled CLI grammar (from rm_models syntaxes); see tools/compile_config_grammar.py.\n',
           "node path -> attribute keywords. Generated; do not edit by hand.",
           '"""\n',
           "from __future__ import absolute_import, division, print_function\n",
           "__metaclass__ = type\n",
           "CONFIG_GRAMMAR = {"]
    for key in sorted(nodes):
        node = nodes[key]
        attrs = dict(sorted(node["attrs"].items()))
        out.append("    %r: %r," % (key, {"path": node["path"], "attrs": attrs}))
    out.append("}\n")
    return "\n".join(out)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    model_root = argv[0] if argv else os.path.join(ROOT, "rm_models/configure")
    nodes, skipped = compile_nodes(model_root)
    out = os.path.join(ROOT, "plugins/module_utils/network/isam/config_grammar.py")
    with open(out, "w") as fh:
        fh.write(render(nodes))
    print("compiled %d nodes -> %s" % (len(nodes), out))
    if skipped:
        print("skipped (no keyword path): %s" % ", ".join(skipped))


if __name__ == "__main__":
    main()
