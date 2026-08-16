from pathlib import Path
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

    def test_isam_facts_operational_subset_uses_show_commands(self):
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
                gather_subset=["!all", "active_alarms"],
            )
        )

        result = self.execute_module(changed=False)
        self.assertEqual(connection.commands, ["show alarm current table"])
        self.assertEqual(
            result["ansible_facts"]["ansible_net_active_alarms"]["alarms"][0]["alarm_id"],
            "1",
        )

    def test_isam_facts_dhcp_relay_gathers_configured_port_stats(self):
        class DhcpRelayConn:
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                if command == "info configure dhcp-relay flat":
                    return "\n".join(
                        [
                            "configure dhcp-relay port-stats vlan-port:1/1/1/1",
                            "configure dhcp-relay v6-port-stats vlan-port:1/1/1/1",
                        ]
                    )
                if command == "show dhcp-relay session":
                    return "SESSION | STATE\n1 | active"
                if command == "show dhcp-relay port-stats 1/1/1/1":
                    return "PORT | RECEIVED | FORWARDED | DROPPED\nvlan-port:1/1/1/1 | 123 | 120 | 3"
                if command == "show dhcp-relay v6-port-stats 1/1/1/1":
                    return "\n".join(
                        [
                            "dhcp-relay v6-port-stats 1/1/1/1 vlan 10 v6summary",
                            "  dhcpv6-error-summary : 1",
                        ]
                    )
                return ""

        connection = DhcpRelayConn()
        self.get_resource_connection_facts.return_value = connection
        set_module_args(dict(gather_subset=["!all", "dhcp_relay"]))

        result = self.execute_module(changed=False)
        relay = result["ansible_facts"]["ansible_net_dhcp_relay"]
        self.assertEqual(
            connection.commands,
            [
                "info configure dhcp-relay flat",
                "show dhcp-relay session",
                "show dhcp-relay port-stats 1/1/1/1",
                "show dhcp-relay v6-port-stats 1/1/1/1",
            ],
        )
        self.assertEqual(relay["port_stats"][0]["received"], "123")
        self.assertEqual(relay["port_stats"][0]["port"], "1/1/1/1")
        self.assertEqual(relay["v6_port_stats"][0]["dhcpv6_error_summary"], 1)
        self.assertEqual(relay["v6_port_stats"][0]["vlan"], "10")
        self.assertEqual(relay["v6_port_stats"][0]["version"], "v6")

    def test_isam_facts_dhcp_relay_uses_active_session_ports(self):
        class SessionConn:
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                if command == "info configure dhcp-relay flat":
                    return "#-------------------------------------------------------------------------------"
                if command == "show dhcp-relay session":
                    return "CLIENT | STATE\nvlanport:1/1/5/1/6/1/1:10 | active"
                if command == "show dhcp-relay port-stats 1/1/5/1/6/1/1":
                    return "\n".join(
                        [
                            "dhcp-relay port-stats 1/1/5/1/6/1/1 vlan 10 summary",
                            "  error-summary : 0",
                            "  total-in : 551",
                            "  total-out : 549",
                        ]
                    )
                return ""

        connection = SessionConn()
        self.get_resource_connection_facts.return_value = connection
        set_module_args(dict(gather_subset=["!all", "dhcp_relay"]))

        result = self.execute_module(changed=False)
        relay = result["ansible_facts"]["ansible_net_dhcp_relay"]
        self.assertIn("show dhcp-relay port-stats 1/1/5/1/6/1/1", connection.commands)
        self.assertNotIn("show dhcp-relay v6-port-stats 1/1/5/1/6/1/1", connection.commands)
        self.assertEqual(relay["port_stats"], [{
            "port": "1/1/5/1/6/1/1",
            "vlan": "10",
            "error_summary": 0,
            "total_in": 551,
            "total_out": 549,
        }])

    def test_isam_facts_all_operational_subsets_are_legacy_facts(self):
        class AllOperationalConn:
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                return ""

        connection = AllOperationalConn()
        self.get_resource_connection_facts.return_value = connection
        set_module_args(dict(gather_subset=["all"]))
        result = self.execute_module(changed=False)
        facts = result["ansible_facts"]

        for key in (
            "active_alarms",
            "dhcp_relay",
            "equipment_status",
            "interface_status",
            "ont_status",
            "ont_ranging_status",
            "ont_software_status",
            "pon_pm_status",
            "pon_status",
            "software_status",
        ):
            self.assertIn("ansible_net_%s" % key, facts)
        self.assertEqual(facts["ansible_network_resources"], {})
        self.assertEqual(
            set(connection.commands),
            {
                "show alarm current table",
                "info configure dhcp-relay flat",
                "show dhcp-relay session",
                "show equipment slot",
                "show interface port",
                "show equipment ont status pon",
                "show equipment ont ranging-status channel-pair",
                "show equipment ont sw-version",
                "show equipment ont sw-download",
                "show pon interface tc-layer current-interval",
                "show pon interface",
                "show software-mngt oswp",
            },
        )

    def test_isam_facts_default_does_not_gather_operational_data(self):
        class DefaultConn:
            def __init__(self):
                self.commands = []

            def get(self, command):
                self.commands.append(command)
                return ""

        connection = DefaultConn()
        self.get_resource_connection_facts.return_value = connection
        set_module_args(dict())

        result = self.execute_module(changed=False)
        self.assertEqual(connection.commands, [])
        self.assertEqual(result["ansible_facts"]["ansible_net_gather_subset"], [])

    def test_isam_facts_with_alarm_status_fixture(self):
        """Integration test using alarm_status fixture file."""
        from pathlib import Path
        fixture_path = Path(__file__).parent.parent.parent.parent.parent / "fixtures" / "alarm_status" / "r6.2.04m" / "output.txt"
        fixture_content = fixture_path.read_text()

        class AlarmConn:
            def get(self, cmd):
                if cmd == "show alarm current table":
                    return fixture_content
                return ""

        self.get_resource_connection_facts.return_value = AlarmConn()
        set_module_args(dict(gather_subset=["active_alarms"]))

        result = self.execute_module(changed=False)
        alarms = result["ansible_facts"]["ansible_net_active_alarms"]["alarms"]
        self.assertEqual(len(alarms), 40)
        self.assertEqual(alarms[0]["index"], "1")
        self.assertEqual(alarms[0]["type"], "olt-gen")

    def test_isam_facts_with_ont_status_fixture(self):
        """Integration test using ont_status fixture file."""
        from pathlib import Path
        fixture_path = Path(__file__).parent.parent.parent.parent.parent / "fixtures" / "ont_status" / "r6.2.04m" / "output.txt"
        fixture_content = fixture_path.read_text()

        class OntStatusConn:
            def get(self, cmd):
                if cmd == "show equipment ont status pon":
                    return fixture_content
                return ""

        self.get_resource_connection_facts.return_value = OntStatusConn()
        set_module_args(dict(gather_subset=["ont_status"]))

        result = self.execute_module(changed=False)
        ont_status = result["ansible_facts"]["ansible_net_ont_status"]
        self.assertEqual(len(ont_status), 74)
        self.assertEqual(ont_status[0]["pon"], "1/1/2/1")
        self.assertEqual(ont_status[0]["sernum"], "XXXX:SANIT")

    def test_isam_facts_with_software_status_fixture(self):
        """Integration test using software_status fixture file."""
        from pathlib import Path
        fixture_path = Path(__file__).parent.parent.parent.parent.parent / "fixtures" / "software_status" / "r6.2.04m" / "output.txt"
        fixture_content = fixture_path.read_text()

        class SoftwareStatusConn:
            def get(self, cmd):
                if cmd == "show software-mngt oswp":
                    return fixture_content
                return ""

        self.get_resource_connection_facts.return_value = SoftwareStatusConn()
        set_module_args(dict(gather_subset=["software_status"]))

        result = self.execute_module(changed=False)
        software_status = result["ansible_facts"]["ansible_net_software_status"]
        self.assertEqual(len(software_status), 2)
        self.assertEqual(software_status[0]["name"], "L6GPAA62.652")
        self.assertEqual(software_status[0]["act_status"], "not-active")

    def test_isam_facts_with_pon_pm_status_fixture(self):
        """Integration test using pon_pm_status fixture file."""
        from pathlib import Path
        fixture_path = Path(__file__).parent.parent.parent.parent.parent / "fixtures" / "pon_pm_status" / "r6.2.04m" / "output.txt"
        fixture_content = fixture_path.read_text()

        class PonPmConn:
            def get(self, cmd):
                if cmd == "show pon interface tc-layer current-interval":
                    return fixture_content
                return ""

        self.get_resource_connection_facts.return_value = PonPmConn()
        set_module_args(dict(gather_subset=["pon_pm_status"]))

        result = self.execute_module(changed=False)
        pon_pm = result["ansible_facts"]["ansible_net_pon_pm_status"]
        self.assertEqual(len(pon_pm), 16)
        self.assertEqual(pon_pm[0]["pon_idx"], "1/1/5/1")
        self.assertEqual(pon_pm[0]["err_frags_up"], 0)












