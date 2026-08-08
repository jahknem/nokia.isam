from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_arp_relay
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamArpRelayModule(TestIsamModule):
    module = isam_arp_relay

    def setUp(self):
        super(TestIsamArpRelayModule, self).setUp()
        self.connection_patch = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        )
        self.connection = self.connection_patch.start()
        self.facts_patch = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.arp_relay.arp_relay.Isam_arp_relayFacts.get_facts"
        )
        self.get_facts = self.facts_patch.start()
        self.get_facts.side_effect = self._parse_facts

    def _parse_facts(self, data=None, **kwargs):
        if data:
            objects = []
            for line in data.splitlines():
                fields = line.split()
                if len(fields) >= 4 and fields[0:3] == ["configure", "arp-relay", "statistics"]:
                    objects.append({"name": " ".join(fields[3:]), "statistics": True})
                elif len(fields) >= 5 and fields[0:4] == ["configure", "arp-relay", "no", "statistics"]:
                    objects.append({"name": " ".join(fields[4:]), "statistics": False})
            return {"ansible_network_resources": {"isam_arp_relay": objects}}, []
        return (self.get_facts.return_value or ({"ansible_network_resources": {"isam_arp_relay": []}}, []))

    def tearDown(self):
        self.facts_patch.stop()
        self.connection_patch.stop()
        super(TestIsamArpRelayModule, self).tearDown()

    def test_rendered(self):
        set_module_args(
            {"state": "rendered", "config": [{"name": "vlan-port:1/1/1/1:100", "statistics": True}]},
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure arp-relay statistics vlan-port:1/1/1/1:100"])

    def test_parsed(self):
        self.facts_patch.stop()
        set_module_args(
            {
                "state": "parsed",
                "running_config": dedent(
                    """\
                    configure arp-relay statistics vlan-port:1/1/1/1:100
                    configure arp-relay no statistics vlan-port:1/1/1/2:200
                    """
                ),
            },
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["statistics"], True)
        self.assertEqual(result["parsed"][1]["statistics"], False)

    def test_gathered(self):
        self.get_facts.return_value = (
            {"ansible_network_resources": {"isam_arp_relay": [{"name": "vlan-port:1/1/1/1:100", "statistics": True}]}},
            [],
        )
        set_module_args({"state": "gathered"}, ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"][0]["name"], "vlan-port:1/1/1/1:100")

    def test_merged_check_mode(self):
        self.get_facts.return_value = (
            {"ansible_network_resources": {"isam_arp_relay": [{"name": "vlan-port:1/1/1/1:100", "statistics": True}]}},
            [],
        )
        set_module_args(
            {"state": "merged", "config": [{"name": "vlan-port:1/1/1/2:200", "statistics": True}]},
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure arp-relay statistics vlan-port:1/1/1/2:200"])
