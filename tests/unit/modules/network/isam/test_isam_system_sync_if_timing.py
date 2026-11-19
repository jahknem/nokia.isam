"""isam_system: configure system sync-if-timing (structure from the lab device's detail capture)."""
import pathlib
import shlex

import pytest
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties

from ansible_collections.nokia.isam.plugins.modules import isam_system
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
    parse_sync_if_timing,
    render_sync_if_timing,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures

ignore_provider_arg = True
CAPTURE_DIR = lab_captures.CAPTURE_DIR
DETAIL = CAPTURE_DIR / "root-detail-flat.txt"
CONFIGURED = CAPTURE_DIR / "root-flat.txt"
PREFIX = "configure system sync-if-timing"

# non-default lines covering every node
DEVICE = [
    PREFIX + " revert wait-time 300 output-ql-thresh clk-ql-dnu ssmout-en-bits ssmout-ceiling clk-ql-prc ais-sensitivity enable",
    PREFIX + " bits e1",
    PREFIX + " bits-bind bits-a-bind nt-a bits-b-bind nt-b",
    PREFIX + " force-reference synce-1",
    PREFIX + " ref-order prio1 synce-1",
    PREFIX + " ref-order prio2 bits-a",
    PREFIX + " ssm bits-a ssmenable default-ql clk-ql-ssu-a target-ql clk-ql-dnu",
    PREFIX + " ssm synce-1 default-ql clk-ql-prc target-ql clk-ql-sec",
    PREFIX + " synce synce-1 nt-a:xfp:1",
    PREFIX + " synce synce-2 none",
    PREFIX + " ssmout-synce nt-a:xfp:1 ssmout-enable",
]


def _parse(lines):
    sync = {}
    unknown = []
    for line in lines:
        if not parse_sync_if_timing(shlex.split(line)[3:], sync):
            unknown.append(line)
    return sync, unknown


def test_parse_every_node():
    sync, unknown = _parse(DEVICE)
    assert unknown == []
    assert sync["revert"] is True and sync["wait_time"] == 300 and sync["ais_sensitivity"] == "enable"
    assert sync["bits"] == "e1"
    assert sync["bits_bind"] == {"bits_a_bind": "nt-a", "bits_b_bind": "nt-b"}
    assert sync["force_reference"] == "synce-1"
    assert sync["ref_order"] == {"prio1": "synce-1", "prio2": "bits-a"}
    assert sync["ssm"][0] == {"reference": "bits-a", "ssmenable": True, "default_ql": "clk-ql-ssu-a", "target_ql": "clk-ql-dnu"}
    assert sync["synce"][0] == {"reference": "synce-1", "port": "nt-a:xfp:1"}
    assert sync["ssmout_synce"] == [{"port": "nt-a:xfp:1", "ssmout_enable": True}]


def test_render_round_trip():
    sync, _unknown = _parse(DEVICE)
    again, unknown = _parse(render_sync_if_timing(sync))
    assert unknown == []
    assert again == sync


@pytest.mark.skipif(not DETAIL.exists(), reason="lab capture not available")
@pytest.mark.parametrize("path", [DETAIL, CONFIGURED])
def test_capture_every_line_is_parsed(path):
    lines = [line for line in path.read_text().splitlines() if line.startswith(PREFIX + " ")]
    assert lines
    sync, unknown = _parse(lines)
    assert unknown == []
    # and rendering what was parsed gives the same structure back (facts drop empty blocks)
    again, unknown = _parse(render_sync_if_timing(sync))
    assert unknown == [] and remove_empties(again) == remove_empties(sync)
    if path == DETAIL:
        assert len(lines) == 24
        assert len(sync["ssm"]) == 6 and len(sync["synce"]) == 2 and len(sync["ssmout_synce"]) == 10