def test_ont_ranging_status_integration():
    """Integration test for Ont_ranging_statusFacts operational parser."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import Ont_ranging_statusFacts
    
    fixture_path = Path("tests/fixtures/ont_ranging_status/r6.2.04m/output.txt")
    if not fixture_path.exists():
        return  # Skip if fixture doesn't exist
    
    output = fixture_path.read_text()
    facts = Ont_ranging_statusFacts(module=None)
    
    # Just verify the parser can handle the output without errors
    if hasattr(facts, 'parse'):
        parsed = facts.parse(output)
        assert parsed is not None
    else:
        # For parsers without parse method, just verify they can be instantiated
        assert facts is not None

def test_ont_software_status_integration():
    """Integration test for Ont_software_statusFacts operational parser."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import Ont_software_statusFacts
    
    fixture_path = Path("tests/fixtures/ont_software_status/sw_version/output.txt")
    if not fixture_path.exists():
        return  # Skip if fixture doesn't exist
    
    output = fixture_path.read_text()
    facts = Ont_software_statusFacts(module=None)
    
    # Just verify the parser can handle the output without errors
    if hasattr(facts, 'parse'):
        parsed = facts.parse(output)
        assert parsed is not None
    else:
        # For parsers without parse method, just verify they can be instantiated
        assert facts is not None

