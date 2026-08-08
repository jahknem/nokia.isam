from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_security_ext_authenticator

from .isam_module import TestIsamModule, set_module_args


class TestIsamSecurityExtAuthenticatorModule(TestIsamModule):
    module = isam_security_ext_authenticator

    def test_rendered_is_non_mutating(self):
        set_module_args({
            "state": "rendered",
            "config": [
                {"port": "1/1/1/1"},
                {"port": "1/1/1/2", "clear_statistics": True},
            ],
        }, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [
            "admin security ext-authenticator 1/1/1/1",
            "admin security ext-authenticator 1/1/1/2 clear-statistics",
        ])

    def test_parsed(self):
        set_module_args({
            "state": "parsed",
            "running_config": dedent("""
                admin security ext-authenticator 1/1/1/1
                admin security ext-authenticator 1/1/1/2 clear-statistics
            """),
        }, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["config"], [
            {"port": "1/1/1/1", "clear_statistics": False},
            {"port": "1/1/1/2", "clear_statistics": True},
        ])
