from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_dhcp_relay
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamDhcpRelayModule(TestIsamModule):
    module = isam_dhcp_relay

    def setUp(self):
        super(TestIsamDhcpRelayModule, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dhcp_relay.dhcp_relay.Isam_dhcp_relayFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def tearDown(self):
        super(TestIsamDhcpRelayModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()

    def test_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=[dict(name="vlan-port:1/1/1/1", port_stats=True, v6_port_stats=False)],
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure dhcp-relay port-stats vlan-port:1/1/1/1"],
        )

    def test_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure dhcp-relay port-stats vlan-port:1/1/1/1
                    configure dhcp-relay v6-port-stats vlan-port:1/1/1/1
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [dict(name="vlan-port:1/1/1/1", port_stats=True, v6_port_stats=True)])

    def test_gathered_hierarchical_config(self):
        self.get_config.return_value = dedent(
            """\
            configure dhcp-relay
              port-stats vlan-port:1/1/1/1
              v6-port-stats vlan-port:1/1/1/1
            exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [dict(name="vlan-port:1/1/1/1", port_stats=True, v6_port_stats=True)])

    def test_merged_check_mode(self):
        self.get_config.return_value = "configure dhcp-relay port-stats vlan-port:1/1/1/1"
        set_module_args(
            dict(
                state="merged",
                config=[dict(name="vlan-port:1/1/1/1", port_stats=True, v6_port_stats=True)],
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure dhcp-relay v6-port-stats vlan-port:1/1/1/1"])
