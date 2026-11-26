from pathlib import Path

from ansible_collections.nokia.isam.plugins.modules import isam_ihub_ports, isam_ihub_lags, isam_ihub_services
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIhubReadModules(TestIsamModule):
    module = isam_ihub_ports

    def setUp(self):
        super().setUp()
        self.module = isam_ihub_ports
        self.connection = patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection")
        self.get_conn = self.connection.start()
        self.commands = []
        self.text = (Path(__file__).parents[4] / "fixtures/ihub_configuration/observed-shapes/output.txt").read_text()
        test = self

        class Conn:
            def get(self, command):
                test.commands.append(command)
                return test.text

        self.get_conn.return_value = Conn()

    def tearDown(self):
        self.connection.stop()
        super().tearDown()

    def test_port_root_read_needs_consent_before_connection(self):
        set_module_args({"state": "gathered"}, ignore_provider=True)
        self.failed()
        self.get_conn.assert_not_called()

    def test_port_gather_reports_real_source_and_returns_typed_config(self):
        set_module_args({"state": "gathered", "allow_broad_read": True}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(self.commands, ["info configure"])
        self.assertEqual(result["source"]["read_scope"], "device")
        self.assertTrue(result["source"]["collected_at"].endswith("Z"))
        self.assertEqual(len(result["gathered"]), 5)
        self.assertTrue(result["coverage"]["complete"])

    def test_port_selection_filters_only_with_explicit_whole_source_permission(self):
        set_module_args({"state": "gathered", "config": [{"id": "nt-a:xfp:2"}], "allow_broad_read": True}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual([p["id"] for p in result["gathered"]], ["nt-a:xfp:2"])
        self.assertEqual(self.commands, ["info configure"])
        self.assertEqual(result["source"]["read_scope"], "device")

    def test_service_family_read_does_not_require_redundant_broad_consent(self):
        self.module = isam_ihub_services
        set_module_args({"state": "gathered"}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(self.commands, ["info configure service"])
        self.assertEqual(result["source"]["read_scope"], "family")
        self.assertEqual(len(result["gathered"]["services"]), 2)

    def test_service_selection_cannot_silently_widen(self):
        self.module = isam_ihub_services
        set_module_args({"state": "gathered", "config": {"services": [{"service_type": "vpls", "id": "200"}]}}, ignore_provider=True)
        self.failed()
        self.get_conn.assert_not_called()

    def test_service_selection_requires_customer_type_aware_identity(self):
        self.module = isam_ihub_services
        set_module_args({"state": "gathered", "allow_broad_read": True,
                         "config": {"services": [{"service_type": "vpls", "id": "200"}]}}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(len(result["gathered"]["services"]), 1)
        self.assertEqual(result["gathered"]["customers"], [])

    def test_lag_parsing_is_offline_and_read_only(self):
        self.module = isam_ihub_lags
        set_module_args({"state": "parsed", "running_config": self.text}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["lacp"]["administrative_key"], 32768)
        self.assertEqual(result["source"]["read_scope"], "offline")
        self.get_conn.assert_not_called()

    def test_write_state_is_rejected_before_connection(self):
        set_module_args({"state": "merged", "config": [{"id": "nt-a:xfp:2"}]}, ignore_provider=True)
        self.failed()
        self.get_conn.assert_not_called()

    def test_check_mode_reads_like_a_normal_run(self):
        # read-only modules never write, so check mode returns the same data
        set_module_args({"state": "gathered", "allow_broad_read": True, "_ansible_check_mode": True}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertNotIn("skipped", result)
        self.assertEqual(self.commands, ["info configure"])
        self.assertEqual(len(result["gathered"]), 5)
        self.assertEqual(result["ansible_facts"]["ansible_network_resources"]["ihub_ports"], result["gathered"])

    def test_parsed_does_not_publish_facts(self):
        set_module_args({"state": "parsed", "running_config": self.text}, ignore_provider=True)
        result = self.execute_module(changed=False)
        self.assertTrue(result["parsed"])
        self.assertNotIn("ansible_facts", result)

    def test_selection_accepts_only_identity_keys(self):
        set_module_args({"state": "gathered", "allow_broad_read": True,
                         "config": [{"id": "nt-a:xfp:2", "description": "ignored before"}]}, ignore_provider=True)
        result = self.failed()
        self.assertIn("description", result["msg"])
        self.get_conn.assert_not_called()

    def test_lag_selection_no_longer_requires_nested_fields(self):
        self.module = isam_ihub_lags
        set_module_args({"state": "gathered", "allow_broad_read": True, "config": [{"id": "1"}]}, ignore_provider=True)
        self.execute_module(changed=False)

    def test_wrong_family_source_fails_not_empty(self):
        self.text = 'echo "port-protection"\n----------'
        set_module_args({"state": "gathered", "allow_broad_read": True}, ignore_provider=True)
        self.failed()
