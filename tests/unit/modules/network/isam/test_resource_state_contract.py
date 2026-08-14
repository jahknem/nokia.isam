import importlib
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.tests.unit.modules.utils import (
    AnsibleExitJson,
)
from ansible_collections.nokia.isam.tests.unit.modules.network.isam.isam_module import (
    set_module_args,
)


RESOURCE_MODULES = (
    "isam_alarm",
    "isam_ani_onts",
    "isam_arp_relay",
    "isam_bridges",
    "isam_cfm",
    "isam_channel_pair_pm",
    "isam_dhcp_relay",
    "isam_dhcp_server",
    "isam_dist_service",
    "isam_efm_oam_interface",
    "isam_epon_interfaces",
    "isam_equipment",
    "isam_equipment_onts",
    "isam_equipment_replan",
    "isam_ethernet_line",
    "isam_ethernet_onts",
    "isam_generic_pon",
    "isam_igmp",
    "isam_interface_alarms",
    "isam_interface_cages",
    "isam_interfaces",
    "isam_iphost",
    "isam_ipv6_antispoofing_slot",
    "isam_l2cp",
    "isam_l2cp_session",
    "isam_l2cp_user_port",
    "isam_linetest",
    "isam_link_agg",
    "isam_li_vlan",
    "isam_mcast_control",
    "isam_mcast_general",
    "isam_multicast",
    "isam_ngpon2_channel_groups",
    "isam_ntp_onts",
    "isam_pon_interfaces",
    "isam_pppoe_client_interface",
    "isam_pppoe_client_ppp_profile",
    "isam_pppoel2_statistics",
    "isam_qos_interfaces",
    "isam_qos_maps",
    "isam_qos_profiles",
    "isam_system",
    "isam_traps",
    "isam_vlan_global",
    "isam_vlans",
    "isam_voice_sip",
    "isam_xdsl_boards",
    "isam_xdsl_bonding",
    "isam_xdsl_lines",
    "isam_xdsl_profiles",
    "isam_xstp",
)

CANONICAL_STATES = {
    "merged",
    "replaced",
    "overridden",
    "deleted",
    "gathered",
    "rendered",
    "parsed",
}


def _sample_value(spec, required_only=False):
    value_type = spec.get("type")
    if value_type == "dict":
        options = spec.get("options", {})
        selected = (
            set(options)
            if not required_only
            else {key for key, option in options.items() if option.get("required")}
        )
        if not selected and options:
            selected.add(next(iter(options)))
        return {
            key: _sample_value(option, required_only)
            for key, option in options.items()
            if key in selected
        }
    if value_type == "list":
        if spec.get("options"):
            return [_sample_value({"type": "dict", "options": spec["options"]}, False)]
        element = spec.get("elements")
        if isinstance(element, dict):
            return [_sample_value(element, required_only)]
        return [{}] if element == "dict" else ["fixture"]
    if spec.get("choices"):
        return spec["choices"][0]
    if value_type == "bool":
        return True
    if value_type == "int":
        return 1
    return "fixture"


def _exit_json(*args, **kwargs):
    raise AnsibleExitJson(kwargs)


def _fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleExitJson(kwargs)


class _EmptyConnection:
    def get(self, *args, **kwargs):
        return ""


def _empty_connection(*args, **kwargs):
    return _EmptyConnection()


@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_every_resource_accepts_noise_only_parsed_input(module_name, monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", _exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", _fail_json)
    module = importlib.import_module(
        "ansible_collections.nokia.isam.plugins.modules." + module_name
    )
    set_module_args({"state": "parsed", "running_config": "! fixture noise"}, True)

    with pytest.raises(AnsibleExitJson) as raised:
        module.main()

    assert raised.value.args[0].get("failed") is not True


@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_every_resource_exposes_all_canonical_states(module_name):
    module = importlib.import_module(
        "ansible_collections.nokia.isam.plugins.modules." + module_name
    )
    args_classes = [
        value
        for name, value in vars(module).items()
        if name.endswith("Args") and hasattr(value, "argument_spec")
    ]
    assert len(args_classes) == 1
    choices = set(args_classes[0].argument_spec["state"]["choices"])
    assert choices == CANONICAL_STATES


