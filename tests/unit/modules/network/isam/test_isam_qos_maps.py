from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_qos_maps
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamQosMapsModule(TestIsamModule):
    module = isam_qos_maps

    def setUp(self):
        super(TestIsamQosMapsModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamQosMapsModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_qos_maps_parsed(self):
        running = dedent(
            """
            configure qos
            tc-map-dot1p 0 tc 0
            tc-map-dot1p 7 tc 7
            dscp-map-dot1p CS0 dot1p 0
            dscp-map-dot1p EF dot1p 5
            up-ctrl-pkt dhcp queue 0 profile default
            up-ctrl-pkt arp queue 0
            dn-ctrl-pkt dhcp queue 0 profile default
            dn-ctrl-pkt arp queue 0
            exit
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        parsed = result.get("parsed", {})

        tc_map = parsed.get("tc_map_dot1p", [])
        self.assertEqual(len(tc_map), 2)
        self.assertEqual(tc_map[0]["dot1p"], 0)
        self.assertEqual(tc_map[0]["tc"], 0)
        self.assertEqual(tc_map[1]["dot1p"], 7)
        self.assertEqual(tc_map[1]["tc"], 7)

        dscp_map = parsed.get("dscp_map_dot1p", [])
        self.assertEqual(len(dscp_map), 2)
        self.assertEqual(dscp_map[0]["dscp"], "CS0")
        self.assertEqual(dscp_map[0]["dot1p"], 0)
        self.assertEqual(dscp_map[1]["dscp"], "EF")
        self.assertEqual(dscp_map[1]["dot1p"], 5)

        up_ctrl = parsed.get("up_ctrl_pkt", [])
        self.assertEqual(len(up_ctrl), 2)
        self.assertEqual(up_ctrl[0]["protocol"], "dhcp")
        self.assertEqual(up_ctrl[0]["queue"], 0)
        self.assertEqual(up_ctrl[0]["profile"], "default")
        self.assertEqual(up_ctrl[1]["protocol"], "arp")
        self.assertEqual(up_ctrl[1]["queue"], 0)
        self.assertNotIn("profile", up_ctrl[1])

        dn_ctrl = parsed.get("dn_ctrl_pkt", [])
        self.assertEqual(len(dn_ctrl), 2)
        self.assertEqual(dn_ctrl[0]["protocol"], "dhcp")
        self.assertEqual(dn_ctrl[0]["queue"], 0)
        self.assertEqual(dn_ctrl[0]["profile"], "default")
        self.assertEqual(dn_ctrl[1]["protocol"], "arp")
        self.assertEqual(dn_ctrl[1]["queue"], 0)

    def test_isam_qos_maps_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config={
                    "tc_map_dot1p": [
                        {"dot1p": 0, "tc": 0},
                        {"dot1p": 7, "tc": 7},
                    ],
                    "dscp_map_dot1p": [
                        {"dscp": "CS0", "dot1p": 0},
                        {"dscp": "EF", "dot1p": 5},
                    ],
                    "up_ctrl_pkt": [
                        {"protocol": "dhcp", "queue": 0, "profile": "default"},
                    ],
                    "dn_ctrl_pkt": [
                        {"protocol": "dhcp", "queue": 0, "profile": "default"},
                    ],
                },
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        rendered = result.get("rendered", [])
        self.assertIn("configure qos tc-map-dot1p 0 tc 0", rendered)
        self.assertIn("configure qos tc-map-dot1p 7 tc 7", rendered)
        self.assertIn("configure qos dscp-map-dot1p CS0 dot1p 0", rendered)
        self.assertIn("configure qos dscp-map-dot1p EF dot1p 5", rendered)
        self.assertIn("configure qos up-ctrl-pkt dhcp queue 0 profile default", rendered)
        self.assertIn("configure qos dn-ctrl-pkt dhcp queue 0 profile default", rendered)

    def test_isam_qos_maps_gathered_empty(self):
        class FakeConn:
            def get(self, cmd):
                return ""

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        gathered = result.get("gathered", {})
        self.assertEqual(gathered.get("tc_map_dot1p") or [], [])
        self.assertEqual(gathered.get("dscp_map_dot1p") or [], [])
        self.assertEqual(gathered.get("up_ctrl_pkt") or [], [])
        self.assertEqual(gathered.get("dn_ctrl_pkt") or [], [])