class TestIsamSystemSyncIfTiming(TestIsamModule):
    module = isam_system

    def setUp(self):
        super(TestIsamSystemSyncIfTiming, self).setUp()
        self.mocks = [patch(target) for target in (
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.system.system.Isam_systemFacts.get_config",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )]
        started = [m.start() for m in self.mocks]
        self.get_config = started[1]
        self.get_config.return_value = "\n".join(DEVICE) + "\n"

    def tearDown(self):
        super(TestIsamSystemSyncIfTiming, self).tearDown()
        for mock in self.mocks:
            mock.stop()

    def _run(self, state, config, changed):
        set_module_args(dict(state=state, config=config), ignore_provider_arg)
        return self.execute_module(changed=changed)

    def test_gathered(self):
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        gathered = self.execute_module(changed=False)["gathered"]["sync_if_timing"]
        assert gathered["ref_order"]["prio1"] == "synce-1"
        assert len(gathered["ssm"]) == 2

    def test_merged_idempotent(self):
        sync, _unknown = _parse(DEVICE)
        self._run("merged", {"sync_if_timing": sync}, changed=False)

    def test_merged_changes_only_what_differs(self):
        result = self._run("merged", {"sync_if_timing": {
            "wait_time": 600,
            "ref_order": {"prio2": "none"},
            "ssm": [{"reference": "synce-1", "ssmenable": True}, {"reference": "bits-a", "ssmenable": True}],
            "ssmout_synce": [{"port": "nt-b:xfp:1", "ssmout_enable": True}],
        }}, changed=True)
        assert result["commands"] == [
            PREFIX + " wait-time 600",
            PREFIX + " ref-order prio2 none",
            PREFIX + " ssm synce-1 ssmenable",
            PREFIX + " ssmout-synce nt-b:xfp:1 ssmout-enable",
        ]

    def test_replaced_resets_unwanted(self):
        result = self._run("replaced", {"sync_if_timing": {
            "revert": True, "wait_time": 300, "output_ql_thresh": "clk-ql-dnu", "ssmout_en_bits": True,
            "ssmout_ceiling": "clk-ql-prc", "ais_sensitivity": "enable", "bits": "e1",
            "bits_bind": {"bits_a_bind": "nt-a"},
            "ref_order": {"prio1": "synce-1"},
            "ssm": [{"reference": "bits-a", "ssmenable": True, "default_ql": "clk-ql-ssu-a", "target_ql": "clk-ql-dnu"}],
            "synce": [{"reference": "synce-1", "port": "nt-a:xfp:1"}],
            "ssmout_synce": [{"port": "nt-a:xfp:1", "ssmout_enable": True}],
        }}, changed=True)
        assert sorted(result["commands"]) == sorted([
            PREFIX + " bits-bind no bits-b-bind",
            PREFIX + " force-reference none",
            PREFIX + " ref-order prio2 none",
            PREFIX + " ssm synce-1 no default-ql no target-ql",
            PREFIX + " synce synce-2 none",
        ])

    def test_deleted_resets_section(self):
        set_module_args(dict(state="deleted", config={"sync_if_timing": {"bits": "e1"}}), ignore_provider_arg)
        result = self.execute_module(changed=True)
        commands = result["commands"]
        assert PREFIX + " no revert no wait-time no output-ql-thresh no ssmout-en-bits no ssmout-ceiling no ais-sensitivity" in commands
        assert PREFIX + " no bits" in commands
        assert PREFIX + " force-reference none" in commands
        assert PREFIX + " ref-order prio1 none" in commands
        assert PREFIX + " ssm bits-a no ssmenable no default-ql no target-ql" in commands
        assert PREFIX + " synce synce-1 none" in commands
        assert PREFIX + " ssmout-synce nt-a:xfp:1 no ssmout-enable" in commands
        assert not any("id " in c or "sntp" in c for c in commands)

    def test_deleted_other_section_keeps_sync(self):
        self.get_config.return_value = "\n".join(DEVICE + ["configure system syslog server 10.0.0.2"]) + "\n"
        set_module_args(dict(state="deleted", config={"syslog": {"server": "10.0.0.2"}}), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert not any("sync-if-timing" in c for c in result["commands"])
