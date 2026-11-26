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
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_isam_qos_maps_parsed(self):
        running = dedent(
            """
            configure qos
            tc-map-dot1p 0 tc 0
            tc-map-dot1p 7 tc 7
            dscp-map-dot1p CS0 dot1p 0
            dscp-map-dot1p EF dot1p 5
            up-ctrl-pkt dhcp dscp 46 pbit 5 tc 7
            up-ctrl-pkt arp
            dn-ctrl-pkt dhcp tc 3
            dn-ctrl-pkt arp
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
        self.assertEqual(up_ctrl[0]["dscp"], 46)
        self.assertEqual(up_ctrl[0]["pbit"], 5)
        self.assertEqual(up_ctrl[0]["tc"], 7)
        self.assertEqual(up_ctrl[1], {"protocol": "arp"})

        dn_ctrl = parsed.get("dn_ctrl_pkt", [])
        self.assertEqual(len(dn_ctrl), 2)
        self.assertEqual(dn_ctrl[0]["protocol"], "dhcp")
        self.assertEqual(dn_ctrl[0]["tc"], 3)
        self.assertEqual(dn_ctrl[1], {"protocol": "arp"})

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
                        {"protocol": "dhcp", "dscp": 46, "tc": 7},
                    ],
                    "dn_ctrl_pkt": [
                        {"protocol": "dhcp", "tc": 3},
                    ],
                },
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        rendered = result.get("rendered", [])
        self.assertIn("configure qos tc-map-dot1p 0 tc 0", rendered)
        self.assertIn("configure qos tc-map-dot1p 7 tc 7", rendered)
        self.assertIn("configure qos dscp-map-dot1p CS0 dot1p-value 0", rendered)
        self.assertIn("configure qos dscp-map-dot1p EF dot1p-value 5", rendered)
        self.assertIn("configure qos up-ctrl-pkt dhcp dscp 46 tc 7", rendered)
        self.assertIn("configure qos dn-ctrl-pkt dhcp tc 3", rendered)

    def test_isam_qos_maps_replaced(self):
        class FakeConn:
            _map = {
                "info configure qos tc-map-dot1p flat": (
                    "tc-map-dot1p 0 tc 0\ntc-map-dot1p 7 tc 7\n"
                ),
                "info configure qos dscp-map-dot1p flat": (
                    "dscp-map-dot1p CS0 dot1p 0\ndscp-map-dot1p EF dot1p 5\n"
                ),
                "info configure qos up-ctrl-pkt flat": (
                    "up-ctrl-pkt dhcp dscp 46 pbit 5 tc 7\n"
                    "up-ctrl-pkt arp\n"
                ),
                "info configure qos dn-ctrl-pkt flat": (
                    "dn-ctrl-pkt dhcp tc 3\n"
                    "dn-ctrl-pkt arp\n"
                ),
            }

            def get(self, cmd):
                return self._map.get(cmd, "")

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(
            dict(
                state="replaced",
                config={
                    # dot1p=7 removed from want → should be deleted
                    "tc_map_dot1p": [
                        {"dot1p": 0, "tc": 0},
                    ],
                    # CS0 dot1p changed 0→3, EF unchanged, AF11 is new
                    "dscp_map_dot1p": [
                        {"dscp": "CS0", "dot1p": 3},
                        {"dscp": "EF", "dot1p": 5},
                        {"dscp": "AF11", "dot1p": 1},
                    ],
                    # up_ctrl_pkt / dn_ctrl_pkt omitted → left untouched
                },
            ),
            ignore_provider_arg,
        )

        expected_commands = sorted([
            "configure qos no tc-map-dot1p 7",
            "configure qos dscp-map-dot1p CS0 dot1p-value 3",
            "configure qos dscp-map-dot1p AF11 dot1p-value 1",
        ])
        result = self.execute_module(changed=True, commands=expected_commands)
        commands = result.get("commands", [])
        # verify no commands are generated for untouched fields
        for cmd in commands:
            self.assertNotIn("up-ctrl-pkt", cmd)
            self.assertNotIn("dn-ctrl-pkt", cmd)

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


def _doc_options_match_argspec(doc_options, spec_options, path=""):
    """Every argspec option is documented (recursively) and vice versa."""
    assert set(doc_options) == set(spec_options), (path, sorted(set(doc_options) ^ set(spec_options)))
    for name, spec in spec_options.items():
        if spec.get("options"):
            _doc_options_match_argspec(doc_options[name].get("suboptions") or {}, spec["options"], path + "." + name)


def test_isam_qos_maps_documentation_matches_argspec():
    import yaml

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_maps.qos_maps import Qos_mapsArgs

    doc = yaml.safe_load(isam_qos_maps.DOCUMENTATION)
    _doc_options_match_argspec(doc["options"], Qos_mapsArgs.argument_spec)
    tc_doc = doc["options"]["config"]["suboptions"]["tc_map_dot1p"]["suboptions"]
    assert tc_doc["dpcolor"]["type"] == "str"
    assert tc_doc["policer_color"]["type"] == "str"


def test_isam_qos_maps_capture_map_lines_are_parsed():
    """tc-map-dot1p / dscp-map-dot1p lines of the lab capture are parsed completely.

    up-ctrl-pkt / dn-ctrl-pkt lines are not checked: the device form ('<protocol> [dscp|pbit|tc]')
    does not match the module's queue/profile model (reported separately).
    """
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_maps import Qos_mapsTemplate

    from . import lab_captures

    tc_lines = []
    dscp_lines = []
    for line in lab_captures.configured().splitlines():
        if line.startswith("configure qos tc-map-dot1p "):
            tc_lines.append(line.rstrip())
        elif line.startswith("configure qos dscp-map-dot1p "):
            dscp_lines.append(line.rstrip())
    parsed = Qos_mapsTemplate(lines=tc_lines + dscp_lines).parse()
    assert len(parsed["tc_map_dot1p"]) == len(tc_lines) == 8
    for line, entry in zip(tc_lines, parsed["tc_map_dot1p"]):
        tokens = line.split()
        assert entry == {"dot1p": int(tokens[3]), "tc": int(tokens[5]), "dpcolor": tokens[7], "policer_color": tokens[9]}
    assert len(parsed["dscp_map_dot1p"]) == len(dscp_lines)
    for line, entry in zip(dscp_lines, parsed["dscp_map_dot1p"]):
        tokens = line.split()
        assert entry == {"dscp": tokens[3], "dot1p": int(tokens[5])}
