# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Sync and shape of the inlined read_outcomes RETURN docs.

The read_outcomes return documentation is written once in
plugins/doc_fragments/read_outcomes.py and inlined into every targeted
module's RETURN block between sync markers (tools/sync_read_outcomes_docs.py).
It is intentionally not referenced with ``extends_documentation_fragment``:
return-section doc fragments only work on ansible-core 2.20+, and this
collection must keep working on older releases (where such a reference
crashes ``ansible-doc`` with "dictionary update sequence element #0 has
length 1; 2 is required").
"""
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[5]
FRAGMENT = ROOT / "plugins" / "doc_fragments" / "read_outcomes.py"
SYNC_TOOL = ROOT / "tools" / "sync_read_outcomes_docs.py"
REF = "extends_documentation_fragment: nokia.isam.read_outcomes"


def _canonical_yaml():
    source = FRAGMENT.read_text()
    match = re.search(r"RETURN = r\"\"\"\n(.*?)\n\"\"\"", source, re.S)
    assert match, "the fragment file lost its RETURN yaml"
    return match.group(1)


def test_fragment_yaml_is_well_formed():
    data = yaml.safe_load(_canonical_yaml())
    assert set(data) == {"read_outcomes"}
    entry = data["read_outcomes"]
    assert entry["type"] == "dict"
    assert entry["returned"]
    assert isinstance(entry["description"], list) and entry["description"]
    assert all(isinstance(line, str) for line in entry["description"])


def test_no_module_references_the_fragment():
    # A return-section doc fragment reference crashes ansible-doc on
    # ansible-core < 2.20; the docs must stay inlined.
    offenders = [
        path.name
        for path in sorted((ROOT / "plugins" / "modules").glob("*.py"))
        if REF in path.read_text()
    ]
    assert not offenders, offenders


def test_read_outcomes_docs_are_in_sync():
    result = subprocess.run(
        [sys.executable, str(SYNC_TOOL), "--check"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        cwd=str(ROOT),
    )
    assert result.returncode == 0, result.stdout
