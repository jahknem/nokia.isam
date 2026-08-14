from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_lines
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamXdslLinesModule(TestIsamModule):
    module = isam_xdsl_lines

    def setUp(self):
        super(TestIsamXdslLinesModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_lines.xdsl_lines.Xdsl_linesFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamXdslLinesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()

    def test_isam_xdsl_lines_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/3/1",
                        service_profile="13",
                        spectrum_profile="2",
                        dpbo_profile="1",
                        vect_profile="10",
                        admin_up=True,
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        commands = [
            "configure xdsl line 1/1/3/1 service-profile 13",
            "configure xdsl line 1/1/3/1 spectrum-profile 2",
            "configure xdsl line 1/1/3/1 dpbo-profile 1",
            "configure xdsl line 1/1/3/1 vect-profile 10",
            "configure xdsl line 1/1/3/1 admin-up",
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(set(result["rendered"]), set(commands))

    def test_isam_xdsl_lines_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    configure xdsl
                    #-------------------------------------------------------------------------------
                    echo "xdsl"
                    #-------------------------------------------------------------------------------
                    line 1/1/3/1
                      service-profile 13
                      spectrum-profile 2
                      dpbo-profile 1
                      vect-profile 10
                      admin-up
                    exit
                    #-------------------------------------------------------------------------------
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["parsed"],
            [
                dict(
                    name="1/1/3/1",
                    service_profile="13",
                    spectrum_profile="2",
                    dpbo_profile="1",
                    vect_profile="10",
                    admin_up=True,
                )
            ],
        )

    def test_isam_xdsl_lines_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure xdsl
            #-------------------------------------------------------------------------------
            echo "xdsl"
            #-------------------------------------------------------------------------------
            line 1/1/3/1
              service-profile 13
              spectrum-profile 2
              dpbo-profile 1
              vect-profile 10
              admin-up
            exit
            line 1/1/3/16
              service-profile 13
              spectrum-profile 2
              vect-profile 10
              admin-up
            exit
            #-------------------------------------------------------------------------------
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(len(result["gathered"]), 2)
        self.assertEqual(result["gathered"][0]["name"], "1/1/3/1")
        self.assertEqual(result["gathered"][1]["name"], "1/1/3/16")
        self.assertNotIn("dpbo_profile", result["gathered"][1])

    def test_isam_xdsl_lines_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure xdsl
            #-------------------------------------------------------------------------------
            echo "xdsl"
            #-------------------------------------------------------------------------------
            line 1/1/3/1
              service-profile 13
              spectrum-profile 2
              dpbo-profile 1
              vect-profile 10
              admin-up
            exit
            #-------------------------------------------------------------------------------
            """
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/3/1",
                        service_profile="13",
                        spectrum_profile="2",
                        dpbo_profile="1",
                        vect_profile="10",
                        admin_up=True,
                    )
                ],
                state="merged",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_xdsl_lines_negative_profile_forms(self):
        set_module_args(
            dict(
                running_config=(
                    "configure xdsl line 1/1/3/1 no service-profile no spectrum-profile "
                    "no dpbo-profile no vect-profile no rtx-profile no sos-profile no admin-up"
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "1/1/3/1", "admin_up": False}])

    def test_isam_xdsl_lines_documented_mode_fields(self):
        set_module_args(
            dict(
                running_config=(
                    "configure xdsl line 1/1/3/1 carrier-data-mode on transfer-mode ptm "
                    "vect-qln-mode with-cancel vect-fallback forced ansi-t1413 "
                    "no etsi-dts no imp-noise-sensor auto-switch"
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        entry = result["parsed"][0]
        self.assertEqual(entry["carrier_data_mode"], "on")
        self.assertEqual(entry["transfer_mode"], "ptm")
        self.assertEqual(entry["vect_qln_mode"], "with-cancel")
        self.assertEqual(entry["vect_fallback"], "forced")
        self.assertTrue(entry["ansi_t1413"])
        self.assertFalse(entry["etsi_dts"])
        self.assertFalse(entry["imp_noise_sensor"])
        self.assertTrue(entry["auto_switch"])

        set_module_args(
            dict(
                state="rendered",
                config=[
                    {
                        "name": "1/1/3/1",
                        "carrier_data_mode": "on",
                        "transfer_mode": "ptm",
                        "vect_qln_mode": "with-cancel",
                        "vect_fallback": "forced",
                        "ansi_t1413": True,
                    }
                ],
            ),
            ignore_provider_arg,
        )
        rendered = self.execute_module(changed=False)["rendered"]
        self.assertIn("configure xdsl line 1/1/3/1 carrier-data-mode on", rendered)
        self.assertIn("configure xdsl line 1/1/3/1 transfer-mode ptm", rendered)
        self.assertIn("configure xdsl line 1/1/3/1 vect-qln-mode with-cancel", rendered)
        self.assertIn("configure xdsl line 1/1/3/1 vect-fallback forced", rendered)
        self.assertIn("configure xdsl line 1/1/3/1 ansi-t1413", rendered)

    def _set_xdsl_have(self):
        self.get_config.return_value = dedent(
            """\
            configure xdsl line 1/1/3/1 service-profile 13 spectrum-profile 2 dpbo-profile 1 vect-profile 10 admin-up
            configure xdsl line 1/1/3/2 service-profile 13 spectrum-profile 2 dpbo-profile 1 vect-profile 10 admin-up
            """
        )

    def test_isam_xdsl_lines_state_sibling_isolation(self):
        self._set_xdsl_have()
        set_module_args(
            dict(state="merged", config=[{"name": "1/1/3/1", "service_profile": "14"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure xdsl line 1/1/3/1 service-profile 14", result["commands"])
        self.assertFalse(any("1/1/3/2" in command for command in result["commands"]))

        set_module_args(
            dict(state="overridden", config=[{"name": "1/1/3/1", "service_profile": "13"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertTrue(any("1/1/3/2" in command for command in result["commands"]))

        set_module_args(
            dict(state="replaced", config=[{"name": "1/1/3/1", "service_profile": "14"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure xdsl line 1/1/3/1 service-profile 14", result["commands"])
        self.assertTrue(any("no spectrum-profile" in command for command in result["commands"]))
        self.assertFalse(any("1/1/3/2" in command for command in result["commands"]))

        set_module_args(
            dict(state="deleted", config=[{"name": "1/1/3/1"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertTrue(any("1/1/3/1" in command for command in result["commands"]))
        self.assertFalse(any("1/1/3/2" in command for command in result["commands"]))
