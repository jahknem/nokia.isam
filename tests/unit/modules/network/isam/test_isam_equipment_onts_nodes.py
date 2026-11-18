"""isam_equipment_onts: sw-ctrl cfgfiles/delay-act, interface sub-nodes, loop and pm-collect nodes."""
import os
import re

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_equipment_onts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import (
    Equipment_ontsFacts,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args

# Lab captures (info configure detail flat / info configure flat) in the sibling
# pon-migration-planner checkout; the capture tests skip when they are absent.
CAPTURES = os.environ.get("ISAM_ROOT_CAPTURES") or os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    *([os.pardir] * 6 + ["pon-migration-planner", ".local"])
)
DETAIL = os.path.join(CAPTURES, "root-detail-flat.txt")
CONFIGURED = os.path.join(CAPTURES, "root-flat.txt")

DETAIL_LINES = "\n".join([
    "configure equipment ont interface 1/1/2/1/1 sw-ver-pland auto sernum GNXS:00000001 no desc1 log-auth-pwd plain:****** no vtfd",
    "configure equipment ont interface 1/1/2/1/1 tc-layer no olt-pm-collect no od-pm-collect no ont-pm-collect",
    "configure equipment ont interface 1/1/2/1/1 tc-layer-threshold no lost-frags-down no lost-frags-up no bad-headers-down",
    "configure equipment ont interface 1/1/2/1/1 delay-act no at",
    "configure equipment ont interface 1/1/2/1/1 xg-tc-layer olt-pm-collect enable no ont-pm-collect",
    "configure equipment ont interface 1/1/2/1/1 no slid-visibility admin-state up",
    "configure equipment ont slot 1/1/2/1/1/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0 no port-type",
    "configure equipment ont sw-ctrl 1 hw-version 3FE47211AB* ont-variant DO plnd-sw-version 3FE45655AOCK85"
    " no pland-cfgfile1 pland-cfgfile2 CFG2 no dnload-cfgfile1 no dnload-cfgfile2",
    "configure equipment ont sw-ctrl 1 delay-act no at",
    "configure equipment ont sw-ctrl 2 hw-version G2110BV2*",
    "configure equipment ont sw-ctrl 2 delay-act at 2026-01-01:00:00:00",
    "configure equipment ont loop 1/1/2/1/1 no loop-detect no loop-portautoshut",
    "configure equipment ont loop 1/1/2/1/2 loop-detect enable loop-portautoshut disable",
    "configure equipment ont loop 1/1/2/1/3 loop-detect no-control loop-portautoshut enable",
    "configure equipment ont pm-collect 1/1/2/1/1 no xg-pm-collect",
    "configure equipment ont pm-collect 1/1/2/1/2 xg-pm-collect enable",
    "configure equipment ont interface 1/1/2/1/1 future-keyword 7 no other-future",
    "configure equipment ont gis 1/1/2/1/1 no olt-location",
])


def parse(text):
    return Equipment_ontsFacts(module=None)._parse_config(text)


def test_detail_output_parses_new_fields_and_drops_defaults():
    parsed = parse(DETAIL_LINES)
    interface = parsed["interfaces"][0]
    assert interface["sernum"] == "GNXS:00000001"
    assert interface["admin_state"] == "up"
    assert interface["xg_tc_layer"] == {"olt_pm_collect": "enable"}
    assert "future_keyword" not in interface and "7" not in interface
    sw_ctrls = dict((entry["sw_ctrl_id"], entry) for entry in parsed["sw_ctrls"])
    assert sw_ctrls[1]["pland_cfgfile2"] == "CFG2"
    assert "pland_cfgfile1" not in sw_ctrls[1]
    assert sw_ctrls[2]["delay_act"] == {"at": "2026-01-01:00:00:00"}
    # Loop/pm-collect nodes with only defaults (no <attr> or the default value) are not reported.
    assert parsed["loops"] == [{"ont_idx": "1/1/2/1/2", "loop_detect": "enable", "loop_portautoshut": "disable"}]
    assert parsed["pm_collects"] == [{"ont_idx": "1/1/2/1/2", "xg_pm_collect": "enable"}]


def _relevant(line):
    """(node, identity, sub-node, [(attr, value)]) of a line; ``no <attr>`` pairs carry no value."""
    tokens = re.findall(r'"[^"]*"|\S+', line[len("configure equipment ont "):])
    node, ident, rest = tokens[0], tokens[1], tokens[2:]
    sub = None
    if rest and rest[0] in Equipment_ontsFacts._nodes()[node][4]:
        sub, rest = rest[0], rest[1:]
    pairs, index = [], 0
    while index < len(rest):
        if rest[index] == "no":
            index += 2
            continue
        pairs.append((rest[index], rest[index + 1].strip('"')))
        index += 2
    return node, ident, sub, pairs


