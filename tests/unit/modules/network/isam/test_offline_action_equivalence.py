# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Offline action states render exactly what the module renders against a device.

For merged/replaced/overridden/deleted, ``config`` + ``running_config`` (CLI text or the
canonical JSON that ``gathered`` returns) must produce the same commands as the same
request against a fake device holding that configuration, without any device access.
"""
import json
from copy import deepcopy
from types import SimpleNamespace

import pytest

from . import contract_registry as _registry

from ansible.module_utils import basic
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg import base as cfg_base
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts import facts
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base import resource_module_base
from ansible_collections.nokia.isam.plugins.action.isam import ActionModule
from ansible_collections.nokia.isam.plugins.modules import (
    isam_bridges, isam_equipment_onts, isam_interfaces, isam_qos_interfaces, isam_vlans, isam_voice_sip,
)

from .isam_module import set_module_args

ACTION_STATES = ("merged", "replaced", "overridden", "deleted")


class Device:
    """A fake device answering every read with its configuration (None: no access allowed)."""

    def __init__(self, running=None):
        self.running = running
        self.reads = []
        self.writes = []

    def get(self, command):
        self.reads.append(command)
        if self.running is None:
            raise AssertionError("offline run read the device: %s" % command)
        return self.running

    def get_config(self, *args, **kwargs):
        return self.get("get_config")

    def edit_config(self, candidate=None, **kwargs):
        if self.running is None:
            raise AssertionError("offline run wrote to the device: %r" % candidate)
        self.writes.append(list(candidate))
        return {"response": [""] * len(candidate)}


def run(monkeypatch, capsys, module, args, device):
    for target in (resource_module_base, facts, cfg_base):
        monkeypatch.setattr(target, "get_resource_connection", lambda _module: device)
    set_module_args(dict(args, _ansible_check_mode=True), True)
    with pytest.raises(SystemExit) as exited:
        module.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code == 0, result
    return result


CASES = [
    pytest.param(
        isam_vlans,
        "configure vlan id 100 mode residential-bridge name Home priority 5 new-secure-fwd enable\n"
        "configure vlan id 200 mode residential-bridge name Other priority 4 new-secure-fwd enable\n",
        [{"id": "100", "name": "Changed", "priority": 6}, {"id": "300", "mode": "residential-bridge"}],
        id="vlans"),
    pytest.param(
        isam_interfaces,
        "configure interface port uni:1/1/5/1/1/1/1 admin-up user Y654321\n"
        "configure interface port uni:1/1/5/1/1/1/2 admin-up user Y000002\n",
        [{"name": "uni:1/1/5/1/1/1/1", "user": "Y999999"}],
        id="interfaces"),
    pytest.param(
        isam_equipment_onts,
        "configure equipment ont interface 1/1/6/1/1 sernum ALCL:F0000001 sw-ver-pland auto plnd-var DO enable-aes enable\n"
        "configure equipment ont interface 1/1/6/1/1 admin-state up\n"
        "configure equipment ont slot 1/1/6/1/1/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0\n"
        "configure equipment ont slot 1/1/6/1/1/1 admin-state up\n",
        {"interfaces": [{"ont_idx": "1/1/6/1/1", "admin_state": "down"}]},
        id="equipment_onts"),
    pytest.param(
        isam_bridges,
        "configure bridge port 1/1/8/1 max-unicast-mac 5 pvid 20\n"
        "configure bridge port 1/1/8/1 vlan-id 20 tag single-tagged l2fwder-vlan 720 vlan-scope local\n"
        "configure bridge port 1/1/8/1 vlan-id 30\n",
        {"port": [{"port": "1/1/8/1", "max_unicast_mac": 8,
                   "vlan_id": [{"id": "20", "tag": "single-tagged", "l2fwder_vlan": "720", "vlan_scope": "local"}]}]},
        id="bridges"),
    pytest.param(
        isam_qos_interfaces,
        "configure qos interface 1/1/2/1/1/1/1 cac-profile name:FD_ONTUniVideo\n"
        "configure qos interface 1/1/2/1/1/1/1 queue 0 priority 6 queue-profile name:NGLT_Default\n"
        "configure qos interface 1/1/2/1/1/1/2 cac-profile name:Other\n",
        [{"name": "1/1/2/1/1/1/1", "queue": [{"id": 0, "shaper_profile": "name:qssShaperDN920Mbps"}]}],
        id="qos_interfaces"),
    pytest.param(
        isam_voice_sip,
        "configure voice sip vsp vsp1 domain-name DomainName.com\n"
        "configure voice sip vsp vsp2 domain-name OtherDomain.com\n",
        {"vsp": [{"name": "vsp1", "domain_name": "Changed.com"}]},
        id="voice_sip (TableResourceModule)"),
]


@pytest.mark.parametrize("module,running,config", CASES)
@pytest.mark.skipif(not all(_registry.module_in_scope(c[0][0].__name__) for c in CASES), reason='offline equivalence covers the whole inventory only in the final integration PR')
def test_offline_action_states_match_device_run(monkeypatch, capsys, module, running, config):
    gathered = run(monkeypatch, capsys, module, {"state": "gathered"}, Device(running))["gathered"]
    assert gathered, "the fixture must parse"
    some_commands = False
    for state in ACTION_STATES:
        args = {"state": state, "config": deepcopy(config)}
        device = Device(running)
        online = run(monkeypatch, capsys, module, args, device)
        assert device.writes == []  # check mode
        for running_config in (running, json.dumps(gathered)):
            offline = run(monkeypatch, capsys, module, dict(args, running_config=running_config), Device())
            assert offline["commands"] == online["commands"], (state, running_config)
            assert offline["changed"] is False
            if running_config == running:
                assert offline["before"] == online["before"], state
        some_commands = some_commands or bool(online["commands"])
    assert some_commands


@_registry.requires('isam_vlans')
def test_offline_json_is_validated_like_config(monkeypatch, capsys):
    # "100"/100 and an explicit null compare like the device facts: no spurious diff.
    running = json.dumps([{"id": 100, "name": "Home", "priority": "5", "mode": "residential-bridge", "new_secure_fwd": None}])
    result = run(monkeypatch, capsys, isam_vlans, {
        "state": "merged", "config": [{"id": "100", "name": "Home", "priority": 5}], "running_config": running}, Device())
    assert result["commands"] == []
    assert result["before"] == [{"id": "100", "name": "Home", "priority": 5, "mode": "residential-bridge"}]


@pytest.mark.parametrize("running_config,message", [
    ("{not json", "neither CLI text nor valid JSON"),
    (json.dumps([{"id": "100", "priority": "high"}]), "does not match the config argspec"),
])
@_registry.requires('isam_vlans')
def test_offline_json_errors_fail_cleanly(monkeypatch, capsys, running_config, message):
    for target in (resource_module_base, facts, cfg_base):
        monkeypatch.setattr(target, "get_resource_connection", lambda _module: Device())
    set_module_args({"state": "deleted", "running_config": running_config}, True)
    with pytest.raises(SystemExit) as exited:
        isam_vlans.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code != 0
    assert result["failed"] and message in result["msg"]


def _offline_action(monkeypatch, module, args, diff=False, check_mode=False):
    action = object.__new__(ActionModule)
    action._task = SimpleNamespace(action="nokia.isam.%s" % module.__name__.rsplit(".", 1)[-1], args=args,
                                   check_mode=check_mode, diff=diff, no_log=False)
    action._play_context = SimpleNamespace(connection="nokia.isam.isam_network_cli", executable="/bin/sh")
    action._supports_check_mode = True
    action._connection = SimpleNamespace(socket_path=None, _shell=SimpleNamespace(tmpdir=None))
    monkeypatch.setattr(action, "_is_become_unprivileged", lambda: False)
    monkeypatch.setattr(action, "get_shell_option", lambda option, default=None: default)

    def no_connection(*_args, **_kwargs):
        raise AssertionError("the offline path must not use the persistent connection")

    monkeypatch.setattr(action, "_find_load_module", lambda: (module.__file__, module))
    monkeypatch.setattr(ActionModule.__bases__[0], "run", no_connection)
    monkeypatch.setattr(action, "_patch_update_module", no_connection, raising=False)
    monkeypatch.setattr(module, "AnsibleModule", basic.AnsibleModule)
    monkeypatch.setattr(basic, "_PARSED_MODULE_ARGS", None, raising=False)
    for target in (resource_module_base, facts, cfg_base):
        monkeypatch.setattr(target, "get_resource_connection", lambda _module: Device())
    return action


@_registry.requires('isam_vlans')
def test_action_plugin_offline_path_sets_ansible_args(monkeypatch):
    # The offline path must set the _ansible_* arguments (diff, verbosity, ...) like any run.
    seen = {}
    original = basic.AnsibleModule.__init__

    def recording_init(self, *args, **kwargs):
        original(self, *args, **kwargs)
        if "running_config" in self.params and not seen:  # the module, not facts' validators
            seen.update(diff=self._diff, check_mode=self.check_mode, verbosity=self._verbosity, name=self._name)

    action = _offline_action(monkeypatch, isam_vlans, {
        "state": "deleted", "running_config": "configure vlan id 100 mode residential-bridge name Home\n"},
        diff=True, check_mode=True)
    monkeypatch.setattr(basic.AnsibleModule, "__init__", recording_init)
    result = action.run(task_vars={})
    assert not result.get("failed"), result
    assert result["commands"] == ["configure vlan no id 100"]
    assert result["changed"] is False
    assert seen["diff"] is True and seen["check_mode"] is True
    assert seen["name"] == "nokia.isam.isam_vlans"


def test_action_plugin_offline_states_are_the_resource_action_states():
    assert set(ActionModule.OFFLINE_ACTION_STATES) == set(ACTION_STATES)


def _example_configs(name):
    """Literal config values of the module's EXAMPLES tasks (templated values dropped)."""
    from .test_module_docs_argspec import _blocks, _strip_templated, _tasks

    configs = []
    for task in _tasks(_blocks(name).get("EXAMPLES") or ""):
        for key in ("nokia.isam.%s" % name, name):
            args = task.get(key)
            # a gathered task's config is an instance selection, not a configuration
            if isinstance(args, dict) and args.get("config") and args.get("state") != "gathered" \
                    and "{{" not in json.dumps(args["config"]):
                configs.append(_strip_templated(args["config"]))
    return configs


