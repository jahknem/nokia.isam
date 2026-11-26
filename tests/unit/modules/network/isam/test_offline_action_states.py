"""Offline action states: running_config supplies the current state, no device is touched.

An action state (deleted/replaced/overridden/merged) given ``running_config`` renders
against that configuration instead of reading the device and never sends commands.
``deleted`` with no ``config`` renders the removal of everything in ``running_config``
(the offline counterpart of ``rendered`` for deletions, used by NOC move/copy/delete
previews). running_config is accepted as canonical resource JSON or as CLI text.
"""
from . import contract_registry as _registry
import json

import pytest

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base import resource_module_base
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts import facts
from ansible_collections.nokia.isam.plugins.modules import (
    isam_ani_onts, isam_arp_relay, isam_bridges, isam_dhcp_relay, isam_efm_oam_interface,
    isam_equipment_onts, isam_ethernet_onts, isam_interfaces, isam_ntp_onts, isam_qos_interfaces,
)

from .isam_module import set_module_args


class Connection:
    def __init__(self):
        self.reads = []
        self.writes = []

    def get(self, command):
        self.reads.append(command)
        raise AssertionError("offline action state must not read the device: %s" % command)

    def edit_config(self, candidate):
        self.writes.append(list(candidate))
        raise AssertionError("offline action state must not write to the device")


def invoke_offline(monkeypatch, capsys, module, running_config, state="deleted", config=None, check_mode=False):
    connection = Connection()
    monkeypatch.setattr(resource_module_base, "get_resource_connection", lambda module: connection)
    monkeypatch.setattr(facts, "get_resource_connection", lambda module: connection)
    args = {"state": state, "running_config": running_config, "_ansible_check_mode": check_mode}
    if config is not None:
        args["config"] = config
    set_module_args(args, True)
    with pytest.raises(SystemExit) as exited:
        module.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code == 0, result
    assert connection.reads == [] and connection.writes == []
    return result


EQUIPMENT = {"interfaces": [{"ont_idx": "1/1/6/1/1", "sernum": "ALCL:F0000001", "sw_ver_pland": "auto",
                             "plnd_var": "DO", "enable_aes": "enable", "admin_state": "up"}],
             "slots": [{"ont_slot_idx": "1/1/6/1/1/1", "planned_card_type": "ethernet",
                        "plndnumdataports": 1, "plndnumvoiceports": 0, "admin_state": "up"}]}


@_registry.requires('isam_equipment_onts')
def test_equipment_onts_delete_renders_removal_offline_from_json(monkeypatch, capsys):
    result = invoke_offline(monkeypatch, capsys, isam_equipment_onts, json.dumps(EQUIPMENT))
    commands = result["commands"]
    assert "configure equipment ont no interface 1/1/6/1/1" in commands
    assert "configure equipment ont no slot 1/1/6/1/1/1" in commands
    assert any(c.endswith("admin-state down") for c in commands)
    assert result["before"] == EQUIPMENT
    assert result["changed"] is False


@_registry.requires('isam_equipment_onts')
def test_equipment_onts_delete_renders_removal_offline_from_cli(monkeypatch, capsys):
    cli = ("configure equipment ont interface 1/1/6/1/1 sernum ALCL:F0000001 sw-ver-pland auto plnd-var DO enable-aes enable\n"
           "configure equipment ont interface 1/1/6/1/1 admin-state up\n"
           "configure equipment ont slot 1/1/6/1/1/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0\n"
           "configure equipment ont slot 1/1/6/1/1/1 admin-state up\n")
    result = invoke_offline(monkeypatch, capsys, isam_equipment_onts, cli)
    assert "configure equipment ont no interface 1/1/6/1/1" in result["commands"]
    assert "configure equipment ont no slot 1/1/6/1/1/1" in result["commands"]


@_registry.requires('isam_bridges')
def test_bridges_delete_renders_removal_offline(monkeypatch, capsys):
    bridges = {"port": [{"port": "1/1/6/1/1/1/1", "max_unicast_mac": 5, "pvid": 99,
                         "vlan_id": [{"id": "10", "tag": "single-tagged", "l2fwder_vlan": "410", "vlan_scope": "local"}, {"id": "99"}]}]}
    result = invoke_offline(monkeypatch, capsys, isam_bridges, json.dumps(bridges))
    assert "configure bridge no port 1/1/6/1/1/1/1" in result["commands"]


@_registry.requires('isam_ethernet_onts')
def test_ethernet_onts_delete_renders_removal_offline(monkeypatch, capsys):
    result = invoke_offline(monkeypatch, capsys, isam_ethernet_onts,
                            json.dumps([{"uni_idx": "1/1/6/1/1/1/1", "cust_info": "Y000001", "admin_state": "up"}]))
    assert any("1/1/6/1/1/1/1" in c for c in result["commands"])
    assert result["commands"]


@_registry.requires('isam_equipment_onts')
def test_offline_delete_of_a_subset_via_running_config(monkeypatch, capsys):
    # Supplying only the subset as running_config (delete-all) removes exactly that subset.
    subset = {"interfaces": [{"ont_idx": "1/1/6/1/1", "sernum": "ALCL:F0000001", "admin_state": "up"}], "slots": []}
    result = invoke_offline(monkeypatch, capsys, isam_equipment_onts, json.dumps(subset))
    assert "configure equipment ont no interface 1/1/6/1/1" in result["commands"]
    assert not any("1/1/6/1/2" in c for c in result["commands"])

_REMAINING = [
    (isam_ntp_onts, "ntp_onts", {"ont_id": "1/1/6/1/1"}),
    (isam_ani_onts, "ani_onts", {"ont_idx": "1/1/6/1/1", "tca_thresh": True}),
    (isam_dhcp_relay, "dhcp_relay", {"name": "vlan-port:1/1/6/1/1/1/1:10", "port_stats": True}),
    (isam_arp_relay, "arp_relay", {"name": "1/1/6/1/1/1/1"}),
    (isam_efm_oam_interface, "efm_oam", {"name": "1/1/6/1/1/1/1", "admin_up": True, "passive_mode": True}),
]
_REMAINING = [e for e in _REMAINING if _registry.module_in_scope(e[0].__name__)]


@pytest.mark.parametrize("module,family,identity", _REMAINING)
def test_remaining_noc_families_delete_offline(monkeypatch, capsys, module, family, identity):
    result = invoke_offline(monkeypatch, capsys, module, json.dumps([identity]))
    assert result["commands"], family
    assert any("1/1/6/1/1" in c for c in result["commands"]), family
    assert result["changed"] is False


@_registry.requires('isam_equipment_onts')
def test_offline_running_config_unknown_field_fails(monkeypatch, capsys):
    # A renamed/unknown field must error, not silently render zero removal commands.
    connection = Connection()
    monkeypatch.setattr(resource_module_base, "get_resource_connection", lambda module: connection)
    monkeypatch.setattr(facts, "get_resource_connection", lambda module: connection)
    bad = {"interfaces": [{"ont_idx": "1/1/6/1/1", "sernum": "ALCL:F0000001", "bogus_field": "x"}], "slots": []}
    set_module_args({"state": "deleted", "running_config": json.dumps(bad), "_ansible_check_mode": False}, True)
    with pytest.raises(SystemExit) as exited:
        isam_equipment_onts.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code != 0
    assert result.get("failed")
    assert "bogus_field" in result.get("msg", "")
    assert connection.reads == [] and connection.writes == []
