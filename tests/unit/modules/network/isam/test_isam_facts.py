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