def _resource_modules():
    import importlib

    from .test_module_docs_argspec import MODULE_NAMES

    for name in MODULE_NAMES:
        module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules.%s" % name)
        source = open(module.__file__).read()
        if "IsamResourceModule" in source or "execute_module()" in source and "running_config" in source:
            yield name, module


OFFLINE_SMOKE = [(name, module, config) for name, module in _resource_modules()
                 for config in _example_configs(name)[:2]]


@pytest.mark.parametrize("name,module,config", OFFLINE_SMOKE, ids=["%s-%d" % (c[0], i) for i, c in enumerate(OFFLINE_SMOKE)])
def test_every_resource_module_renders_action_states_offline(monkeypatch, capsys, name, module, config):
    # Every family: config + running_config (empty, and the request itself) renders for all
    # action states without reading or writing the device.
    for target in (resource_module_base, facts, cfg_base):
        monkeypatch.setattr(target, "get_resource_connection", lambda _module: Device())
    empty = "[]" if isinstance(config, list) else "{}"
    for state in ACTION_STATES:
        for running_config in (empty, json.dumps(config)):
            set_module_args({"state": state, "config": deepcopy(config), "running_config": running_config,
                             "_ansible_check_mode": False}, True)
            with pytest.raises(SystemExit) as exited:
                module.main()
            result = json.loads(capsys.readouterr().out)
            if exited.value.code != 0:
                # only a module's own validation may refuse (e.g. mandatory-at-creation)
                assert "exception" not in result and result.get("msg"), (state, running_config, result)
                assert "mutually exclusive" not in result["msg"], (state, result)
                continue
            assert result["changed"] is False, (state, result)
            assert isinstance(result["commands"], list)


@pytest.mark.parametrize("name,module", list(_resource_modules()), ids=[n for n, _m in _resource_modules()])
def test_every_resource_module_accepts_offline_running_config(monkeypatch, capsys, name, module):
    # Families without a literal example config are covered at least by deleted, which also
    # proves the offline path never reaches the device for them.
    from .test_module_docs_argspec import _module_kwargs

    kind = _module_kwargs(name, monkeypatch)["argument_spec"]["config"]["type"]
    monkeypatch.undo()
    for target in (resource_module_base, facts, cfg_base):
        monkeypatch.setattr(target, "get_resource_connection", lambda _module: Device())
    set_module_args({"state": "deleted", "running_config": "[]" if kind == "list" else "{}"}, True)
    with pytest.raises(SystemExit) as exited:
        module.main()
    result = json.loads(capsys.readouterr().out)
    assert exited.value.code == 0, result
    assert result["commands"] == [] and result["changed"] is False
