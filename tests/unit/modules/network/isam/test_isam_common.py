import re
from types import SimpleNamespace

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import compact_cli_commands


QOS_SCOPES = (
    re.compile(
        r"^(?P<scope>configure qos interface \S+ queue \d+) "
        r"(?P<suffix>(?!no(?:\s|$)).+)$"
    ),
)


def test_compact_cli_commands_only_merges_adjacent_positive_matching_scopes():
    commands = [
        "configure qos interface 1/1/8/28 queue 0 priority 6",
        "configure qos interface 1/1/8/28 queue 0 weight 34",
        "configure qos interface 1/1/8/28 queue 1 priority 7",
        "configure qos interface 1/1/8/28 queue 0 no weight",
        "configure qos interface 1/1/8/28 queue 0 queue-profile name:Default",
    ]
    assert compact_cli_commands(commands, QOS_SCOPES) == [
        "configure qos interface 1/1/8/28 queue 0 priority 6 weight 34",
        "configure qos interface 1/1/8/28 queue 1 priority 7",
        "configure qos interface 1/1/8/28 queue 0 no weight",
        "configure qos interface 1/1/8/28 queue 0 queue-profile name:Default",
    ]


def test_compact_cli_commands_allows_negation_when_the_scope_allows_it():
    scopes = (
        re.compile(r"^(?P<scope>configure ethernet ont \S+) (?P<suffix>.+)$"),
    )
    commands = [
        "configure ethernet ont 1/1/5/1/6/1/1 cust-info Y1110111",
        "configure ethernet ont 1/1/5/1/6/1/1 auto-detect auto",
        "configure ethernet ont 1/1/5/1/6/1/1 no power-control",
    ]

    assert compact_cli_commands(commands, scopes) == [
        "configure ethernet ont 1/1/5/1/6/1/1 cust-info Y1110111 auto-detect auto no power-control"
    ]


class _DirectCommandResource(ResourceModule):
    COMPACT_COMMAND_SCOPES = QOS_SCOPES


def _direct_command_resource(state):
    resource = object.__new__(_DirectCommandResource)
    resource.state = state
    resource.commands = [
        "configure qos interface 1/1/8/28 queue 0 priority 6",
        "configure qos interface 1/1/8/28 queue 0 weight 34",
    ]
    resource.warnings = []
    resource.changed = False
    resource.before = []
    resource._module = SimpleNamespace(check_mode=True)
    return resource


def test_resource_result_compacts_commands_built_without_addcmd():
    resource = _direct_command_resource("rendered")

    assert resource.result["rendered"] == [
        "configure qos interface 1/1/8/28 queue 0 priority 6 weight 34"
    ]


def test_resource_run_commands_compacts_before_check_mode_result():
    resource = _direct_command_resource("merged")

    resource.run_commands()

    assert resource.commands == [
        "configure qos interface 1/1/8/28 queue 0 priority 6 weight 34"
    ]
    assert resource.changed is True
