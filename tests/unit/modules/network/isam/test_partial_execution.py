# -*- coding: utf-8 -*-
"""A refused command in the middle of a write reports what was applied (all resource modules)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule


class Failed(Exception):
    pass


class Module(object):
    check_mode = False
    params = {}

    def fail_json(self, **kwargs):
        raise Failed(kwargs)


class Connection(object):
    def __init__(self, refuse):
        self.refuse, self.sent = refuse, []

    def edit_config(self, candidate=None, **kwargs):
        (command,) = candidate
        self.sent.append(command)
        if command == self.refuse:
            raise Exception("Error : it is not possible to configure a severity on this interface")


def resource(commands, refuse=None, check_mode=False):
    obj = object.__new__(IsamResourceModule)
    obj._module = Module()
    obj._module.check_mode = check_mode
    obj.state = "deleted"
    obj.commands = list(commands)
    obj.changed = False
    obj.COMPACT_COMMAND_SCOPES = ()
    connection = Connection(refuse)
    obj._connection_obj = connection
    type(obj)  # noqa: B018
    return obj, connection


COMMANDS = ["configure bridge no port 1/1/7/16/1/1/1", "configure interface port vlan-port:1/1/7/16/1/1/1:10 no severity",
            "configure equipment ont no interface 1/1/7/16/1"]


@pytest.fixture(autouse=True)
def connection_property(monkeypatch):
    monkeypatch.setattr(IsamResourceModule, "_connection", property(lambda self: self._connection_obj), raising=False)


def test_a_refused_command_reports_accepted_failed_and_pending():
    obj, connection = resource(COMMANDS, refuse=COMMANDS[1])
    with pytest.raises(Failed) as raised:
        obj.run_commands()
    failure = raised.value.args[0]
    assert connection.sent == COMMANDS[:2]
    assert failure["accepted"] == COMMANDS[:1]
    assert failure["failed_command"] == COMMANDS[1]
    assert failure["pending"] == COMMANDS[2:]
    assert failure["changed"] is True
    assert failure["failure_phase"] == "execution" and "command 2 of 3 failed" in failure["msg"]


def test_a_first_command_refused_changed_nothing():
    obj, connection = resource(COMMANDS, refuse=COMMANDS[0])
    with pytest.raises(Failed) as raised:
        obj.run_commands()
    assert raised.value.args[0]["changed"] is False and raised.value.args[0]["accepted"] == []


def test_all_accepted_sends_each_once_and_check_mode_sends_nothing():
    obj, connection = resource(COMMANDS)
    obj.run_commands()
    assert connection.sent == COMMANDS and obj.changed is True
    obj, connection = resource(COMMANDS, check_mode=True)
    obj.run_commands()
    assert connection.sent == [] and obj.changed is True
