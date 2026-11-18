"""state: deleted against devices that actually have configuration.

The state contract only exercised deleted against an empty device, which hid a crash
(PON variants), silent no-ops (an empty_fact_val dict of empty lists is truthy) and a
hard failure on a field without a CLI removal form (interface cages).
"""
import importlib
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson
from . import lab_captures
from .isam_module import set_module_args
from .test_resource_state_contract import RESOURCE_MODULES

PREFIX = "ansible_collections.nokia.isam.plugins.modules."


def run(monkeypatch, module_name, args, text):
    class Conn(object):
        def get(self, *a, **k):
            return text

        def get_config(self, *a, **k):
            return text

    def conn(*a, **k):
        return Conn()

    warnings = []

    def exit_json(self, **kw):
        raise AnsibleExitJson(kw)

    def fail_json(self, **kw):
        kw["failed"] = True
        raise AnsibleExitJson(kw)

    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)
    monkeypatch.setattr(basic.AnsibleModule, "warn", lambda self, msg: warnings.append(msg))
    module = importlib.import_module(PREFIX + module_name)
    for loaded in tuple(sys.modules.values()):
        if loaded is not None and hasattr(loaded, "get_resource_connection"):
            monkeypatch.setattr(loaded, "get_resource_connection", conn)
    set_module_args(dict(args, _ansible_check_mode=True), True)
    with pytest.raises(AnsibleExitJson) as raised:
        module.main()
    result = raised.value.args[0]
    result["_warnings"] = warnings
    return result


@pytest.mark.parametrize("module_name,line,command", [
    ("isam_epon_interfaces", "configure epon interface 1/1/1/1 polling-period 10",
     "configure epon no interface 1/1/1/1"),
    ("isam_channel_pair_pm", "configure channel-pair interface 1/1/5/1 fec-tc-layer pm-collect enable",
     "configure channel-pair no interface 1/1/5/1"),
    ("isam_ngpon2_channel_groups", "configure channel-group id 1 polling-period 10",
     "configure channel-group no id 1"),
])
def test_pon_variants_delete_existing_instances(monkeypatch, module_name, line, command):
    for config in (None, [{"name" if "group" not in module_name else "id": line.split()[3]}]):
        args = {"state": "deleted"}
        if config is not None:
            if "group" in module_name:
                config = [{"id": 1}]
            args["config"] = config
        result = run(monkeypatch, module_name, args, line)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == [command]


@pytest.mark.parametrize("module_name", ["isam_epon_interfaces", "isam_channel_pair_pm", "isam_ngpon2_channel_groups"])
def test_pon_variants_ignore_unrelated_lines(monkeypatch, module_name):
    text = "\n".join([
        "configure alarm log-full-action wrap",
        "configure equipment ont interface 1/1/5/1/3 sw-ver-pland auto",
        "configure system id name x",
    ])
    result = run(monkeypatch, module_name, {"state": "parsed", "running_config": text}, "")
    assert not result.get("failed"), result.get("msg")
    assert not result["parsed"]


def test_xdsl_boards_deleted_without_config_removes_all(monkeypatch):
    text = "\n".join([
        "configure xdsl board 1/1/1 vce-profile 1",
        "configure xdsl board 1/1/3 vce-profile 2",
    ])
    for config in (None, {}, {"boards": [], "vp_boards": []}):
        args = {"state": "deleted"}
        if config is not None:
            args["config"] = config
        result = run(monkeypatch, "isam_xdsl_boards", args, text)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == ["configure xdsl no board 1/1/1", "configure xdsl no board 1/1/3"]
    named = run(monkeypatch, "isam_xdsl_boards", {"state": "deleted", "config": {"boards": [{"board_id": "1/1/3"}]}}, text)
    assert named["commands"] == ["configure xdsl no board 1/1/3"]


def test_mcast_general_deleted_resets_fast_change(monkeypatch):
    text = "configure mcast general fast-change"
    result = run(monkeypatch, "isam_mcast_general", {"state": "deleted"}, text)
    assert not result.get("failed"), result.get("msg")
    assert result["commands"] == ["configure mcast general no fast-change"]
    assert run(monkeypatch, "isam_mcast_general", {"state": "deleted"}, "")["commands"] == []


def test_interface_cages_keep_operational_mode_with_a_warning(monkeypatch):
    text = "configure interface cage lt:1/1/2:cage:1 operational-mode gpon"
    for state in ("deleted", "overridden"):
        args = {"state": state}
        if state == "overridden":
            args["config"] = [{"id": "lt:1/1/2:cage:2"}]
        result = run(monkeypatch, "isam_interface_cages", args, text)
        assert not result.get("failed"), result.get("msg")
        assert not any("operational-mode" in c for c in result.get("commands", []))
        assert any("operational_mode" in w for w in result["_warnings"])


@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_deleted_without_config_never_fails_on_a_real_capture(monkeypatch, module_name):
    """No-ops are allowed (e.g. context selectors, isam_system by design); failures are not."""
    if not lab_captures.CONFIGURED.exists():
        pytest.skip("lab capture not available")
    text = lab_captures.CONFIGURED.read_text(errors="replace")
    result = run(monkeypatch, module_name, {"state": "deleted"}, text)
    assert not result.get("failed"), "%s: deleted failed" % module_name  # no message: may quote config
