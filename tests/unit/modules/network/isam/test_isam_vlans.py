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
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

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
        self.assertEqual(v.get("new_broadcast"), "enable")
        self.assertEqual(v.get("protocol_filter"), "pass-pppoe-ipoe")
        self.assertTrue(v.get("relay_id_dhcp"))
        self.assertTrue(v.get("dhcp_linerate"))
        self.assertTrue(v.get("pppoe_l2_encaps"))
        self.assertEqual(v.get("in_qos_prof_name"), "qprof1")

    def test_isam_vlans_gathered_empty(self):
        # test gathered with empty device output -> empty list
        class FakeConn:
            def get(self, cmd):
                return ""

        self.get_resource_connection_facts.return_value = FakeConn()

        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("gathered"), [])

    def test_isam_vlans_flat_fields_and_negative_flags(self):
        running = dedent(
            """
            configure vlan id 100 mode residential-bridge name Home priority 5 new-secure-fwd enable aging-time 60000 in-qos-prof-name name:Default_TC0 sntp-proxy vmac-not-in-opt61
            configure vlan id 100 dhcp-opt82-ext add-or-forward circuit-id-dhcp physical-id remote-id-dhcp customer-id relay-id-dhcp dhcpv6-itf-id physical-id dhcpv6-remote-id customer-id
            configure vlan id stacked:552:2 mode cross-connect name Stacked pppoe-relay-tag configurable circuit-id-pppoe physical-id remote-id-pppoe customer-id
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        vlans = {entry["id"]: entry for entry in result["parsed"]}

        self.assertEqual(vlans["100"]["priority"], 5)
        self.assertEqual(vlans["100"]["aging_time"], 60000)
        self.assertTrue(vlans["100"]["sntp_proxy"])
        self.assertTrue(vlans["100"]["vmac_not_in_opt61"])
        self.assertEqual(vlans["100"]["dhcp_opt82_ext"], "add-or-forward")
        self.assertTrue(vlans["100"]["relay_id_dhcp"])
        self.assertEqual(vlans["100"]["dhcpv6_itf_id"], "physical-id")
        self.assertEqual(vlans["100"]["dhcpv6_remote_id"], "customer-id")
        self.assertEqual(vlans["stacked:552:2"]["pppoe_relay_tag"], "configurable")

        negative = dedent(
            """
            id 100
              no sntp-proxy
              no relay-id-dhcp
            """
        )
        set_module_args(dict(running_config=negative, state="parsed"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        vlan = result["parsed"][0]
        self.assertFalse(vlan.get("sntp_proxy"))  # off is the default: not reported
        self.assertFalse(vlan.get("relay_id_dhcp"))

    def test_isam_vlans_rendered_smoke(self):
        set_module_args(
            dict(
                state="rendered",
                config=[
                    {
                        "id": "100",
                        "mode": "residential-bridge",
                        "name": "HomeNet",
                        "priority": 5,
                        "new-secure-fwd": "enable",
                        "sntp-proxy": True,
                    }
                ],
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("rendered", result)
        self.assertIsInstance(result.get("rendered"), list)
        self.assertIn(
            "configure vlan id 100 mode residential-bridge name HomeNet sntp-proxy priority 5 new-secure-fwd enable",
            result["rendered"],
        )

    def test_isam_vlans_compacts_each_native_vlan_scope_and_round_trips(self):
        set_module_args(
            dict(
                state="rendered",
                config=[
                    {
                        "id": "410",
                        "mode": "residential-bridge",
                        "name": "HSI-410",
                        "new-secure-fwd": "enable",
                        "in-qos-prof-name": "name:Default_TC0",
                        "dhcp-opt82-ext": "enable",
                        "circuit-id-dhcp": "physical-id",
                        "remote-id-dhcp": "customer-id",
                    }
                ],
            ),
            ignore_provider_arg,
        )
        rendered = self.execute_module(changed=False)["rendered"]
        self.assertEqual(
            rendered,
            [
                "configure vlan id 410 mode residential-bridge name HSI-410 new-secure-fwd enable in-qos-prof-name name:Default_TC0",
                "configure vlan id 410 dhcp-opt82-ext enable circuit-id-dhcp physical-id remote-id-dhcp customer-id",
            ],
        )

        set_module_args(
            dict(running_config="\n".join(rendered), state="parsed"),
            ignore_provider_arg,
        )
        parsed = self.execute_module(changed=False)["parsed"][0]
        self.assertEqual(parsed["mode"], "residential-bridge")
        self.assertEqual(parsed["name"], "HSI-410")
        self.assertEqual(parsed["dhcp_opt82_ext"], "enable")
        self.assertEqual(parsed["circuit_id_dhcp"], "physical-id")

    def test_isam_vlans_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)

    def _set_vlan_have(self):
        running = dedent(
            """\
            configure vlan id 100 mode residential-bridge name Home priority 5 new-secure-fwd enable
            configure vlan id 200 mode residential-bridge name Other priority 4 new-secure-fwd enable
            """
        )
        self.get_resource_connection_config.return_value.get.return_value = running
        self.get_resource_connection_facts.return_value.get.return_value = running

    def test_isam_vlans_merged_changes_only_requested_vlan_field(self):
        self._set_vlan_have()
        set_module_args(
            dict(state="merged", config=[{"id": "100", "priority": 6}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure vlan id 100 priority 6", result["commands"])
        self.assertFalse(any("id 200" in command for command in result["commands"]))

    def test_isam_vlans_merged_is_idempotent(self):
        self._set_vlan_have()
        set_module_args(
            dict(
                state="merged",
                config=[
                    {"id": "100", "name": "Home", "priority": 5, "new-secure-fwd": "enable"}
                ],
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_vlans_replaced_removes_omitted_fields_but_keeps_siblings(self):
        self._set_vlan_have()
        set_module_args(
            dict(state="replaced", config=[{"id": "100", "name": "Changed"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        # mode is mandatory and has no "no" form (CLI guide); it stays
        self.assertIn(
            "configure vlan id 100 name Changed no priority no new-secure-fwd",
            result["commands"],
        )
        self.assertTrue(any("no priority" in command for command in result["commands"]))
        self.assertFalse(any("id 200" in command for command in result["commands"]))

    def test_isam_vlans_overridden_removes_unrequested_vlan_siblings(self):
        self._set_vlan_have()
        set_module_args(
            dict(state="overridden", config=[{"id": "100", "name": "Home"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertTrue(any("id 200" in command for command in result["commands"]))

    def test_isam_vlans_deleted_removes_only_requested_vlan(self):
        self._set_vlan_have()
        set_module_args(
            dict(state="deleted", config=[{"id": "100"}]),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertTrue(any("id 100" in command for command in result["commands"]))
        self.assertFalse(any("id 200" in command for command in result["commands"]))
