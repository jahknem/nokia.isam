from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_traps
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamTrapsModule(TestIsamModule):
    module = isam_traps

    def setUp(self):
        super(TestIsamTrapsModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.traps.traps.Isam_trapsFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def tearDown(self):
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
        self.mock_get_config.stop()
        super(TestIsamTrapsModule, self).tearDown()

    def test_isam_traps_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    definitions=[
                        dict(name="cold-start", priority="high"),
                        dict(name="link-down"),
                    ],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("rendered", result)

    def test_isam_traps_parsed(self):
        running = dedent("""\
            configure trap definition cold-start priority high
            configure trap definition link-down
            configure trap manager 10.0.0.1:162 priority high
        """)
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        parsed = result.get("parsed", {})
        self.assertIn("definitions", parsed)

    def test_isam_traps_replaced_resets_omitted_trap_type(self):
        self.get_config.return_value = dedent("""\
            configure trap manager 10.0.0.1:162 priority high
            configure trap manager 10.0.0.1:162 cold-start-trap
            configure trap manager 10.0.0.1:162 link-down-trap
        """)
        set_module_args(dict(
            state="replaced",
            config=dict(
                managers=[dict(
                    address="10.0.0.1:162",
                    priority="high",
                    cold_start_trap=True,
                )],
            ),
        ), ignore_provider_arg)
        result = self.execute_module(changed=True)
        commands = result["commands"]
        self.assertIn(
            "configure trap manager 10.0.0.1:162 no link-down-trap",
            commands,
        )
        self.assertNotIn(
            "configure trap manager 10.0.0.1:162 cold-start-trap",
            commands,
        )
        self.assertNotIn(
            "configure trap manager 10.0.0.1:162 no priority",
            commands,
        )

    def test_isam_traps_replaced_idempotent_no_change(self):
        self.get_config.return_value = dedent("""\
            configure trap manager 10.0.0.1:162 cold-start-trap
        """)
        set_module_args(dict(
            state="replaced",
            config=dict(
                managers=[dict(
                    address="10.0.0.1:162",
                    cold_start_trap=True,
                )],
            ),
        ), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_traps_replaced_v6manager_resets_trap_type(self):
        self.get_config.return_value = dedent("""\
            configure trap v6manager 2001:db8::1 cold-start-trap
            configure trap v6manager 2001:db8::1 link-down-trap
        """)
        set_module_args(dict(
            state="replaced",
            config=dict(
                v6managers=[dict(
                    ipv6address="2001:db8::1",
                    cold_start_trap=True,
                )],
            ),
        ), ignore_provider_arg)
        result = self.execute_module(changed=True)
        commands = result["commands"]
        self.assertIn(
            "configure trap v6manager 2001:db8::1 no link-down-trap",
            commands,
        )

    def test_isam_traps_replaced_resets_omitted_shaping(self):
        self.get_config.return_value = dedent("""\
            configure trap manager 10.0.0.1:162 max-per-window 5
            configure trap manager 10.0.0.1:162 window-size 100
        """)
        set_module_args(dict(
            state="replaced",
            config=dict(
                managers=[dict(
                    address="10.0.0.1:162",
                )],
            ),
        ), ignore_provider_arg)
        result = self.execute_module(changed=True)
        commands = result["commands"]
        self.assertIn(
            "configure trap manager 10.0.0.1:162 no max-per-window",
            commands,
        )
        self.assertIn(
            "configure trap manager 10.0.0.1:162 no window-size",
            commands,
        )

    def test_isam_traps_replaced_definitions_noop(self):
        self.get_config.return_value = dedent("""\
            configure trap definition cold-start priority high
            configure trap definition link-down
        """)
        set_module_args(dict(
            state="replaced",
            config=dict(
                definitions=[dict(
                    name="cold-start",
                    priority="high",
                )],
            ),
        ), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
