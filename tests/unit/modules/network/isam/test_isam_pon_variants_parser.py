"""The PON variant modules and isam_facts share one parser, typed per argspec."""
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from ansible_collections.nokia.isam.plugins.modules import isam_channel_pair_pm, isam_epon_interfaces, isam_ngpon2_channel_groups
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_variants.pon_variants import (
    Channel_pair_pmFacts,
    Epon_interfacesFacts,
    Ngpon2_channel_groupsFacts,
)
from .isam_module import TestIsamModule, set_module_args

EPON = (
    "configure epon interface 1/1/1/1 polling-period 10\n"
    "configure epon interface 1/1/1/1 dba-polling0 5\n"
    "configure epon interface 1/1/1/1 admin-state up\n"
)
NGPON2 = (
    "configure channel-group id 1 name group-a\n"
    "configure channel-group id 1 polling-period 10\n"
    "configure channel-group id 1 channel-pair 1/1/1/1\n"
    "configure channel-group id 1 subchannel-group id 2 closest-ont 3\n"
    "configure channel-group id 1 subchannel-group id 2 diff-reach 20\n"
    "configure channel-group id 1 subchannel-group id 2 fec-dn enable\n"
)
CHANNEL_PAIR = "configure channel-pair interface 1/1/1/1 fec-tc-layer pm-collect enable\n"


class TestPonVariantsParser(TestIsamModule):
    def facts(self, cls, resource, data):
        return cls(module=None).populate_facts(None, {"ansible_network_resources": {}}, data=data)["ansible_network_resources"][resource]

    def module_view(self, module, data, state="parsed"):
        self.module = module
        if state == "parsed":
            set_module_args({"state": "parsed", "running_config": data}, True)
            return self.execute_module()["parsed"]
        device = type("Device", (), {"get": lambda self, command, *a, **kw: data})()
        with patch("ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants.get_resource_connection",
                   return_value=device):
            set_module_args({"state": "gathered"}, True)
            return self.execute_module()["gathered"]

    def test_epon_ints_are_typed_like_isam_facts(self):
        expected = [{"name": "1/1/1/1", "polling_period": 10, "dba_polling0": 5, "admin_state": "up"}]
        self.assertEqual(self.facts(Epon_interfacesFacts, "epon_interfaces", EPON), expected)
        for state in ("parsed", "gathered"):
            self.assertEqual(self.module_view(isam_epon_interfaces, EPON, state), expected)

    def test_ngpon2_ints_are_typed_like_isam_facts(self):
        expected = [{
            "id": 1, "name": "group-a", "polling_period": 10, "channel_pairs": ["1/1/1/1"],
            "subchannel_groups": [{"id": 2, "closest_ont": 3, "diff_reach": 20, "fec_dn": "enable"}],
        }]
        self.assertEqual(self.facts(Ngpon2_channel_groupsFacts, "ngpon2_channel_groups", NGPON2), expected)
        for state in ("parsed", "gathered"):
            self.assertEqual(self.module_view(isam_ngpon2_channel_groups, NGPON2, state), expected)

    def test_channel_pair_pm_is_unchanged(self):
        expected = [{"name": "1/1/1/1", "fec_tc_layer": "enable"}]
        self.assertEqual(self.facts(Channel_pair_pmFacts, "channel_pair_pm", CHANNEL_PAIR), expected)
        self.assertEqual(self.module_view(isam_channel_pair_pm, CHANNEL_PAIR), expected)

    def test_non_numeric_int_field_does_not_crash(self):
        self.assertEqual(self.facts(Epon_interfacesFacts, "epon_interfaces", "configure epon interface 1/1/1/1 polling-period auto\n"),
                         [{"name": "1/1/1/1", "polling_period": "auto"}])

