"""isam_l2uni_onts: configure l2uni ont performance-monitor (+ pm-collect-ext) / tc-layer-threshold."""
import pathlib
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_l2uni_onts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2uni_onts import (
    L2uni_ontsTemplate,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures


ignore_provider_arg = True
PREFIXES = ("configure l2uni ont performance-monitor ", "configure l2uni ont tc-layer-threshold ")
UNI = "1/1/2/1/1/1/1"
UNI2 = "1/1/2/1/100/1/1"

DEFAULTS = dedent("""
    configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit
    configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits no vlan-id
    configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 no dropped-frames-up no dropped-frames-dn
""")

CONFIGURED = dedent("""
    configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect tca-enable pm-collect-64bit pm-enable
    configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext pm-collect enable p-bits 3 vlan-id 100
    configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 dropped-frames-up 1000 no dropped-frames-dn
    configure l2uni ont performance-monitor 1/1/2/1/100/1/1 pm-collect pm-enable no pm-collect-64bit
    configure l2uni ont tc-layer-threshold 1/1/2/1/100/1/1 no dropped-frames-up dropped-frames-dn 5
""")

FULL = {
    "performance_monitor": [
        {"uni_idx": UNI, "pm_collect": "tca-enable", "pm_collect_64bit": "pm-enable",
         "pm_collect_ext": {"pm_collect": "enable", "p_bits": 3, "vlan_id": 100}},
        {"uni_idx": UNI2, "pm_collect": "pm-enable"},
    ],
    "tc_layer_threshold": [
        {"uni_idx": UNI, "dropped_frames_up": 1000},
        {"uni_idx": UNI2, "dropped_frames_dn": 5},
    ],
}


def _by_uni(entries):
    return dict((e["uni_idx"], e) for e in entries)


def test_template_parses_packed_values_and_drops_defaults():
    parser = L2uni_ontsTemplate(lines=CONFIGURED.splitlines() + [
        "configure l2uni ont tc-layer-threshold 1/1/9/1/1/1/1 dropped-frames-up disabled dropped-frames-dn 4294967295",
        "configure l2uni ont performance-monitor 1/1/9/1/1/1/1 pm-collect-ext p-bits 0xFF vlan-id 0 pm-collect disable",
    ])
    got = parser.parse()
    assert not parser.unknown
    pm = got["performance_monitor"]
    assert pm[UNI] == FULL["performance_monitor"][0]
    assert pm[UNI2] == FULL["performance_monitor"][1]
    assert pm["1/1/9/1/1/1/1"] == {"uni_idx": "1/1/9/1/1/1/1", "pm_collect_ext": {}}
    assert got["tc_layer_threshold"]["1/1/9/1/1/1/1"] == {"uni_idx": "1/1/9/1/1/1/1"}
    assert got["tc_layer_threshold"][UNI2] == {"uni_idx": UNI2, "dropped_frames_dn": 5}


def test_template_parses_detail_defaults_as_identity_only():
    parser = L2uni_ontsTemplate(lines=DEFAULTS.splitlines())
    got = parser.parse()
    assert not parser.unknown
    assert got["performance_monitor"][UNI] == {"uni_idx": UNI, "pm_collect_ext": {}}
    assert got["tc_layer_threshold"][UNI] == {"uni_idx": UNI}


def test_template_reports_unknown_tokens():
    parser = L2uni_ontsTemplate(lines=["configure l2uni ont performance-monitor 1/1/1/1/1/1/1 bogus 3 pm-collect pm-enable"])
    got = parser.parse()
    assert got["performance_monitor"]["1/1/1/1/1/1/1"]["pm_collect"] == "pm-enable"
    assert [token for dummy, token in parser.unknown] == ["bogus", "3"]


def test_every_capture_line_parses():
    lines = [line.strip() for line in lab_captures.detail().splitlines() if line.startswith(PREFIXES)]
    assert len(lines) == 146 + 73
    for line in lines:
        parser = L2uni_ontsTemplate(lines=[line])
        got = parser.parse()
        assert not parser.unknown, (line, parser.unknown)
        section = "performance_monitor" if "performance-monitor" in line else "tc_layer_threshold"
        uni = line.split()[4]
        assert uni in got[section], line
        if " pm-collect-ext" in line:
            assert "pm_collect_ext" in got[section][uni], line
    parsed = L2uni_ontsTemplate(lines=lines).parse()
    assert len(parsed["performance_monitor"]) == 73
    assert len(parsed["tc_layer_threshold"]) == 73


class FakeConn(object):
    def __init__(self, text):
        self.text, self.commands = text, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        return self.text


class TestIsamL2uniOntsModule(TestIsamModule):
    module = isam_l2uni_onts

    def setUp(self):
        super(TestIsamL2uniOntsModule, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamL2uniOntsModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_facts.stop()

    def _device(self, text):
        conn = FakeConn(text)
        self.get_resource_connection_facts.return_value = conn
        return conn

    def test_parsed(self):
        set_module_args(dict(running_config=CONFIGURED, state="parsed"), ignore_provider_arg)
        parsed = self.execute_module(changed=False)["parsed"]
        assert _by_uni(parsed["performance_monitor"]) == _by_uni(FULL["performance_monitor"])
        assert _by_uni(parsed["tc_layer_threshold"]) == _by_uni(FULL["tc_layer_threshold"])

    def test_parsed_indented_output(self):
        running = dedent("""
            configure l2uni
              ont
                performance-monitor 1/1/2/1/1/1/1
                  pm-collect pm-enable
                  pm-collect-ext
                    vlan-id 7
                  exit
                exit
              exit
            exit
        """)
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        parsed = self.execute_module(changed=False)["parsed"]
        assert parsed["performance_monitor"] == [{"uni_idx": UNI, "pm_collect": "pm-enable", "pm_collect_ext": {"vlan_id": 7}}]

    def test_rendered_packs_one_command_per_scope(self):
        set_module_args(dict(state="rendered", config=FULL), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        assert rendered == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect tca-enable pm-collect-64bit pm-enable",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext pm-collect enable p-bits 3 vlan-id 100",
            "configure l2uni ont performance-monitor 1/1/2/1/100/1/1 pm-collect pm-enable",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 dropped-frames-up 1000",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/100/1/1 dropped-frames-dn 5",
        ]

    def test_rendered_default_values_render_as_reset(self):
        set_module_args(dict(state="rendered", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect": "none", "pm_collect_ext": {"p_bits": 255}}],
            "tc_layer_threshold": [{"uni_idx": UNI, "dropped_frames_up": 4294967295}],
        }), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        assert rendered == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no p-bits",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 no dropped-frames-up",
        ]

    def test_render_parse_round_trip(self):
        set_module_args(dict(state="rendered", config=FULL), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        again = L2uni_ontsTemplate(lines=rendered).parse()
        assert _by_uni(again["performance_monitor"].values()) == _by_uni(FULL["performance_monitor"])
        assert _by_uni(again["tc_layer_threshold"].values()) == _by_uni(FULL["tc_layer_threshold"])

    def test_merged_idempotent(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="merged", config=FULL), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_merged_default_value_on_default_device_is_idempotent(self):
        self._device(DEFAULTS)
        set_module_args(dict(state="merged", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect": "none", "pm_collect_ext": {"vlan_id": 0}}],
            "tc_layer_threshold": [{"uni_idx": UNI, "dropped_frames_dn": 4294967295}],
        }), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_merged_sends_only_changed_fields(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="merged", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect": "pm-enable", "pm_collect_64bit": "pm-enable",
                                     "pm_collect_ext": {"vlan_id": 200}}],
            "tc_layer_threshold": [{"uni_idx": UNI2, "dropped_frames_up": 7}],
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect pm-enable",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext vlan-id 200",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/100/1/1 dropped-frames-up 7",
        ]

    def test_merged_default_value_resets(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="merged", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect": "none"}],
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == ["configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect"]

    def test_replaced_resets_unspecified_fields_of_named_unis(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="replaced", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect": "tca-enable"}],
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect-64bit",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits no vlan-id",
        ]

    def test_overridden_resets_other_unis_and_missing_lists(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="overridden", config={
            "performance_monitor": [{"uni_idx": UNI2, "pm_collect": "pm-enable"}],
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits no vlan-id",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 no dropped-frames-up",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/100/1/1 no dropped-frames-dn",
        ]

    def test_deleted_identity_only_resets_the_whole_entry(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted", config={"performance_monitor": [{"uni_idx": UNI}]}), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits no vlan-id",
        ]

    def test_deleted_named_fields_only(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect_ext": {"vlan_id": 100}}],
            "tc_layer_threshold": [{"uni_idx": UNI2, "dropped_frames_dn": 5}],
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no vlan-id",
            "configure l2uni ont tc-layer-threshold 1/1/2/1/100/1/1 no dropped-frames-dn",
        ]

    def test_deleted_empty_sub_node_counts_as_identity_only(self):
        """An empty pm_collect_ext names nothing (empties are dropped): the whole entry is reset."""
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect_ext": {}}],
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit",
            "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no p-bits no vlan-id",
        ]

    def test_deleted_without_config_resets_everything(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted"), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert len(result["commands"]) == 5
        assert "configure l2uni ont tc-layer-threshold 1/1/2/1/100/1/1 no dropped-frames-dn" in result["commands"]

    def test_deleted_on_defaults_is_idempotent(self):
        self._device(DEFAULTS)
        set_module_args(dict(state="deleted"), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_out_of_range_value_fails(self):
        set_module_args(dict(state="rendered", config={
            "performance_monitor": [{"uni_idx": UNI, "pm_collect_ext": {"p_bits": 9}}],
        }), ignore_provider_arg)
        result = self.execute_module(failed=True)
        assert "p_bits=9" in result["msg"]

    def test_gathered_with_config_reads_only_named_unis(self):
        conn = self._device("configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect pm-enable\n")
        set_module_args(dict(state="gathered", config={"performance_monitor": [{"uni_idx": UNI}]}), ignore_provider_arg)
        result = self.execute_module(changed=False)
        assert conn.commands == ["info configure l2uni ont performance-monitor 1/1/2/1/1/1/1 flat"]
        assert result["gathered"]["performance_monitor"] == [{"uni_idx": UNI, "pm_collect": "pm-enable"}]

    def test_gathered_without_config_reads_whole_resource(self):
        conn = self._device(CONFIGURED)
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        assert conn.commands == ["info configure l2uni flat"]
        assert len(result["gathered"]["performance_monitor"]) == 2