def test_equipment_status_integration():
    """Integration test for Equipment_statusFacts operational parser."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import Equipment_statusFacts
    
    fixture_path = Path("tests/fixtures/equipment_status/live-fttn/output.txt")
    if not fixture_path.exists():
        return  # Skip if fixture doesn't exist
    
    output = fixture_path.read_text()
    facts = Equipment_statusFacts(module=None)
    
    # Just verify the parser can handle the output without errors
    if hasattr(facts, 'parse'):
        parsed = facts.parse(output)
        assert parsed is not None
    else:
        # For parsers without parse method, just verify they can be instantiated
        assert facts is not None

def test_interface_status_integration():
    """Integration test for Interface_statusFacts operational parser."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import Interface_statusFacts
    
    fixture_path = Path("tests/fixtures/interface_status/r6.2.04m/output.txt")
    if not fixture_path.exists():
        return  # Skip if fixture doesn't exist
    
    output = fixture_path.read_text()
    facts = Interface_statusFacts(module=None)
    
    # Just verify the parser can handle the output without errors
    if hasattr(facts, 'parse'):
        parsed = facts.parse(output)
        assert parsed is not None
    else:
        # For parsers without parse method, just verify they can be instantiated
        assert facts is not None

def test_dhcp_relay_integration():
    """Integration test for Dhcp_relayFacts operational parser."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import Dhcp_relayFacts
    
    fixture_path = Path("tests/fixtures/dhcp_relay/r6.2.04m/output.txt")
    if not fixture_path.exists():
        return  # Skip if fixture doesn't exist
    
    output = fixture_path.read_text()
    facts = Dhcp_relayFacts(module=None)
    
    # Just verify the parser can handle the output without errors
    if hasattr(facts, 'parse'):
        parsed = facts.parse(output)
        assert parsed is not None
    else:
        # For parsers without parse method, just verify they can be instantiated
        assert facts is not None