@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_every_resource_handles_empty_deleted_state(module_name, monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", _exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", _fail_json)
    module = importlib.import_module(
        "ansible_collections.nokia.isam.plugins.modules." + module_name
    )
    monkeypatch.setattr(
        "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        _empty_connection,
    )
    for loaded in tuple(sys.modules.values()):
        if loaded is not None and hasattr(loaded, "get_resource_connection"):
            monkeypatch.setattr(loaded, "get_resource_connection", _empty_connection)
    set_module_args({"state": "deleted", "_ansible_check_mode": True}, True)

    with pytest.raises(AnsibleExitJson) as raised:
        module.main()

    assert raised.value.args[0].get("failed") is not True


@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_every_resource_renders_a_minimal_configuration(module_name, monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", _exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", _fail_json)
    module = importlib.import_module(
        "ansible_collections.nokia.isam.plugins.modules." + module_name
    )
    args_classes = [
        value
        for name, value in vars(module).items()
        if name.endswith("Args") and hasattr(value, "argument_spec")
    ]
    config_spec = args_classes[0].argument_spec["config"]
    config = _sample_value(config_spec, required_only=True)
    if module_name == "isam_pon_interfaces":
        config[0]["name"] = "1/1/1/1"
        config[0].update(
            pon_tag="0",
            pon_id="0",
            ponid_identifier="00000000000000",
            sig_degrade_th=9,
            sig_fail_th=5,
            diff_reach=20,
            closest_ont=0,
            ponid_interval=0,
            max_ranging_onts=128,
            tconts_per_frame=64,
        )
    elif module_name == "isam_cfm":
        config = {"domains": [{"domain_index": 1, "name": "fixture", "level": 0}]}
    elif module_name == "isam_qos_maps":
        config = {"tc_map_dot1p": [{"dot1p": 1, "tc": 1}]}
    set_module_args({"state": "rendered", "config": config}, True)

    with pytest.raises(AnsibleExitJson) as raised:
        module.main()

    result = raised.value.args[0]
    assert result.get("failed") is not True
    assert "rendered" in result


@pytest.mark.parametrize("state", ("merged", "replaced", "overridden"))
@pytest.mark.parametrize("module_name", RESOURCE_MODULES)
def test_every_resource_handles_mutating_state_in_check_mode(module_name, state, monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", _exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", _fail_json)
    module = importlib.import_module(
        "ansible_collections.nokia.isam.plugins.modules." + module_name
    )
    monkeypatch.setattr(
        "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        _empty_connection,
    )
    for loaded in tuple(sys.modules.values()):
        if loaded is not None and hasattr(loaded, "get_resource_connection"):
            monkeypatch.setattr(loaded, "get_resource_connection", _empty_connection)
    args_classes = [
        value
        for name, value in vars(module).items()
        if name.endswith("Args") and hasattr(value, "argument_spec")
    ]
    config = _sample_value(args_classes[0].argument_spec["config"], required_only=True)
    if module_name == "isam_pon_interfaces":
        config[0]["name"] = "1/1/1/1"
        config[0].update(
            pon_tag="0",
            pon_id="0",
            ponid_identifier="00000000000000",
            sig_degrade_th=9,
            sig_fail_th=5,
            diff_reach=20,
            closest_ont=0,
            ponid_interval=0,
            max_ranging_onts=128,
            tconts_per_frame=64,
        )
    elif module_name == "isam_cfm":
        config = {"domains": [{"domain_index": 1, "name": "fixture", "level": 0}]}
    elif module_name == "isam_qos_maps":
        config = {"tc_map_dot1p": [{"dot1p": 1, "tc": 1}]}
    set_module_args(
        {"state": state, "config": config, "_ansible_check_mode": True},
        True,
    )

    with pytest.raises(AnsibleExitJson) as raised:
        module.main()

    assert raised.value.args[0].get("failed") is not True
