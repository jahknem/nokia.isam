"""Targeted gathering for every resource listed in TARGETED_GATHER.

``state: gathered`` with ``config`` reads only the named instances; without ``config``
the whole resource, as before. Real modules and parsers against synthetic device replies.
"""
import importlib
import re
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER
from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson
from .isam_module import set_module_args

ONT, SIBLING = "1/1/5/1/3", "1/1/5/1/30"
UNI = ONT + "/1/1"

# resource -> (module, device lines for ONT (SIBLING is derived), config selecting ONT, identity read)
CASES = {
    "ani_onts": ("isam_ani_onts", ["configure ani ont tca-thresh %s lower-optical-th -28" % ONT],
                 [{"ont_idx": ONT}], ONT),
    "bridges": ("isam_bridges", ["configure bridge port %s max-unicast-mac 5 pvid 99" % UNI, "configure bridge port %s vlan-id 99" % UNI],
                {"port": [{"port": UNI}]}, UNI),
    "efm_oam_interface": ("isam_efm_oam_interface", ["configure efm-oam interface %s admin-up keep-alive-intvl 10" % UNI],
                          [{"name": UNI}], UNI),
    "equipment_onts": ("isam_equipment_onts", ["configure equipment ont interface %s sw-ver-pland auto admin-state up" % ONT,
                                               "configure equipment ont slot %s/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0" % ONT],
                       {"interfaces": [{"ont_idx": ONT}], "slots": [{"ont_slot_idx": ONT + "/1"}]}, ONT),
    "ethernet_onts": ("isam_ethernet_onts", ["configure ethernet ont %s auto-detect auto admin-state up" % UNI], [{"uni_idx": UNI}], UNI),
    "interfaces": ("isam_interfaces", ["configure interface port uni:%s admin-up" % UNI], [{"name": "uni:" + UNI}], "uni:" + UNI),
    "isam_arp_relay": ("isam_arp_relay", ["configure arp-relay statistics vlan-port:%s:10" % UNI], [{"name": "vlan-port:%s:10" % UNI}], UNI),
    "isam_dhcp_relay": ("isam_dhcp_relay", ["configure dhcp-relay port-stats vlan-port:%s:10" % UNI], [{"name": "vlan-port:%s:10" % UNI}], UNI),
    "ntp_onts": ("isam_ntp_onts", ["configure ntp ont %s client-state on" % ONT], [{"ont_id": ONT}], ONT),
    "pon_interfaces": ("isam_pon_interfaces", ["configure pon interface 1/1/5/3 admin-state up"], [{"name": "1/1/5/3"}], "1/1/5/3"),
    "qos_interfaces": ("isam_qos_interfaces", ["configure qos interface %s scheduler-node name:A" % UNI], [{"name": UNI}], UNI),
}


def device_lines(resource):
    lines = CASES[resource][1]
    sibling = [line.replace(ONT, SIBLING).replace("1/1/5/3", "1/1/5/30") for line in lines]
    return lines + sibling


class Device:
    """Answers 'info configure <path> [<id>] [detail] flat [detail]' from flat lines."""

    def __init__(self, lines, fail=False):
        self.lines, self.commands, self.fail = lines, [], fail

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        if self.fail:
            raise Exception("Error : connection to the device was lost")
        match = re.match(r"^info configure (.*?)(?:\s+detail)?(?:\s+flat)(?:\s+detail)?$", command)
        assert match, command
        prefix = "configure " + match.group(1)
        hits = [line for line in self.lines if line == prefix or line.startswith(prefix + " ")]
        if not hits and re.search(r"\d", match.group(1).split()[-1]):
            raise Exception("Error : instance does not exist")
        return "\n".join(hits) + "\n"

    def edit_config(self, *args, **kwargs):
        raise AssertionError("gathered must not change anything")


def gathered(monkeypatch, resource, config, device):
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules." + CASES[resource][0])
    importlib.import_module("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts")

    def exit_json(self, **result):
        raise AnsibleExitJson(result)

    def fail_json(self, **result):
        raise AnsibleExitJson(dict(result, failed=True))

    with monkeypatch.context() as patch:
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: device)
        patch.setattr(basic.AnsibleModule, "exit_json", exit_json)
        patch.setattr(basic.AnsibleModule, "fail_json", fail_json)
        args = {"state": "gathered"}
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        with pytest.raises(AnsibleExitJson) as result:
            module.main()
        return result.value.args[0]


def instances(data):
    if isinstance(data, dict):
        return [item for value in data.values() if isinstance(value, list) for item in value]
    return data or []


def test_every_targetable_resource_has_a_case():
    assert set(CASES) == set(TARGETED_GATHER)


@pytest.mark.parametrize("resource", sorted(CASES))
def test_gathered_with_config_reads_only_the_named_instances(monkeypatch, resource):
    device = Device(device_lines(resource))
    result = gathered(monkeypatch, resource, CASES[resource][2], device)
    assert not result.get("failed"), result
    assert device.commands and all(CASES[resource][3] in command for command in device.commands), device.commands
    found = instances(result["gathered"])
    assert found, result
    text = repr(found)
    assert SIBLING not in text and "1/1/5/30" not in text


@pytest.mark.parametrize("resource", sorted(CASES))
def test_absent_instances_are_simply_not_gathered(monkeypatch, resource):
    device = Device([])
    result = gathered(monkeypatch, resource, CASES[resource][2], device)
    assert not result.get("failed"), result
    assert instances(result["gathered"]) == []


@pytest.mark.parametrize("resource", sorted(CASES))
def test_other_device_errors_fail(monkeypatch, resource):
    result = gathered(monkeypatch, resource, CASES[resource][2], Device([], fail=True))
    assert result.get("failed")


@pytest.mark.parametrize("resource", sorted(CASES))
def test_without_config_the_whole_resource_is_read(monkeypatch, resource):
    device = Device(device_lines(resource))
    result = gathered(monkeypatch, resource, None, device)
    assert not result.get("failed"), result
    assert not any(CASES[resource][3] in command for command in device.commands), device.commands
    text = repr(instances(result["gathered"]))
    assert (SIBLING in text or "1/1/5/30" in text) and (ONT in text or "1/1/5/3'" in text)
