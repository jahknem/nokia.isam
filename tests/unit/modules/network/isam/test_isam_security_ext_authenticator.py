from ansible_collections.nokia.isam.plugins.modules import isam_security_ext_authenticator
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIsamSecurityExtAuthenticatorModule(TestIsamModule):
    module = isam_security_ext_authenticator

    def test_check_mode_returns_action_commands_without_connecting(self):
        with patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.security_ext_authenticator.security_ext_authenticator.get_resource_connection"
        ) as get_connection:
            set_module_args({
                "_ansible_check_mode": True,
                "config": [
                    {"port": "1/1/1/1"},
                    {"port": "1/1/1/2", "clear_statistics": True},
                ],
            }, True)
            result = self.execute_module(changed=True)
        get_connection.assert_not_called()
        self.assertEqual(result["commands"], [
            "admin security ext-authenticator 1/1/1/1",
            "admin security ext-authenticator 1/1/1/2 clear-statistics",
        ])

    def test_action_executes_only_when_not_check_mode(self):
        class FakeConnection:
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                return "admin security ext-authenticator 1/1/1/1 clear-statistics"

            def edit_config(self, candidate):
                self.commands.extend(candidate)

        connection = FakeConnection()
        connection_patch = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.security_ext_authenticator.security_ext_authenticator.get_resource_connection"
        )
        get_connection = connection_patch.start()
        get_connection.return_value = connection
        try:
            set_module_args(
                {"config": [{"port": "1/1/1/1"}]},
                False,
            )
            result = self.execute_module(changed=True)
            self.assertEqual(
                result["commands"],
                ["admin security ext-authenticator 1/1/1/1"],
            )
        finally:
            connection_patch.stop()