@pytest.mark.parametrize("capture", [DETAIL, CONFIGURED])
def test_real_captures_parse_and_validate_completely(capture):
    if not os.path.exists(capture):
        pytest.skip("capture %s not available" % capture)
    with open(capture) as handle:
        lines = [line.rstrip() for line in handle if line.startswith("configure equipment ont ")]
    assert lines
    facts = Equipment_ontsFacts(module=None)
    parsed = facts._parse_config("\n".join(lines))
    assert facts.unknown == []
    # Gathering validates against the argspec: no unsupported parameters.
    ansible_facts = {"ansible_network_resources": {}}
    facts.populate_facts(None, ansible_facts, data="\n".join(lines))
    gathered = ansible_facts["ansible_network_resources"]["equipment_onts"]

    nodes = Equipment_ontsFacts._nodes()
    for line in lines:
        node, ident, sub, pairs = _relevant(line)
        section, key, int_identity, fields, subs = nodes[node]
        defaults = dict((cli, default) for cli, (_field, default) in fields.items())
        ident = int(ident) if int_identity else ident
        entry = [item for item in gathered.get(section, []) if item[key] == ident]
        relevant = [(attr, value) for attr, value in pairs if defaults.get(attr) != value]
        if not relevant:
            continue
        assert entry, line
        for attr, value in relevant:
            if sub:
                sub_key, sub_fields = subs[sub]
                got = entry[0][sub_key][sub_fields[attr][0]]
            else:
                got = entry[0][fields[attr][0]]
            if attr in ("plndnumdataports", "plndnumvoiceports"):
                value = int(value)
            assert got == value, (line, attr)
    assert len(parsed["interfaces"]) == len(set(line.split()[4] for line in lines if line.split()[3] == "interface"))


def test_detail_and_configured_captures_gather_the_same():
    if not (os.path.exists(DETAIL) and os.path.exists(CONFIGURED)):
        pytest.skip("captures not available")
    results = []
    for capture in (DETAIL, CONFIGURED):
        with open(capture) as handle:
            text = "\n".join(line.rstrip() for line in handle if line.startswith("configure equipment ont "))
        ansible_facts = {"ansible_network_resources": {}}
        Equipment_ontsFacts(module=None).populate_facts(None, ansible_facts, data=text)
        results.append(ansible_facts["ansible_network_resources"]["equipment_onts"])
    assert results[0] == results[1]


