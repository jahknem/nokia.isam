from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent

from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from ansible_collections.nokia.isam.tests.unit.modules.network.isam.isam_module import (
    TestIsamModule,
    set_module_args,
)
from ansible_collections.nokia.isam.plugins.modules import isam_alarm


ignore_provider_arg = True


class TestIsamAlarmModule(TestIsamModule):
    module = isam_alarm

    def setUp(self):
        super(TestIsamAlarmModule, self).setUp()

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
        super(TestIsamAlarmModule, self).tearDown()

    def test_isam_alarm_rendered(self):
        set_module_args(
            dict(
                config=dict(log=dict(log_sev_level="warning", log_full_action="wrap", non_itf_rep_sev_level="minor")),
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("rendered", result)

    def test_isam_alarm_parsed(self):
        running = dedent("""\
            configure alarm log-sev-level warning log-full-action wrap non-itf-rep-sev-level minor
        """)
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        parsed = result.get("parsed", {})
        self.assertIn("log", parsed)
        self.assertEqual(parsed["log"]["log_sev_level"], "warning")
