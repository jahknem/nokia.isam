from ansible_collections.nokia.isam.plugins.modules import cli_config
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestCliConfigModule(TestIsamModule):
    module = cli_config

    def test_check_mode_renders_config_without_connecting(self):
        with patch(
            "ansible_collections.nokia.isam.plugins.modules.cli_config.get_resource_connection"
        ) as get_connection:
            set_module_args({"_ansible_check_mode": True, "config": "configure system\n  id name access-node"}, True)
            result = self.execute_module(changed=True)
        get_connection.assert_not_called()
        self.assertEqual(result["commands"], ["configure system", "  id name access-node"])

    def test_config_is_sent_when_not_in_check_mode(self):
        class FakeConnection:
            def __init__(self):
                self.calls = []

            def edit_config(self, candidate):
                self.calls.append(candidate)

        connection = FakeConnection()
        with patch(
            "ansible_collections.nokia.isam.plugins.modules.cli_config.get_resource_connection",
            return_value=connection,
        ):
            set_module_args({"config": "configure system"}, False)
            result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure system"])
        self.assertEqual(connection.calls, [["configure system"]])

    def test_complete_configure_commands_are_sent_individually(self):
        class FakeConnection:
            def __init__(self):
                self.calls = []

            def edit_config(self, candidate):
                self.calls.append(candidate)

        connection = FakeConnection()
        with patch(
            "ansible_collections.nokia.isam.plugins.modules.cli_config.get_resource_connection",
            return_value=connection,
        ):
            set_module_args(
                {"config": "configure system\nconfigure qos interface ont:1 scheduler-node name:X"},
                False,
            )
            self.execute_module(changed=True)
        self.assertEqual(
            connection.calls,
            [["configure system"], ["configure qos interface ont:1 scheduler-node name:X"]],
        )
