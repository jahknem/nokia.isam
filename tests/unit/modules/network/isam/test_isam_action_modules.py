import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ethernet_statistics.ethernet_statistics import (
    Isam_ethernet_statistics,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dhcp_relay_port_stats.dhcp_relay_port_stats import (
    Isam_dhcp_relay_port_stats,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.bridge_learned_mac.bridge_learned_mac import (
    Isam_bridge_learned_mac,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

CONNECTION = "ansible_collections.nokia.isam.plugins.module_utils.network.isam.action_module.get_resource_connection"


class FakeFail(Exception):
    def __init__(self, kwargs):
        self.kwargs = kwargs
        super(FakeFail, self).__init__(kwargs.get("msg", ""))


class FakeModule:
    def __init__(self, config, check_mode=True):
        self.params = {"config": config}
        self.check_mode = check_mode

    def fail_json(self, **kwargs):
        raise FakeFail(kwargs)

    def warn(self, msg):
        pass


class FakeConnection:
    def __init__(self, responses=None):
        self.calls = []
        self._responses = responses or {}

    def edit_config(self, candidate):
        self.calls.append(list(candidate))
        return {"request": list(candidate), "response": self._responses.get(candidate[0], ["ok"])}


# (class, operation flag, identifier option, command template)
PORT_MODULES = [
    (Isam_ethernet_statistics, "clear_stats", "port", "admin ethernet statistics %s clear-stats"),
    (Isam_dhcp_relay_port_stats, "clear_statistics", "port", "admin dhcp-relay port-stats %s clear-statistics"),
]


@pytest.mark.parametrize("cls,flag,ident,template", PORT_MODULES)
def test_operation_is_required(cls, flag, ident, template):
    for entry in ({ident: "1/1/6/1"}, {ident: "1/1/6/1", flag: False}):
        with pytest.raises(FakeFail) as exc:
            cls(FakeModule([entry])).build_commands()
        assert "explicit operation" in exc.value.kwargs["msg"]


@pytest.mark.parametrize("cls,flag,ident,template", PORT_MODULES)
def test_command_format_and_identifier_validation(cls, flag, ident, template):
    for port in ("1/1/6/1", "lt:1/1/6", "lt-link:1/1/6/1", "vlan:1/1/6/1:3990"):
        action = cls(FakeModule([{ident: port, flag: True}]))
        assert action.build_commands() == [template % port]
    with pytest.raises(FakeFail) as exc:
        cls(FakeModule([{ident: "1/1/6/1 reboot", flag: True}])).build_commands()
    assert "Invalid port" in exc.value.kwargs["msg"]


@pytest.mark.parametrize("cls,flag,ident,template", PORT_MODULES)
def test_check_mode_never_connects(cls, flag, ident, template):
    with patch(CONNECTION) as connect:
        result = cls(FakeModule([{ident: "1/1/6/1", flag: True}], check_mode=True)).execute_module()
    connect.assert_not_called()
    assert result["changed"] is True
    assert result["commands"] == [template % "1/1/6/1"]
    assert "response" not in result


@pytest.mark.parametrize("cls,flag,ident,template", PORT_MODULES)
def test_execution_one_transaction_per_command(cls, flag, ident, template):
    connection = FakeConnection()
    with patch(CONNECTION, return_value=connection):
        result = cls(FakeModule([{ident: "1/1/6/1", flag: True}, {ident: "1/1/6/2", flag: True}],
                                check_mode=False)).execute_module()
    assert connection.calls == [[template % "1/1/6/1"], [template % "1/1/6/2"]]
    assert result["response"] == ["ok", "ok"]


# --- bridge learned MAC (identifier + MAC + operation) ---

def _mac_entry(vlan_port="vlan-port:1/1/6/1:3990", mac="aa:bb:cc:dd:ee:ff", delete=True):
    return {"vlan_port": vlan_port, "mac_address": mac, "delete": delete}


def test_bridge_command_format():
    action = Isam_bridge_learned_mac(FakeModule([_mac_entry()]))
    assert action.build_commands() == [
        "admin bridge learned-unicast-mac vlan-port:1/1/6/1:3990 unicast-mac-address aa:bb:cc:dd:ee:ff delete"
    ]


def test_bridge_operation_is_required():
    with pytest.raises(FakeFail) as exc:
        Isam_bridge_learned_mac(FakeModule([_mac_entry(delete=False)])).build_commands()
    assert "explicit operation" in exc.value.kwargs["msg"]


@pytest.mark.parametrize("mac", ["aa:bb:cc:dd:ee", "aa:bb:cc:dd:ee:ff:00", "zz:bb:cc:dd:ee:ff",
                                 "aabb.ccdd.eeff", "aa bb cc dd ee ff", "", "aa:bb:cc:dd:ee:gg"])
def test_bridge_invalid_mac_rejected(mac):
    with pytest.raises(FakeFail) as exc:
        Isam_bridge_learned_mac(FakeModule([_mac_entry(mac=mac)])).build_commands()
    assert "Invalid mac_address" in exc.value.kwargs["msg"]


@pytest.mark.parametrize("mac", ["aa:bb:cc:dd:ee:ff", "00:11:22:33:44:55", "AA:BB:CC:A1:02:03"])
def test_bridge_valid_mac_accepted(mac):
    action = Isam_bridge_learned_mac(FakeModule([_mac_entry(mac=mac)]))
    assert action.build_commands() == [
        "admin bridge learned-unicast-mac vlan-port:1/1/6/1:3990 unicast-mac-address %s delete" % mac
    ]


def test_bridge_invalid_vlan_port_rejected():
    with pytest.raises(FakeFail) as exc:
        Isam_bridge_learned_mac(FakeModule([_mac_entry(vlan_port="vlan-port:1/1/6/1;reboot")])).build_commands()
    assert "Invalid vlan_port" in exc.value.kwargs["msg"]


def test_bridge_check_mode_never_connects():
    with patch(CONNECTION) as connect:
        result = Isam_bridge_learned_mac(FakeModule([_mac_entry()], check_mode=True)).execute_module()
    connect.assert_not_called()
    assert result["changed"] is True
    assert "response" not in result
