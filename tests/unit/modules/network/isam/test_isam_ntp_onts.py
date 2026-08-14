from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_ntp_onts
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamNtpOntsModule(TestIsamModule):
    module = isam_ntp_onts

    def setUp(self):
        super(TestIsamNtpOntsModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ntp_onts.ntp_onts.Ntp_ontsFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def tearDown(self):
        super(TestIsamNtpOntsModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()

    def test_isam_ntp_onts_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        ont_id="1/1/1",
                        client_state="on",
                        config_mode="manual",
                        server1_ip_addr="10.0.0.1",
                        oper_mode="unicast",
                        key_identifier=7,
                        key="secret",
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("configure ntp ont 1/1/1 client-state on", result["rendered"])
        self.assertIn("configure ntp ont 1/1/1 config-mode manual", result["rendered"])
        self.assertIn("configure ntp ont 1/1/1 server1-ip-addr 10.0.0.1", result["rendered"])
        self.assertIn("configure ntp ont 1/1/1 oper-mode unicast", result["rendered"])
        self.assertIn("configure ntp ont 1/1/1 key-identifier 7", result["rendered"])
        self.assertIn("configure ntp ont 1/1/1 key secret", result["rendered"])

    def test_isam_ntp_onts_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    configure ntp
                      ont 1/1/1
                        client-state on
                        config-mode manual
                        server1-ip-addr 10.0.0.1
                        oper-mode unicast
                        key-identifier 7
                        key secret
                      exit
                    exit
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["ont_id"], "1/1/1")
        self.assertEqual(result["parsed"][0]["client_state"], "on")
        self.assertEqual(result["parsed"][0]["config_mode"], "manual")
        self.assertEqual(result["parsed"][0]["server1_ip_addr"], "10.0.0.1")
        self.assertEqual(result["parsed"][0]["oper_mode"], "unicast")
        self.assertEqual(result["parsed"][0]["key_identifier"], 7)
        self.assertEqual(result["parsed"][0]["key"], "secret")

    def test_isam_ntp_onts_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure ntp
              ont 1/1/1
                client-state on
                config-mode manual
                server1-ip-addr 10.0.0.1
                oper-mode unicast
                key-identifier 7
                key secret
              exit
            exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"][0]["ont_id"], "1/1/1")
        self.assertEqual(result["gathered"][0]["client_state"], "on")
        self.assertEqual(result["gathered"][0]["config_mode"], "manual")
        self.assertEqual(result["gathered"][0]["server1_ip_addr"], "10.0.0.1")
        self.assertEqual(result["gathered"][0]["oper_mode"], "unicast")
        self.assertEqual(result["gathered"][0]["key_identifier"], 7)
        self.assertEqual(result["gathered"][0]["key"], "secret")
