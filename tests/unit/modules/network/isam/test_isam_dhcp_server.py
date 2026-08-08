from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_dhcp_server
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamDhcpServerModule(TestIsamModule):
    module = isam_dhcp_server

    def setUp(self):
        super(TestIsamDhcpServerModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dhcp_server.dhcp_server.Isam_dhcp_serverFacts.get_config"
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
        super(TestIsamDhcpServerModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_dhcp_server_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    start_addr="192.168.1.100",
                    end_addr="192.168.1.200",
                    subnet_mask="255.255.255.0",
                    lease_time=86400,
                    restart=True,
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "configure dhcp-server start-addr 192.168.1.100",
                "configure dhcp-server stop-addr 192.168.1.200",
                "configure dhcp-server subnet-mask 255.255.255.0",
                "configure dhcp-server lease-time 86400",
                "configure dhcp-server restart",
            ],
        )

    def test_isam_dhcp_server_documented_stop_addr_and_no_lease_time(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    start_addr="192.168.1.100",
                    stop_addr="192.168.1.200",
                    lease_time_enabled=False,
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "configure dhcp-server start-addr 192.168.1.100",
                "configure dhcp-server stop-addr 192.168.1.200",
                "configure dhcp-server no lease-time",
            ],
        )

    def test_isam_dhcp_server_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure dhcp-server start-addr 192.168.1.100 stop-addr 192.168.1.200 restart
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["start_addr"], "192.168.1.100")
        self.assertEqual(result["parsed"]["end_addr"], "192.168.1.200")
        self.assertEqual(result["parsed"]["restart"], True)

    def test_isam_dhcp_server_parsed_documented_syntax(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure dhcp-server start-addr 192.168.1.100 stop-addr 192.168.1.200 no lease-time
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["end_addr"], "192.168.1.200")

    def test_isam_dhcp_server_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure dhcp-server start-addr 192.168.1.100 stop-addr 192.168.1.200 restart
            """
        )
        set_module_args(
            dict(state="gathered"),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["start_addr"], "192.168.1.100")
        self.assertEqual(result["gathered"]["end_addr"], "192.168.1.200")
        self.assertEqual(result["gathered"]["restart"], True)

    def test_isam_dhcp_server_merged(self):
        self.get_config.return_value = dedent(
            """\
            configure dhcp-server start-addr 10.0.0.1 restart
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    end_addr="10.0.0.100",
                    subnet_mask="255.255.255.0",
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure dhcp-server stop-addr 10.0.0.100", result["commands"])
        self.assertIn("configure dhcp-server subnet-mask 255.255.255.0", result["commands"])

    def test_isam_dhcp_server_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure dhcp-server start-addr 192.168.1.100 stop-addr 192.168.1.200 restart
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    start_addr="192.168.1.100",
                    end_addr="192.168.1.200",
                    restart=True,
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_dhcp_server_deleted(self):
        self.get_config.return_value = dedent(
            """\
            configure dhcp-server start-addr 192.168.1.100 stop-addr 192.168.1.200 restart
            """
        )
        set_module_args(
            dict(
                state="deleted",
                config=dict(),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("no configure dhcp-server start-addr", result["commands"])
        self.assertIn("no configure dhcp-server stop-addr", result["commands"])
        self.assertIn("no configure dhcp-server restart", result["commands"])
