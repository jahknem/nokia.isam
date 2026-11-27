from types import SimpleNamespace

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.software_mngt.software_mngt import (
    Software_mngt,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    Software_mngtTemplate,
)

HAVE = {
    "database": {"backup": "activate:192.0.2.10:backup/"},
    "oswp": [
        {"id": "1", "primary_file_server_id": "a", "second_file_server_id": "b",
         "activate": "after-download", "auto_verify": "enabled", "on_schedule_time": "x"},
        {"id": "2", "primary_file_server_id": "c", "second_file_server_id": "d", "admin_state": True},
    ],
}


def _run(state, want, config=None, have=None):
    resource = object.__new__(Software_mngt)
    resource.state = state
    resource.want = want
    resource.have = HAVE if have is None else have
    resource.commands = []
    resource._tmplt = Software_mngtTemplate()
    warnings = []
    resource._module = SimpleNamespace(params={"config": config if config is not None else want},
                                       warn=warnings.append)
    resource.generate_commands()
    return resource.commands, warnings


def _no_removal_or_activation(commands):
    # An OSWP is a fixed slot without removal form; nothing may activate or auto-verify
    # a package unless the request names it.
    assert not [c for c in commands if " no oswp" in c]
    assert not [c for c in commands if "activate after-download" in c or "activate on-schedule" in c]
    assert not [c for c in commands if "auto-verify enabled" in c]


def test_deleted_oswp_identity_resets_instead_of_removing():
    commands, warnings = _run("deleted", {"oswp": [{"id": "1"}]})
    assert commands == ["configure software-mngt oswp 1 no activate no auto-verify no on-schedule-time"]
    assert warnings and "oswp 1" in warnings[0]
    _no_removal_or_activation(commands)


def test_deleted_oswp_named_attribute_resets_only_itself():
    commands, _warnings = _run("deleted", {"oswp": [{"id": "1", "auto_verify": "enabled"}]})
    assert commands == ["configure software-mngt oswp 1 no auto-verify"]


def test_deleted_without_config_never_removes_oswp():
    commands, _warnings = _run("deleted", {}, config={})
    assert "configure software-mngt oswp 1 no activate no auto-verify no on-schedule-time" in commands
    assert not [c for c in commands if "oswp 2" in c]  # admin-state is not reset implicitly
    _no_removal_or_activation(commands)


def test_overridden_with_only_database_keeps_oswp_slots():
    commands, _warnings = _run("overridden", {"database": {"backup": "activate:192.0.2.10:backup/"}})
    assert commands == ["configure software-mngt oswp 1 no activate no auto-verify no on-schedule-time"]
    _no_removal_or_activation(commands)


def test_overridden_named_oswp_never_activates_unless_named():
    commands, _warnings = _run("overridden", {"oswp": [{"id": "2", "primary_file_server_id": "e"}]})
    _no_removal_or_activation(commands)
    assert "configure software-mngt oswp 2 primary-file-server-id e" in commands


def test_replaced_and_overridden_keep_an_omitted_admin_state():
    # Review of #19: a named OSWP without admin_state got 'no admin-state'.
    for state in ("replaced", "overridden"):
        commands, _warnings = _run(state, {"oswp": [{"id": "2", "primary_file_server_id": "c",
                                                      "second_file_server_id": "d"}]})
        assert not [c for c in commands if "admin-state" in c], (state, commands)
