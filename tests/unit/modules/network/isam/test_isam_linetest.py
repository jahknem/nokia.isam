from textwrap import dedent

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate
from ansible_collections.nokia.isam.plugins.modules import isam_linetest
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


def test_linetest_parse_ignores_test_actions():
    parsed = LinetestTemplate().parse(dedent("""
        configure linetest single ltsession 3 session-cmd create timeout-period 120 test-mode single
        configure linetest single ltparm 3 resist-tr(ohm) value1 1 min-threshold 10
    """))
    assert parsed["sessions"] == [{"session_id": "3", "timeout_period": "120", "test_mode": "single"}]
    assert parsed["parameters"] == [{
        "session_id": "3", "test_name": "resist-tr(ohm)", "value1": "1", "min_threshold": "10",
    }]


def test_linetest_render_is_configuration_only():
    commands = LinetestTemplate().render({"sessions": [{"session_id": "1", "timeout_period": "120"}], "parameters": []})
    assert commands == ["configure linetest single ltsession 1 timeout-period 120"]
    assert all("session-cmd" not in command for command in commands)


def test_linetest_parse_supports_unset_optional_fields():
    parsed = LinetestTemplate().parse(
        "configure linetest single ltsession 1 no group-opt no busy-overwrite"
    )
    assert parsed["sessions"] == [{
        "session_id": "1", "group_opt": None, "busy_overwrite": None,
    }]


class TestLinetestStates(TestIsamModule):
    module = isam_linetest

    def setUp(self):
        super(TestLinetestStates, self).setUp()
        self.connection_patch = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.linetest.linetest.get_resource_connection"
        )
        self.get_connection = self.connection_patch.start()

    def tearDown(self):
        self.connection_patch.stop()
        super(TestLinetestStates, self).tearDown()

    def test_merged_and_deleted_are_supported(self):
        class FakeConnection:
            def __init__(self):
                self.commands = []

            def get(self, command):
                return "configure linetest single ltsession 1 timeout-period 60"

            def edit_config(self, candidate):
                self.commands.extend(candidate)

        connection = FakeConnection()
        self.get_connection.return_value = connection
        set_module_args(
            {
                "state": "merged",
                "config": {"sessions": [{"session_id": "1", "timeout_period": "120"}]},
            },
            True,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure linetest single ltsession 1 timeout-period 120", result["commands"])

        set_module_args(
            {"state": "deleted", "config": {"sessions": [{"session_id": "1"}]}},
            True,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure linetest single ltsession 1 session-cmd destroy"],
        )
