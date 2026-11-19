"""Exercise netcommon's real direct-execution argument and result handling.

Only connection discovery is stubbed: facts parsing/validation, AnsibleModule,
netcommon's DirectExecutionModule and the resource reconciliation remain real.
Run under both the current core and the pinned EE core (tox -e py312-core219).
"""
from copy import deepcopy
from types import SimpleNamespace

import pytest

from ansible.module_utils import basic
from ansible import template
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base import resource_module_base
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts import facts
from ansible_collections.nokia.isam.plugins.action.isam import ActionModule
from ansible_collections.nokia.isam.plugins.modules import isam_equipment_onts


class Connection:
    def __init__(self, running):
        self.running = running
        self.reads = []
        self.writes = []

    def get(self, command):
        self.reads.append(command)
        return self.running

    def edit_config(self, candidate):
        self.writes.append(list(candidate))
        return {"response": [""] * len(candidate)}


@pytest.mark.parametrize("check_mode", [False, True])
@pytest.mark.parametrize("templated", [False, True])
@pytest.mark.parametrize("reply_style", ["flat", "block", "wrapped-echo"])
def test_admin_only_merged_keeps_single_element_list(monkeypatch, check_mode, templated, reply_style):
    running = "configure equipment ont interface 1/1/6/1/1 admin-state down\n"
    if reply_style == "block":
        running = "configure equipment\nont\ninterface 1/1/6/1/1\n  admin-state down\nexit\nexit\n"
    elif reply_style == "wrapped-echo":
        running = "info configure equipment ont interface 1/1/6/1/1 fl\nat detail\n# header\n" + running
    connection = Connection(running)
    monkeypatch.setattr(resource_module_base, "get_resource_connection", lambda module: connection)
    monkeypatch.setattr(facts, "get_resource_connection", lambda module: connection)
    # Direct execution patches the entrypoint globally; restore it after each test.
    monkeypatch.setattr(isam_equipment_onts, "AnsibleModule", basic.AnsibleModule)
    monkeypatch.setattr(basic, "_PARSED_MODULE_ARGS", None, raising=False)
    config = {"interfaces": [{"ont_idx": "1/1/6/1/1", "admin_state": "up"}]}
    if templated:
        trust = getattr(template, "trust_as_template", lambda value: value)
        config = template.Templar(variables={"ont_interfaces": config["interfaces"]}).template(
            {"interfaces": trust("{{ ont_interfaces }}")})
    action = object.__new__(ActionModule)
    action._task = SimpleNamespace(
        action="nokia.isam.isam_equipment_onts", args={"state": "merged", "config": config}, check_mode=check_mode)
    action._play_context = SimpleNamespace(connection="nokia.isam.isam_network_cli")
    monkeypatch.setattr(action, "_check_dexec_eligibility", lambda host: True)
    monkeypatch.setattr(action, "_find_load_module", lambda: (isam_equipment_onts.__file__, isam_equipment_onts))
    # ActionBase's inventory/magic-variable plumbing is not under test.
    monkeypatch.setattr(action, "_update_module_args", lambda *args: None)
    original = deepcopy(action._task.args)
    result = action.run(task_vars={"ansible_host": "offline-test"})
    assert not result.get("failed"), result
    command = "configure equipment ont interface 1/1/6/1/1 admin-state up"
    assert result["commands"] == [command]
    assert result["changed"] is True
    assert connection.writes == ([] if check_mode else [[command]])
    assert connection.reads and set(connection.reads) == {
        "info configure equipment ont interface 1/1/6/1/1 flat detail"}
    assert action._task.args["config"] == original["config"]
