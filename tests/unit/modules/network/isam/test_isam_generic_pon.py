from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_generic_pon
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import Generic_ponTemplate
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamGenericPonModule(TestIsamModule):
    module = isam_generic_pon

    def setUp(self):
        super(TestIsamGenericPonModule, self).setUp()

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
        super(TestIsamGenericPonModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_generic_pon_parsed(self):
        running = dedent(
            """\
            configure generic-pon dpinteg-threshold 50
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["dpinteg_threshold"], 50)

    def test_isam_generic_pon_gathered(self):
        sample = dedent(
            """\
            configure generic-pon dpinteg-threshold 75
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["dpinteg_threshold"], 75)

    def test_isam_generic_pon_parses_packed_supported_flags(self):
        running = (
            "configure generic-pon utilization no pon-pmcollect no ont-pmcollect "
            "no ontbulk-pmcollect\n"
            "configure generic-pon ont no slid-mode no sn-bundle-timer "
            "no sw-ver-mis-block no sn-autounlock\n"
            "configure generic-pon alarmflag no ponlos-alarm-ctrl"
        )
        result = Generic_ponTemplate(lines=running.splitlines()).parse()
        self.assertEqual(
            result["utilization"],
            {"pon_pmcollect": False, "ont_pmcollect": False, "ontbulk_pmcollect": False},
        )
        self.assertEqual(result["ont"]["slid_mode"], False)
        self.assertEqual(result["alarmflag"]["ponlos_alarm_ctrl"], False)

    def test_isam_generic_pon_parses_utilization_thresholds(self):
        running = (
            "configure generic-pon utilization threshold txmcutilhi 80 "
            "txucdropfrmhi disabled numtcint 60"
        )
        threshold = Generic_ponTemplate(lines=[running]).parse()["utilization"]["threshold"]
        self.assertEqual(threshold["txmcutilhi"], "80")
        self.assertEqual(threshold["txucdropfrmhi"], "disabled")
        self.assertEqual(threshold["numtcint"], "60")

    def test_isam_generic_pon_rendered(self):
        set_module_args(
            dict(
                config=dict(dpinteg_threshold=50),
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure generic-pon dpinteg-threshold 50"],
        )

    def test_isam_generic_pon_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)

    def test_isam_generic_pon_deleted_has_threshold_no_form(self):
        assert Generic_ponTemplate().render(
            {"dpinteg_threshold": None}, "dpinteg_threshold", negate=True
        ) == "no configure generic-pon no dpinteg-threshold"
