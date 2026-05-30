from __future__ import absolute_import, division, print_function

__metaclass__ = type

from textwrap import dedent

from ansible_collections.nokia.isam.tests.unit.modules.network.isam.isam_module import (
    TestIsamModule,
    set_module_args,
    ignore_provider_arg,
)
from ansible_collections.nokia.isam.plugins.modules import isam_alarm


class TestIsamAlarmModule(TestIsamModule):
    module = isam_alarm

    def setUp(self):
        super(TestIsamAlarmModule, self).setUp()

        self.get_config = self.mock_resource_connection_facts.get
        self.get_resource_connection_facts = self.mock_resource_connection_facts

    def test_isam_alarm_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure alarm log-sev-level warning log-full-action wrap non-itf-rep-sev-level minor
            configure alarm entry xtca-ne-es severity major service-affecting reporting logging
            configure alarm filter temporal filterid 1 alarmid xtca-ne-es status 1 threshold 3 window 5
            configure alarm delta-log indet-log-full-action wrap warn-log-full-action wrap minor-log-full-action wrap major-log-full-action wrap crit-log-full-act wrap
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        gathered = result.get("gathered", {})
        self.assertIn("log", gathered)
        self.assertEqual(gathered["log"]["log_sev_level"], "warning")

    def test_isam_alarm_rendered(self):
        set_module_args(
            dict(
                config=dict(
                    log=dict(
                        log_sev_level="warning",
                        log_full_action="wrap",
                        non_itf_rep_sev_level="minor",
                    ),
                ),
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("rendered", result)

    def test_isam_alarm_parsed(self):
        running = dedent(
            """\
            configure alarm log-sev-level warning log-full-action wrap non-itf-rep-sev-level minor
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
        self.assertIn("log", parsed)
        self.assertEqual(parsed["log"]["log_sev_level"], "warning")

    def test_isam_alarm_merged_check(self):
        self.get_config.return_value = dedent(
            """\
            configure alarm log-sev-level warning log-full-action wrap non-itf-rep-sev-level minor
            """
        )
        set_module_args(
            dict(
                config=dict(
                    log=dict(
                        log_sev_level="major",
                        log_full_action="halt",
                        non_itf_rep_sev_level="critical",
                    ),
                ),
                state="merged",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertTrue(result["changed"])
