from ansible_collections.nokia.isam.plugins.modules import isam_facts
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIsamFactsModule(TestIsamModule):
    module = isam_facts

    def setUp(self):
        super(TestIsamFactsModule, self).setUp()
        # Patch the resource connection used by facts to avoid real device calls
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        class FakeConn:
            def get(self, cmd):
                # Return empty outputs for any resource request
                return ""

        self.fake_conn = FakeConn()
        self.get_resource_connection_facts.return_value = self.fake_conn

    def tearDown(self):
        super(TestIsamFactsModule, self).tearDown()
        self.get_resource_connection_facts.stop()

    def test_isam_facts_minimal_interfaces(self):
        # Gather only interfaces to keep scope small and deterministic
        set_module_args(
            dict(
                gather_network_resources=["interfaces"],
            )
        )

        result = self.execute_module(changed=False)
        self.assertIn("ansible_facts", result)
        af = result["ansible_facts"]
        self.assertIn("ansible_network_resources", af)
        anr = af["ansible_network_resources"]
        # interfaces key should be present and a list (empty due to fake conn)
        self.assertIn("interfaces", anr)
        self.assertIsInstance(anr["interfaces"], list)
        self.assertEqual(anr["interfaces"], [])

    def test_isam_facts_bridges_port_vlan(self):
        class BridgeConn:
            def get(self, cmd):
                if cmd == "info configure bridge flat":
                    return "\n".join(
                        [
                            "configure bridge ageing-time 400",
                            "configure bridge port 1/1/2/1 pvid 99",
                            "configure bridge port 1/1/2/1 vlan-id 99 tag single-tagged",
                        ]
                    )
                return ""

        self.get_resource_connection_facts.return_value = BridgeConn()

        set_module_args(dict(gather_network_resources=["bridges"]))
        result = self.execute_module(changed=False)
        bridges = result["ansible_facts"]["ansible_network_resources"]["bridges"]

        self.assertEqual(bridges.get("ageing_time"), 400)
        self.assertTrue(bridges.get("port"))
        self.assertEqual(bridges["port"][0].get("port"), "1/1/2/1")

    def test_isam_facts_interfaces_keys_are_canonical(self):
        class InterfaceConn:
            def get(self, cmd):
                if cmd == "info configure interface port flat":
                    return "\n".join(
                        [
                            "configure interface port uni:1/1/1/1 admin-up",
                            "configure interface port uni:1/1/1/1 link-updown-trap",
                            "configure interface port uni:1/1/1/1 port-type nni",
                            "configure interface port uni:1/1/1/1 user test-user",
                        ]
                    )
                return ""

        self.get_resource_connection_facts.return_value = InterfaceConn()

        set_module_args(dict(gather_network_resources=["interfaces"]))
        result = self.execute_module(changed=False)
        interfaces = result["ansible_facts"]["ansible_network_resources"]["interfaces"]

        self.assertTrue(interfaces)
        interface = interfaces[0]
        self.assertIn("name", interface)
        self.assertIn("admin_up", interface)
        self.assertIn("link_updown_trap", interface)
        self.assertIn("port_type", interface)
        self.assertNotIn("id", interface)
        self.assertNotIn("admin-up", interface)
        self.assertNotIn("link-updown-trap", interface)
        self.assertNotIn("port-type", interface)

    def test_isam_facts_reuses_one_configuration_for_selected_resources(self):
        class ConfigurationConn:
            def __init__(self):
                self.commands = []

            def get(self, cmd):
                self.commands.append(cmd)
                return "\n".join(
                    [
                        "configure interface port pon:1/1/5/1 admin-up",
                        "configure pon interface 1/1/5/1 admin-state up",
                        "configure equipment ont interface 1/1/5/1/100 sernum TMBB:00000000",
                    ]
                )

        connection = ConfigurationConn()
        self.get_resource_connection_facts.return_value = connection
        set_module_args(
            dict(
                gather_configuration=True,
                gather_network_resources=["interfaces", "pon_interfaces", "equipment_onts"],
            )
        )

        result = self.execute_module(changed=False)
        resources = result["ansible_facts"]["ansible_network_resources"]

        self.assertEqual(connection.commands, ["info configure flat"])
        self.assertEqual(resources["interfaces"][0]["name"], "pon:1/1/5/1")
        self.assertEqual(resources["pon_interfaces"][0]["name"], "1/1/5/1")
        self.assertEqual(resources["equipment_onts"]["interfaces"][0]["ont_idx"], "1/1/5/1/100")

    def test_isam_facts_warns_for_unmatched_owned_configuration(self):
        class ConfigurationConn:
            def get(self, cmd):
                return "\n".join(
                    [
                        "configure interface port pon:1/1/5/1 admin-up",
                        "configure interface port pon:1/1/5/1 unsupported-option",
                    ]
                )

        self.get_resource_connection_facts.return_value = ConfigurationConn()
        set_module_args(
            dict(
                gather_configuration=True,
                gather_network_resources=["interfaces"],
            )
        )

        result = self.execute_module(changed=False)
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn(
            "configure interface port pon:1/1/5/1 unsupported-option",
            result["warnings"][0],
        )
        self.assertNotIn("unsupported-option", str(result["ansible_facts"]))

    def test_isam_facts_warns_for_unmatched_custom_parser_configuration(self):
        class ConfigurationConn:
            def get(self, cmd):
                return "\n".join(
                    [
                        "configure qos profiles unsupported-command value",
                        "configure qos profiles queue FD_BEQ red:24:48:80",
                    ]
                )

        self.get_resource_connection_facts.return_value = ConfigurationConn()
        set_module_args(
            dict(
                gather_configuration=True,
                gather_network_resources=["qos_profiles"],
            )
        )

        result = self.execute_module(changed=False)
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn(
            "configure qos profiles unsupported-command value",
            result["warnings"][0],
        )

    def test_isam_facts_keeps_selected_multicast_aliases(self):
        class ConfigurationConn:
            def get(self, cmd):
                return "\n".join(
                    [
                        "configure igmp mcast-svc-context default",
                        "configure mcast-control admin-state enable",
                    ]
                )

        self.get_resource_connection_facts.return_value = ConfigurationConn()
        set_module_args(
            dict(
                gather_configuration=True,
                gather_network_resources=["multicast", "igmp", "mcast_control"],
            )
        )

        result = self.execute_module(changed=False)
        resources = result["ansible_facts"]["ansible_network_resources"]

        self.assertEqual(set(resources), {"multicast", "igmp", "mcast_control"})
        self.assertTrue(resources["multicast"])
        self.assertTrue(resources["igmp"])
        self.assertTrue(resources["mcast_control"])

    def test_isam_facts_keeps_explicit_dhcp_alias(self):
        class ConfigurationConn:
            def get(self, cmd):
                return "configure dhcp-server start-addr 192.0.2.10"

        self.get_resource_connection_facts.return_value = ConfigurationConn()
        set_module_args(
            dict(
                gather_configuration=True,
                gather_network_resources=["dhcp_server", "isam_dhcp_server"],
            )
        )

        result = self.execute_module(changed=False)
        resources = result["ansible_facts"]["ansible_network_resources"]

        self.assertEqual(set(resources), {"dhcp_server", "isam_dhcp_server"})
        self.assertEqual(resources["dhcp_server"], resources["isam_dhcp_server"])

    def test_isam_facts_all_uses_canonical_alias_resources(self):
        class ConfigurationConn:
            def get(self, cmd):
                return "\n".join(
                    [
                        "configure igmp mcast-svc-context default",
                        "configure mcast-control admin-state enable",
                        "configure dhcp-server start-addr 192.0.2.10",
                    ]
                )

        self.get_resource_connection_facts.return_value = ConfigurationConn()
        set_module_args(dict(gather_configuration=True, gather_network_resources=["all"]))

        result = self.execute_module(changed=False)
        resources = result["ansible_facts"]["ansible_network_resources"]

        self.assertIn("multicast", resources)
        self.assertNotIn("igmp", resources)
        self.assertNotIn("mcast_control", resources)
        self.assertIn("dhcp_server", resources)
        self.assertNotIn("isam_dhcp_server", resources)

    def test_isam_facts_operational_resources_use_show_commands(self):
        class OperationalConn:
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                if command == "show alarm current table":
                    return "ALARM  SEVERITY  SOURCE  DESCRIPTION\n1  major  shelf-1  Test alarm"
                return ""

        connection = OperationalConn()
        self.get_resource_connection_facts.return_value = connection
        set_module_args(
            dict(
                gather_configuration=True,
                gather_network_resources=["active_alarms"],
            )
        )

        result = self.execute_module(changed=False)
        self.assertEqual(connection.commands, ["show alarm current table"])
        self.assertEqual(
            result["ansible_facts"]["ansible_network_resources"]["active_alarms"]["alarms"][0]["alarm_id"],
            "1",
        )
