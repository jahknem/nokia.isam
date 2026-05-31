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

    def tearDown(self):
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()
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
