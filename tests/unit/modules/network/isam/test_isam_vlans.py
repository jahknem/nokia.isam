from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_vlans
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamVlansModule(TestIsamModule):
    module = isam_vlans

    def setUp(self):
        super(TestIsamVlansModule, self).setUp()

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
        super(TestIsamVlansModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_vlans_parsed(self):
        # test parsed for single VLAN with key fields
        running = dedent(
            """
            id 100 mode residential-bridge
              name "HomeNet"
              new-broadcast enable
              protocol-filter pass-pppoe-ipoe
              dhcp-opt82-ext enable
              relay-id-dhcp
              dhcp-linerate
              pppoe-l2-encaps
              in-qos-prof-name qprof1
            """
        )
        set_module_args(
            dict(
                running_config=running,
                state="parsed",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        parsed = result.get("parsed", [])
        self.assertTrue(parsed and isinstance(parsed, list))
        v = parsed[0]
        self.assertEqual(v.get("id"), "100")
        self.assertEqual(v.get("mode"), "residential-bridge")
        self.assertEqual(v.get("name"), "HomeNet")
        self.assertEqual(v.get("new-broadcast"), "enable")
        self.assertEqual(v.get("protocol-filter"), "pass-pppoe-ipoe")
        self.assertTrue(v.get("relay-id-dhcp"))
        self.assertTrue(v.get("dhcp-linerate"))
        self.assertTrue(v.get("pppoe-l2-encaps"))
        self.assertEqual(v.get("in-qos-prof-name"), "qprof1")

    def test_isam_vlans_gathered_empty(self):
        # test gathered with empty device output -> empty list
        class FakeConn:
            def get(self, cmd):
                return ""

        self.get_resource_connection_facts.return_value = FakeConn()

        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("gathered"), [])
