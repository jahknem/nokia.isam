"""isam_uni_onts: configure uni ont tc-layer <uni> (TC-layer PM collection per UNI)."""
import pathlib
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_uni_onts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.uni_onts import (
    Uni_ontsTemplate,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures


ignore_provider_arg = True
PREFIX = "configure uni ont tc-layer "
UNI = "1/1/2/1/1/1/1"
UNI2 = "1/1/2/1/100/1/1"

CONFIGURED = dedent("""
    configure uni ont tc-layer 1/1/2/1/1/1/1 pm-collect enable
    configure uni ont tc-layer 1/1/2/1/100/1/1 no pm-collect
""")


def test_template_parses_values_and_defaults():
    parser = Uni_ontsTemplate(lines=CONFIGURED.splitlines() + ["configure uni ont tc-layer 1/1/9/1/1/1/1 pm-collect disable"])
    got = parser.parse()["config"]
    assert not parser.unknown
    assert got[UNI] == {"uni_idx": UNI, "pm_collect": "enable"}
    assert got[UNI2] == {"uni_idx": UNI2}
    assert got["1/1/9/1/1/1/1"] == {"uni_idx": "1/1/9/1/1/1/1"}


def test_template_ignores_other_families():
    parser = Uni_ontsTemplate(lines=["configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 no dropped-frames-up"])
    assert parser.parse() == {}


def test_every_capture_line_parses():
    lines = [line.strip() for line in lab_captures.detail().splitlines() if line.startswith(PREFIX)]
    assert len(lines) == 73
    for line in lines:
        parser = Uni_ontsTemplate(lines=[line])
        got = parser.parse()
        assert not parser.unknown, (line, parser.unknown)
        assert line.split()[4] in got["config"], line
    assert len(Uni_ontsTemplate(lines=lines).parse()["config"]) == 73


class FakeConn(object):
    def __init__(self, text):
        self.text, self.commands = text, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        return self.text


class TestIsamUniOntsModule(TestIsamModule):
    module = isam_uni_onts

    def setUp(self):
        super(TestIsamUniOntsModule, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamUniOntsModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_facts.stop()

    def _device(self, text):
        conn = FakeConn(text)
        self.get_resource_connection_facts.return_value = conn
        return conn

    def test_parsed(self):
        set_module_args(dict(running_config=CONFIGURED, state="parsed"), ignore_provider_arg)
        parsed = self.execute_module(changed=False)["parsed"]
        assert sorted(parsed, key=lambda e: e["uni_idx"]) == [{"uni_idx": UNI, "pm_collect": "enable"}, {"uni_idx": UNI2}]

    def test_rendered_and_round_trip(self):
        config = [{"uni_idx": UNI, "pm_collect": "enable"}, {"uni_idx": UNI2, "pm_collect": "disable"}]
        set_module_args(dict(state="rendered", config=config), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        assert rendered == [
            "configure uni ont tc-layer 1/1/2/1/1/1/1 pm-collect enable",
            "configure uni ont tc-layer 1/1/2/1/100/1/1 no pm-collect",
        ]
        again = Uni_ontsTemplate(lines=rendered).parse()["config"]
        assert again == {UNI: {"uni_idx": UNI, "pm_collect": "enable"}, UNI2: {"uni_idx": UNI2}}

    def test_merged_idempotent(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="merged", config=[
            {"uni_idx": UNI, "pm_collect": "enable"}, {"uni_idx": UNI2, "pm_collect": "disable"},
        ]), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_merged_changes(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="merged", config=[
            {"uni_idx": UNI, "pm_collect": "disable"}, {"uni_idx": UNI2, "pm_collect": "enable"},
        ]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect",
            "configure uni ont tc-layer 1/1/2/1/100/1/1 pm-collect enable",
        ]

    def test_replaced_resets_unspecified(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="replaced", config=[{"uni_idx": UNI}]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == ["configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect"]

    def test_overridden_resets_other_unis(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="overridden", config=[{"uni_idx": UNI2, "pm_collect": "enable"}]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == [
            "configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect",
            "configure uni ont tc-layer 1/1/2/1/100/1/1 pm-collect enable",
        ]

    def test_deleted_named(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted", config=[{"uni_idx": UNI}]), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == ["configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect"]

    def test_deleted_other_uni_is_noop(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted", config=[{"uni_idx": UNI2}]), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_deleted_without_config(self):
        self._device(CONFIGURED)
        set_module_args(dict(state="deleted"), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert result["commands"] == ["configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect"]

    def test_gathered_targeted(self):
        conn = self._device("configure uni ont tc-layer 1/1/2/1/1/1/1 pm-collect enable\n")
        set_module_args(dict(state="gathered", config=[{"uni_idx": UNI}]), ignore_provider_arg)
        result = self.execute_module(changed=False)
        assert conn.commands == ["info configure uni ont tc-layer 1/1/2/1/1/1/1 flat"]
        assert result["gathered"] == [{"uni_idx": UNI, "pm_collect": "enable"}]

    def test_gathered_whole(self):
        conn = self._device(CONFIGURED)
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        self.execute_module(changed=False)
        assert conn.commands == ["info configure uni flat"]
