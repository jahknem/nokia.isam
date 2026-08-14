from ansible_collections.nokia.isam.plugins.modules import isam_bridges
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamBridgesModule(TestIsamModule):
    module = isam_bridges

    def setUp(self):
        super(TestIsamBridgesModule, self).setUp()

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
        super(TestIsamBridgesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_bridges_gathered_empty(self):
        # With empty output, gathered should be an empty list
        class FakeConn:
            def get(self, cmd):
                return ""

        self.get_resource_connection_facts.return_value = FakeConn()

        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result.get("gathered"), [])

    def test_isam_bridges_rendered_ageing_time_only(self):
        """Rendered with only top-level ageing_time."""
        set_module_args(
            dict(
                config={"ageing_time": 300},
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge ageing-time 300",
        ])

    def test_isam_bridges_rendered_port_basic(self):
        """Rendered with port-level pvid, default-priority, mac-learn-off."""
        set_module_args(
            dict(
                config={
                    "ageing_time": 300,
                    "port": [{
                        "port": "1/1/8/1",
                        "pvid": 99,
                        "default-priority": 0,
                        "mac-learn-off": True,
                    }],
                },
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge ageing-time 300",
            "configure bridge port 1/1/8/1",
            "configure bridge port 1/1/8/1 default-priority 0",
            "configure bridge port 1/1/8/1 mac-learn-off",
            "configure bridge port 1/1/8/1 pvid 99",
        ])

    def test_isam_bridges_rendered_vlan(self):
        """Rendered with vlan_id entries including tag."""
        vlan_entry = {"id": "100", "tag": "untagged"}
        set_module_args(
            dict(
                config={
                    "ageing_time": 300,
                    "port": [{
                        "port": "1/1/8/1",
                        "vlan_id": [vlan_entry],
                    }],
                },
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge ageing-time 300",
            "configure bridge port 1/1/8/1",
            "configure bridge port 1/1/8/1 vlan-id 100 tag untagged",
        ])

    def test_isam_bridges_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)

    def test_isam_bridges_rendered_network_vlan(self):
        vlan_entry = {"id": "100", "l2fwder_vlan": "100", "network_vlan": 200}
        set_module_args(
            dict(
                config={"port": [{"port": "1/1/8/1", "vlan_id": [vlan_entry]}]},
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge port 1/1/8/1",
            "configure bridge port 1/1/8/1 vlan-id 100 l2fwder-vlan 100",
            "configure bridge port 1/1/8/1 vlan-id 100 network-vlan 200",
        ])

    def test_isam_bridges_rendered_network_vlan_with_scope_and_qos(self):
        vlan_entry = {
            "id": "20",
            "tag": "single-tagged",
            "l2fwder_vlan": "720",
            "network_vlan": 720,
            "vlan_scope": "local",
            "qos": "priority:5",
        }
        set_module_args(
            dict(
                config={"port": [{"port": "1/1/8/1", "vlan_id": [vlan_entry]}]},
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge port 1/1/8/1",
            "configure bridge port 1/1/8/1 vlan-id 20 tag single-tagged l2fwder-vlan 720",
            "configure bridge port 1/1/8/1 vlan-id 20 network-vlan 720",
            "configure bridge port 1/1/8/1 vlan-id 20 vlan-scope local",
            "configure bridge port 1/1/8/1 vlan-id 20 qos priority:5",
        ])

    def test_isam_bridges_rejects_network_vlan_without_l2fwder_vlan(self):
        set_module_args(
            dict(
                config={"port": [{"port": "1/1/8/1", "vlan_id": [{"id": "100", "network_vlan": 200}]}]},
                state="rendered",
            ),
            ignore_provider_arg,
        )
        self.execute_module(failed=True)

    def test_isam_bridges_merged_keeps_matching_l2fwder_vlan(self):
        class FakeConn:
            def get(self, cmd):
                return (
                    "configure bridge port 1/1/8/1 vlan-id 20 "
                    "tag single-tagged l2fwder-vlan 720 vlan-scope local"
                )

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(
            dict(
                config={
                    "port": [{
                        "port": "1/1/8/1",
                        "vlan_id": [{
                            "id": "20",
                            "tag": "single-tagged",
                            "l2fwder_vlan": "720",
                            "network_vlan": 720,
                            "vlan_scope": "local",
                        }],
                    }]
                },
                state="merged",
                _ansible_check_mode=True,
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure bridge port 1/1/8/1 vlan-id 20 network-vlan 720"],
        )
        self.get_resource_connection.return_value.edit_config.assert_not_called()

    def test_isam_bridges_merged_sends_commands_through_edit_config(self):
        self.get_resource_connection_facts.return_value.get.return_value = ""
        set_module_args(
            dict(
                config={
                    "port": [{
                        "port": "1/1/8/1",
                        "vlan_id": [{
                            "id": "10",
                            "tag": "single-tagged",
                            "l2fwder_vlan": "710",
                            "vlan_scope": "local",
                        }],
                    }]
                },
                state="merged",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.get_resource_connection.return_value.edit_config.assert_called_once_with(
            candidate=result["commands"]
        )

    def test_isam_bridges_rejects_service_vlans_without_pvid_context(self):
        class FakeFactsConn:
            def get(self, command):
                return ""

        self.get_resource_connection_facts.return_value = FakeFactsConn()
        set_module_args(
            dict(
                config={
                    "port": [{
                        "port": "1/1/8/1",
                        "pvid": 99,
                        "vlan_id": [
                            {"id": "10", "tag": "single-tagged", "l2fwder_vlan": "710", "vlan_scope": "local"},
                            {"id": "99"},
                        ],
                    }]
                },
                state="merged",
            ),
            ignore_provider_arg,
        )
        self.execute_module(failed=True)

    def test_isam_bridges_parsed_network_vlan(self):
        set_module_args(
            dict(
                running_config=(
                    "configure bridge port 1/1/8/1 vlan-id 10 network-vlan 410"
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["port"][0]["vlan_id"][0]["id"], "10")
        self.assertEqual(
            result["parsed"]["port"][0]["vlan_id"][0]["network_vlan"], 410
        )

    def test_isam_bridges_deleted_vlan_preserves_vlan_siblings(self):
        class FakeConn:
            def get(self, cmd):
                return "\n".join([
                    "configure bridge port 1/1/8/1",
                    "configure bridge port 1/1/8/1 pvid 10",
                    "configure bridge port 1/1/8/1 vlan-id 10 tag untagged",
                    "configure bridge port 1/1/8/1 vlan-id 20 network-vlan 410",
                    "configure bridge port 1/1/8/2 vlan-id 30 tag single-tagged",
                ])

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(
            dict(
                state="deleted",
                config={
                    "port": [{
                        "port": "1/1/8/1",
                        "vlan_id": [{"id": "10"}],
                    }]
                },
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure bridge port 1/1/8/1 no vlan-id 10"],
        )
        self.assertFalse(any("vlan-id 20" in command for command in result["commands"]))
        self.assertFalse(any("1/1/8/2" in command for command in result["commands"]))

    def test_isam_bridges_deleted_pvid_preserves_vlan_siblings(self):
        class FakeConn:
            def get(self, cmd):
                return "\n".join([
                    "configure bridge port 1/1/8/1",
                    "configure bridge port 1/1/8/1 pvid 10",
                    "configure bridge port 1/1/8/1 vlan-id 10 tag untagged",
                    "configure bridge port 1/1/8/1 vlan-id 20 network-vlan 410",
                ])

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(
            dict(
                state="deleted",
                config={"port": [{"port": "1/1/8/1", "pvid": 10}]},
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure bridge port 1/1/8/1 no pvid"],
        )
        self.assertFalse(any("vlan-id" in command for command in result["commands"]))
