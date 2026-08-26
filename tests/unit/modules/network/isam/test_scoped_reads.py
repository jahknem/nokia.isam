from types import SimpleNamespace

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.bridges.bridges import (
    BridgesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import (
    Equipment_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_onts.ethernet_onts import (
    Ethernet_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces import (
    Pon_interfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
)


class RecordingConnection:
    def __init__(self):
        self.commands = []

    def get(self, command):
        self.commands.append(command)
        return command


def module(config, state="merged"):
    return SimpleNamespace(params={"config": config, "state": state})


@pytest.mark.parametrize(
    "facts_cls,config,expected",
    [
        (
            Pon_interfacesFacts,
            [{"name": "1/1/5/1"}],
            "info configure pon interface 1/1/5/1 flat detail",
        ),
        (
            InterfacesFacts,
            [{"name": "pon:1/1/5/1"}],
            "info configure interface port pon:1/1/5/1 detail flat",
        ),
        (
            Ethernet_ontsFacts,
            [{"uni_idx": "1/1/5/1/100/1/1"}],
            "info configure ethernet ont 1/1/5/1/100/1/1 flat detail",
        ),
        (
            BridgesFacts,
            {"port": [{"port": "1/1/5/1/100/1/1"}]},
            "info configure bridge port 1/1/5/1/100/1/1 flat detail",
        ),
    ],
)
def test_resource_facts_read_only_requested_identities(facts_cls, config, expected):
    connection = RecordingConnection()
    result = facts_cls(module(config)).get_config(connection)

    assert connection.commands == [expected]
    assert result == expected


def test_equipment_facts_reads_requested_interface_and_slot_identities():
    connection = RecordingConnection()
    config = {
        "interfaces": [{"ont_idx": "1/1/5/1/100"}],
        "slots": [{"ont_slot_idx": "1/1/5/1/100/1"}],
        "sw_ctrls": [],
    }

    Equipment_ontsFacts(module(config)).get_config(connection)

    assert connection.commands == [
        "info configure equipment ont interface 1/1/5/1/100 flat detail",
        "info configure equipment ont slot 1/1/5/1/100/1 flat detail",
    ]


def test_qos_facts_scope_uses_one_command_per_requested_interface():
    connection = RecordingConnection()
    config = [{"name": "1/1/5/1/100/1/1"}]

    result = get_scoped_config(
        module(config),
        connection,
        config,
        "info configure qos interface flat",
        ["info configure qos interface 1/1/5/1/100/1/1 flat"],
    )

    assert connection.commands == ["info configure qos interface 1/1/5/1/100/1/1 flat"]
    assert result == connection.commands[0]


def test_scoped_facts_ignore_missing_requested_instances():
    class MissingConnection(RecordingConnection):
        def get(self, command):
            self.commands.append(command)
            return "Error : instance does not exist"

    connection = MissingConnection()
    result = get_scoped_config(
        module([{"name": "uni:1/1/5/1/100/1/1"}]),
        connection,
        [],
        "info configure interface port flat",
        ["info configure interface port uni:1/1/5/1/100/1/1 detail flat"],
    )

    assert result == ""
    assert len(connection.commands) == 1


def test_scoped_facts_ignore_specified_missing_requested_instances():
    class MissingConnection(RecordingConnection):
        def get(self, command):
            self.commands.append(command)
            return "Error : The specified instance does not exist"

    connection = MissingConnection()
    result = get_scoped_config(
        module([]),
        connection,
        [],
        "info configure interface port flat",
        ["info configure interface port uni:1/1/5/1/100/1/1 detail flat"],
    )

    assert result == ""


def test_scoped_facts_ignore_missing_bridge_lower_interface():
    class MissingConnection(RecordingConnection):
        def get(self, command):
            self.commands.append(command)
            raise RuntimeError("specified lower-interface does not exist")

    connection = MissingConnection()
    result = get_scoped_config(
        module({"port": [{"port": "1/1/5/1/2/1/1"}]}),
        connection,
        {"port": [{"port": "1/1/5/1/2/1/1"}]},
        "info configure bridge flat",
        ["info configure bridge port 1/1/5/1/2/1/1 flat detail"],
    )

    assert result == ""


@pytest.mark.parametrize("state", ["overridden", "deleted"])
def test_scoped_facts_fall_back_for_unbounded_destructive_states(state):
    connection = RecordingConnection()
    config = [] if state == "deleted" else [{"name": "pon:1/1/5/1"}]

    Pon_interfacesFacts(module(config, state)).get_config(connection)

    assert connection.commands == ["info configure pon interface flat"]
