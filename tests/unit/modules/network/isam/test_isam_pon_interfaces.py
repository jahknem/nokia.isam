from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_pon_interfaces
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamPonInterfacesModule(TestIsamModule):
    module = isam_pon_interfaces

    def setUp(self):
        super(TestIsamPonInterfacesModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces.Pon_interfacesFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def tearDown(self):
        super(TestIsamPonInterfacesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()

    def test_isam_pon_interfaces_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/1/1",
                        label="access-pon-1",
                        fec_dn="enable",
                        ponid_interval=10,
                        ponid_identifier="00000000000001",
                        tconts_per_frame=44,
                        admin_state="down",
                        tc_layer=dict(pm_collect="tca-enable"),
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("configure pon interface 1/1/1/1 label access-pon-1", result["rendered"])
        self.assertIn("configure pon interface 1/1/1/1 tc-layer pm-collect tca-enable", result["rendered"])

    def test_isam_pon_interfaces_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    configure pon
                      interface 1/1/1/1
                        label access-pon-1
                        fec-dn enable
                        ponid-interval 10
                        ponid-identifier 00000000000001
                        tconts-per-frame 44
                        admin-state down
                        tc-layer
                          pm-collect tca-enable
                        exit
                      exit
                    exit
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["name"], "1/1/1/1")
        self.assertEqual(result["parsed"][0]["tc_layer"]["pm_collect"], "tca-enable")

    def test_isam_pon_interfaces_parses_packed_detail_fields(self):
        set_module_args(
            dict(
                running_config=(
                    "configure pon interface 1/1/5/1 label 5/1 no ber-calc-period "
                    "no polling-period no sig-degrade-th no sig-fail-th fec-dn enable "
                    "no raman-reduct no closest-ont no diff-reach no pon-tag no pon-id "
                    "no mcast-encrypt no auth-method ponid-interval 1 no ponid-odn "
                    "ponid-identifier cccccc5a1ccccc no max-ranging-onts "
                    "tconts-per-frame 64 no pon-speed no burst-overhead no onu-prov-mode"
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        entry = result["parsed"][0]
        self.assertEqual(entry["label"], "5/1")
        self.assertEqual(entry["fec_dn"], "enable")
        self.assertEqual(entry["ponid_interval"], 1)
        self.assertEqual(entry["ponid_identifier"], "cccccc5a1ccccc")
        self.assertEqual(entry["tconts_per_frame"], 64)

        self.assertEqual(entry["ber_calc_period"], 10)
        self.assertEqual(entry["polling_period"], 100)
        self.assertEqual(entry["raman_reduct"], "disable")
        self.assertEqual(entry["closest_ont"], 0)
        self.assertEqual(entry["diff_reach"], 20)
        self.assertEqual(entry["pon_tag"], "0000000000000000")
        self.assertEqual(entry["pon_id"], "00000000")
        self.assertEqual(entry["auth_method"], "sn-slid")
        self.assertEqual(entry["ponid_odn"], "auto")
        self.assertEqual(entry["max_ranging_onts"], 128)
        self.assertEqual(entry["pon_speed"], "nominal")
        self.assertEqual(entry["burst_overhead"], "robust")
        self.assertEqual(entry["onu_prov_mode"], "semi-auto")

    def test_isam_pon_interfaces_renders_documented_fields(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/5/1",
                        ponid_odn="auto",
                        pon_speed="10g-10g",
                        burst_overhead="robust",
                        onu_prov_mode="auto",
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        rendered = result["rendered"]
        self.assertIn("configure pon interface 1/1/5/1 ponid-odn auto", rendered)
        self.assertIn("configure pon interface 1/1/5/1 pon-speed 10g-10g", rendered)
        self.assertIn("configure pon interface 1/1/5/1 burst-overhead robust", rendered)
        self.assertIn("configure pon interface 1/1/5/1 onu-prov-mode auto", rendered)

    def test_isam_pon_interfaces_renders_documented_nested_subtrees(self):
        set_module_args(
            dict(
                config=[
                    {
                        "name": "x-pon:1/1/1/1",
                        "tc_layer_threshold": {"error_frags_up": "disabled"},
                        "mcast_tc_layer": {"pm_collect": "enable"},
                        "otdr": {"mode": "disable"},
                        "utilization": {
                            "pon_pmcollect": "inherit",
                            "threshold": {"txmcutilhi": "90"},
                        },
                        "deact_ont_tca": {
                            "mode": "percent",
                            "monitor_interval": 30,
                            "threshold_percent": {"high": 90},
                        },
                    }
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        rendered = self.execute_module(changed=False)["rendered"]
        for command in (
            "tc-layer-threshold error-frags-up disabled",
            "mcast-tc-layer pm-collect enable",
            "otdr mode disable",
            "utilization pon-pmcollect inherit",
            "utilization threshold txmcutilhi 90",
            "deact-ont-tca mode percent",
            "deact-ont-tca monitor-interval 30",
            "deact-ont-tca threshold-percent high 90",
        ):
            self.assertIn("configure pon interface x-pon:1/1/1/1 " + command, rendered)

    def test_isam_pon_interfaces_parses_nested_packed_detail_fields(self):
        set_module_args(
            dict(
                running_config=(
                    "configure pon interface 1/1/5/1 tc-layer-threshold error-frags-up 10 "
                    "mcast-tc-layer pm-collect enable otdr mode disable "
                    "utilization pon-pmcollect inherit "
                    "\nconfigure pon interface 1/1/5/1 utilization threshold txmcutilhi 90 "
                    "deact-ont-tca mode percent monitor-interval 30"
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        entry = self.execute_module(changed=False)["parsed"][0]
        self.assertEqual(entry["tc_layer_threshold"]["error_frags_up"], "10")
        self.assertEqual(entry["mcast_tc_layer"]["pm_collect"], "enable")
        self.assertEqual(entry["otdr"]["mode"], "disable")
        self.assertEqual(entry["utilization"]["pon_pmcollect"], "inherit")
        self.assertEqual(entry["utilization"]["threshold"]["txmcutilhi"], "90")
        self.assertEqual(entry["deact_ont_tca"]["monitor_interval"], 30)

    def test_isam_pon_interfaces_temporarily_disables_restricted_changes(self):
        self.get_config.return_value = (
            "configure pon interface 1/1/1/1 fec-dn enable admin-state up"
        )
        set_module_args(
            dict(
                state="merged",
                config=[{"name": "1/1/1/1", "fec_dn": "disable", "admin_state": "up"}],
            ),
            ignore_provider_arg,
        )
        commands = self.execute_module(changed=True)["commands"]
        self.assertEqual(
            commands,
            [
                "configure pon interface 1/1/1/1 admin-state down",
                "configure pon interface 1/1/1/1 fec-dn disable",
                "configure pon interface 1/1/1/1 admin-state up",
            ],
        )

    def _set_pon_have(self):
        self.get_config.return_value = dedent(
            """\
            configure pon interface 1/1/1/1 label access-pon-1 fec-dn enable ponid-interval 10 admin-state up
            configure pon interface 1/1/1/2 label access-pon-2 fec-dn disable ponid-interval 20 admin-state up
            """
        )

    def test_isam_pon_interfaces_state_sibling_isolation(self):
        self._set_pon_have()
        set_module_args(
            dict(state="merged", config=[{"name": "1/1/1/1", "ponid_interval": 11}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure pon interface 1/1/1/1 ponid-interval 11", result["commands"])
        self.assertFalse(any("1/1/1/2" in command for command in result["commands"]))

        set_module_args(
            dict(state="replaced", config=[{"name": "1/1/1/1", "label": "new-label"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure pon interface 1/1/1/1 label new-label", result["commands"])
        self.assertTrue(any("no fec-dn" in command for command in result["commands"]))
        self.assertFalse(any("1/1/1/2" in command for command in result["commands"]))

        set_module_args(
            dict(state="overridden", config=[{"name": "1/1/1/1", "label": "new-label"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertTrue(any("1/1/1/2" in command for command in result["commands"]))

        set_module_args(
            dict(state="deleted", config=[{"name": "1/1/1/1"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
        self.assertFalse(any("1/1/1/2" in command for command in result["commands"]))