class TestIsamEquipmentOntsNodes(TestIsamModule):
    module = isam_equipment_onts

    def setUp(self):
        super(TestIsamEquipmentOntsNodes, self).setUp()
        self.patches = [
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"),
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"),
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"),
        ]
        for item in self.patches:
            item.start()
        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts.Equipment_ontsFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()
        self.get_config.return_value = DETAIL_LINES

    def tearDown(self):
        super(TestIsamEquipmentOntsNodes, self).tearDown()
        for item in self.patches:
            item.stop()
        self.mock_get_config.stop()

    def run_state(self, state, config=None, changed=True):
        args = {"state": state}
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        return self.execute_module(changed=changed)

    def test_gathered_detail_output_does_not_fail(self):
        result = self.run_state("gathered", changed=False)
        assert result["gathered"]["sw_ctrls"][1]["delay_act"] == {"at": "2026-01-01:00:00:00"}
        assert result["gathered"]["loops"][0]["ont_idx"] == "1/1/2/1/2"

    def test_rendered_new_fields(self):
        result = self.run_state("rendered", {
            "sw_ctrls": [{"sw_ctrl_id": 3, "hw_version": "3FE4*", "pland_cfgfile1": "C1", "dnload_cfgfile2": "C2",
                          "delay_act": {"at": "2026-01-01:00:00:00"}}],
            "interfaces": [{"ont_idx": "1/1/2/1/9", "admin_state": "up", "tc_layer": {"olt_pm_collect": "enable", "ont_pm_collect": "enable"}}],
            "loops": [{"ont_idx": "1/1/2/1/9", "loop_detect": "enable", "loop_portautoshut": "disable"}],
            "pm_collects": [{"ont_idx": "1/1/2/1/9", "xg_pm_collect": "enable"}],
        }, changed=False)
        assert result["rendered"] == [
            "configure equipment ont interface 1/1/2/1/9 admin-state up",
            "configure equipment ont interface 1/1/2/1/9 tc-layer olt-pm-collect enable ont-pm-collect enable",
            "configure equipment ont sw-ctrl 3 hw-version 3FE4* pland-cfgfile1 C1 dnload-cfgfile2 C2",
            "configure equipment ont sw-ctrl 3 delay-act at 2026-01-01:00:00:00",
            "configure equipment ont loop 1/1/2/1/9 loop-detect enable loop-portautoshut disable",
            "configure equipment ont pm-collect 1/1/2/1/9 xg-pm-collect enable",
        ]

    def test_merged_is_idempotent_and_default_values_match_unset(self):
        self.run_state("merged", {
            "loops": [{"ont_idx": "1/1/2/1/2", "loop_detect": "enable"},
                      {"ont_idx": "1/1/2/1/1", "loop_detect": "no-control", "loop_portautoshut": "enable"}],
            "pm_collects": [{"ont_idx": "1/1/2/1/1", "xg_pm_collect": "disable"}],
            "sw_ctrls": [{"sw_ctrl_id": 1, "pland_cfgfile2": "CFG2"}, {"sw_ctrl_id": 2, "delay_act": {"at": "2026-01-01:00:00:00"}}],
        }, changed=False)

    def test_merged_changes(self):
        result = self.run_state("merged", {
            "loops": [{"ont_idx": "1/1/2/1/1", "loop_detect": "disable"}],
            "sw_ctrls": [{"sw_ctrl_id": 1, "delay_act": {"at": "2027-01-01:00:00:00"}}],
            "interfaces": [{"ont_idx": "1/1/2/1/1", "xg_tc_layer": {"ont_pm_collect": "enable"}}],
        })
        assert result["commands"] == [
            "configure equipment ont interface 1/1/2/1/1 xg-tc-layer ont-pm-collect enable",
            "configure equipment ont sw-ctrl 1 delay-act at 2027-01-01:00:00:00",
            "configure equipment ont loop 1/1/2/1/1 loop-detect disable",
        ]

    def test_replaced_resets_unlisted_fields(self):
        result = self.run_state("replaced", {
            "loops": [{"ont_idx": "1/1/2/1/2", "loop_detect": "enable"}],
            "sw_ctrls": [{"sw_ctrl_id": 2, "hw_version": "G2110BV2*"}],
        })
        assert result["commands"] == [
            "configure equipment ont sw-ctrl 2 delay-act no at",
            "configure equipment ont loop 1/1/2/1/2 no loop-portautoshut",
        ]

    def test_deleted_resets_named_loop_and_pm_collect(self):
        result = self.run_state("deleted", {
            "loops": [{"ont_idx": "1/1/2/1/2"}],
            "pm_collects": [{"ont_idx": "1/1/2/1/2"}],
        })
        assert result["commands"] == [
            "configure equipment ont loop 1/1/2/1/2 no loop-detect no loop-portautoshut",
            "configure equipment ont pm-collect 1/1/2/1/2 no xg-pm-collect",
        ]

    def test_deleted_without_config_removes_all_in_dependency_order(self):
        self.get_config.return_value = "\n".join([
            "configure equipment ont interface 1/1/2/1/2 admin-state up",
            "configure equipment ont slot 1/1/2/1/2/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0",
            "configure equipment ont sw-ctrl 1 hw-version HW1",
            "configure equipment ont loop 1/1/2/1/2 loop-detect enable",
            "configure equipment ont pm-collect 1/1/2/1/2 xg-pm-collect enable",
        ])
        for config in (None, {}, {"interfaces": [], "slots": []}):
            with self.subTest(config=config):
                result = self.run_state("deleted", config)
                assert result["commands"] == [
                    "configure equipment ont interface 1/1/2/1/2 admin-state down",
                    "configure equipment ont no slot 1/1/2/1/2/1",
                    "configure equipment ont no interface 1/1/2/1/2",
                    "configure equipment ont no sw-ctrl 1",
                ]

    def test_deleted_without_config_is_idempotent_on_empty_device(self):
        self.get_config.return_value = "# empty configuration"
        assert self.run_state("deleted", changed=False)["commands"] == []

    def test_deleting_the_ont_does_not_reset_its_loop_afterwards(self):
        self.get_config.return_value = "\n".join([
            "configure equipment ont interface 1/1/2/1/2 admin-state up",
            "configure equipment ont loop 1/1/2/1/2 loop-detect enable",
            "configure equipment ont pm-collect 1/1/2/1/2 xg-pm-collect enable",
        ])
        result = self.run_state("deleted", {
            "interfaces": [{"ont_idx": "1/1/2/1/2"}],
            "loops": [{"ont_idx": "1/1/2/1/2"}],
            "pm_collects": [{"ont_idx": "1/1/2/1/2"}],
        })
        assert result["commands"] == [
            "configure equipment ont interface 1/1/2/1/2 admin-state down",
            "configure equipment ont no interface 1/1/2/1/2",
        ]

    def test_overridden_resets_other_onts(self):
        result = self.run_state("overridden", {
            "interfaces": [{"ont_idx": "1/1/2/1/1", "sw_ver_pland": "auto", "sernum": "GNXS:00000001",
                            "log_auth_pwd": "plain:******", "admin_state": "up", "xg_tc_layer": {"olt_pm_collect": "enable"}}],
            "slots": [{"ont_slot_idx": "1/1/2/1/1/1", "planned_card_type": "ethernet", "plndnumdataports": 1, "plndnumvoiceports": 0}],
            "sw_ctrls": [{"sw_ctrl_id": 1, "hw_version": "3FE47211AB*", "ont_variant": "DO", "plnd_sw_version": "3FE45655AOCK85",
                          "pland_cfgfile2": "CFG2"},
                         {"sw_ctrl_id": 2, "hw_version": "G2110BV2*", "delay_act": {"at": "2026-01-01:00:00:00"}}],
            "loops": [],
        })
        assert result["commands"] == [
            "configure equipment ont loop 1/1/2/1/2 no loop-detect no loop-portautoshut",
            "configure equipment ont pm-collect 1/1/2/1/2 no xg-pm-collect",
        ]
