from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_traps

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamTrapsModule(TestIsamModule):
    module = isam_traps

    def setUp(self):
        super(TestIsamTrapsModule, self).setUp()
        self.get_config = self.mock_resource_connection_facts.get
        self.get_resource_connection_facts = self.mock_resource_connection_facts

    def test_isam_traps_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure
              trap
                definition cold-start
                  priority high
                definition link-down
                manager 10.0.0.1:162
                  priority high
                  cold-start-trap
                  link-down-trap
                  max-per-window 10
                v6manager 2001:db8::1/162
                  priority medium
                  link-up-trap
              exit
              exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        gathered = result.get("gathered", {})
        self.assertIn("definitions", gathered)
        self.assertIn("managers", gathered)
        self.assertIn("v6managers", gathered)

    def test_isam_traps_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    definitions=[
                        dict(name="cold-start", priority="high"),
                        dict(name="link-down"),
                    ],
                    managers=[
                        dict(
                            address="10.0.0.1:162",
                            priority="high",
                            cold_start_trap=True,
                            link_down_trap=True,
                            max_per_window=10,
                        ),
                    ],
                    v6managers=[
                        dict(
                            ipv6address="2001:db8::1/162",
                            priority="medium",
                            link_up_trap=True,
                        ),
                    ],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("rendered", result)
        rendered = result["rendered"]
        self.assertIn("configure trap definition cold-start priority high", rendered)
        self.assertIn("configure trap definition link-down", rendered)
        self.assertIn("configure trap manager 10.0.0.1:162 priority high cold-start-trap link-down-trap max-per-window 10", rendered)
        self.assertIn("configure trap v6manager 2001:db8::1/162 priority medium link-up-trap", rendered)

    def test_isam_traps_parsed(self):
        running = dedent(
            """\
            configure trap definition cold-start priority high
            configure trap definition link-down
            configure trap manager 10.0.0.1:162 priority high cold-start-trap link-down-trap
            configure trap v6manager 2001:db8::1/162 priority medium link-up-trap
            """
        )
        set_module_args(
            dict(
                running_config=running,
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        parsed = result.get("parsed", {})
        self.assertIn("definitions", parsed)
        self.assertIn("managers", parsed)
        self.assertIn("v6managers", parsed)

    def test_isam_traps_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure
              trap
                definition cold-start
                  priority high
                definition link-down
                manager 10.0.0.1:162
                  priority high
                  cold-start-trap
              exit
              exit
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    definitions=[
                        dict(name="cold-start", priority="high"),
                        dict(name="link-down"),
                    ],
                    managers=[
                        dict(
                            address="10.0.0.1:162",
                            priority="high",
                            cold_start_trap=True,
                        ),
                    ],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
