#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Sync the read_outcomes RETURN docs from the fragment into every targeted module.

The read_outcomes return documentation is written once in
plugins/doc_fragments/read_outcomes.py and inlined into each targeted
module's RETURN block between the BEGIN/END markers below. It is
intentionally not referenced with ``extends_documentation_fragment``:
return-section doc fragments only work on ansible-core 2.20+, and this
collection must keep working on older releases (where such a reference
crashes ``ansible-doc``).

Edit the fragment, then run (from the repository root):

    python tools/sync_read_outcomes_docs.py          # rewrite the modules
    python tools/sync_read_outcomes_docs.py --check  # verify only (CI)
"""

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRAGMENT = ROOT / "plugins" / "doc_fragments" / "read_outcomes.py"
BEGIN = "# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)"
END = "# END read_outcomes"
REF = "extends_documentation_fragment: nokia.isam.read_outcomes"


def _registry():
    """The targeted resources from the pure-data registry (no Ansible needed)."""
    spec = importlib.util.spec_from_file_location(
        "isam_targeted", ROOT / "plugins" / "module_utils" / "network" / "isam" / "targeted.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TARGETED_GATHER


def _module_name(resource):
    return resource if resource.startswith("isam_") else "isam_" + resource


def canonical_block():
    source = FRAGMENT.read_text()
    match = re.search(r"RETURN = r\"\"\"\n(.*?)\n\"\"\"", source, re.S)
    if not match:
        raise SystemExit("cannot find the RETURN yaml in %s" % FRAGMENT)
    return "%s\n%s\n%s" % (BEGIN, match.group(1), END)


def _sync_module(text, block):
    """(new_text, status): 'ok', 'updated' or 'missing' (no safe auto-insert)."""
    if BEGIN in text:
        match = re.search(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", text, re.S)
        if match.group(0) == block + "\n":
            return text, "ok"
        return text[:match.start()] + block + "\n" + text[match.end():], "updated"
    if REF + "\n" in text:
        return text.replace(REF + "\n", block + "\n", 1), "updated"
    # No block yet: append it at the end of the module's RETURN yaml.
    match = re.search(r'^RETURN = r?("""|\'\'\')\n(.*?)\n?\1', text, re.S | re.M)
    if match:
        end = match.end(2)
        return text[:end] + ("\n" if match.group(2).strip() else "") + block + text[end:], "updated"
    return text, "missing"


def main(argv):
    check = "--check" in argv
    block = canonical_block()
    modules_dir = ROOT / "plugins" / "modules"
    problems = []
    resources = _registry()

    # 1. every targeted module carries the inlined block, exactly
    for resource in sorted(resources):
        path = modules_dir / (_module_name(resource) + ".py")
        if not path.exists():
            problems.append("%s: no module for resource %s" % (path.name, resource))
            continue
        text = path.read_text()
        final, status = _sync_module(text, block)
        if status == "missing":
            problems.append("%s: RETURN block missing the synced read_outcomes docs" % path.name)
        elif status == "updated":
            if check:
                problems.append("%s: read_outcomes docs out of sync with the fragment" % path.name)
            else:
                path.write_text(final)
                print("updated %s" % path.name)
        if REF in (final if status != "missing" else text):
            problems.append(
                "%s: still references the doc fragment (breaks ansible-core < 2.20)" % path.name)

    # 2. no non-targeted module carries the block
    expected = {_module_name(resource) for resource in resources}
    for path in sorted(modules_dir.glob("*.py")):
        if path.name == "__init__.py" or path.stem in expected:
            continue
        if BEGIN in path.read_text():
            problems.append("%s: carries the read_outcomes docs but is not a targeted module" % path.name)

    if problems:
        for problem in problems:
            print("PROBLEM: %s" % problem)
        return 1
    print("read_outcomes docs in sync (%d modules)" % len(expected))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
