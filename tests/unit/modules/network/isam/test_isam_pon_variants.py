from ansible_collections.nokia.isam.plugins.modules import isam_epon_interfaces, isam_ngpon2_channel_groups
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants import pon_variants
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import (
    Channel_pair_pmTemplate,
    Epon_interfacesTemplate,
    Ngpon2_channel_groupsTemplate,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from .isam_module import TestIsamModule, set_module_args

ignore_provider_arg = True

class TestPonVariantModules(TestIsamModule):
    def setUp(self):
        super(TestPonVariantModules, self).setUp()
        self.connection = patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection").start()
        self.variant_connection = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants.get_resource_connection"
        ).start()

    def tearDown(self):
        patch.stopall()
        super(TestPonVariantModules, self).tearDown()

    def test_ngpon2_rendered(self):
        self.module = isam_ngpon2_channel_groups
        set_module_args(dict(config=[dict(id=1, name="group-a", channel_pairs=["1/1/1/1"], subchannel_groups=[dict(id=2, name="scg-a", channel_pairs=["1/1/1/2"])])], state="rendered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertIn("configure channel-group id 1 name group-a", result["rendered"])
        self.assertIn("configure channel-group id 1 channel-pair 1/1/1/1", result["rendered"])
        self.assertIn("configure channel-group id 1 subchannel-group id 2 name scg-a", result["rendered"])

    def test_epon_rendered(self):
        self.module = isam_epon_interfaces
        set_module_args(dict(config=[dict(name="1/1/1/1", polling_period=10, dba_polling0=5, admin_state="up")], state="rendered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertIn("configure epon interface 1/1/1/1 polling-period 10", result["rendered"])
        self.assertIn("configure epon interface 1/1/1/1 admin-state up", result["rendered"])

    def test_channel_pair_template_parsed(self):
        parsed = Channel_pair_pmTemplate(lines=[
            "configure channel-pair interface 1/1/1/1 fec-tc-layer pm-collect enable",
            "configure channel-pair interface 1/1/1/1 xg-tc-layer pm-collect disable",
        ]).parse()
        self.assertEqual(parsed["1/1/1/1"]["name"], "1/1/1/1")

    def test_epon_template_normalizes_dba_fields(self):
        parsed = Epon_interfacesTemplate(lines=[
            "configure epon interface 1/1/1/1 polling-period 10",
            "configure epon interface 1/1/1/1 dba-polling0 5",
            "configure epon interface 1/1/1/1 admin-state up",
        ]).parse()
        self.assertEqual(parsed["1/1/1/1"]["polling_period"], 10)
        self.assertEqual(parsed["1/1/1/1"]["dba_polling0"], 5)
        self.assertEqual(parsed["1/1/1/1"]["admin_state"], "up")

    def test_ngpon2_template_does_not_parse_epon_commands(self):
        parsed = Ngpon2_channel_groupsTemplate(lines=[
            "configure epon interface 1/1/1/1 polling-period 10",
            "configure channel-group id 1 name group-a",
            "configure channel-group id 1 channel-pair 1/1/1/1",
        ]).parse()
        self.assertEqual(parsed[1]["name"], "group-a")
        self.assertEqual(parsed[1]["channel_pairs"], ["1/1/1/1"])

    def test_optional_family_invalid_token_is_empty(self):
        self.module = isam_epon_interfaces
        self.connection.return_value.get.side_effect = Exception(
            "invalid token: epon is not installed"
        )
        self.variant_connection.return_value = self.connection.return_value
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [])

    def test_optional_family_connection_errors_are_not_hidden(self):
        connection = self.connection.return_value
        connection.get.side_effect = RuntimeError("authentication failed")
        self.variant_connection.return_value = connection
        with self.assertRaises(RuntimeError):
            pon_variants._VariantFacts("epon_interfaces", object()).get_facts()
