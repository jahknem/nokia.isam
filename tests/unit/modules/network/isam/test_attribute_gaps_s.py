"""Regression coverage for the attribute batch interrupted by a provider limit."""
from importlib import import_module

from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


PREFIX = "ansible_collections.nokia.isam.plugins."
CASES = (
    ("xdsl_lines", [{"name": "1/1/3/1", "tca_line_threshold": {"enable": True, "es_nearend": 5}}],
     "configure xdsl line 1/1/3/1 tca-line-threshold enable es-nearend 5"),
    ("ethernet_onts", [{"uni_idx": "1/1/5/1/3/1/1", "phy": {"pm": "enable"},
                         "l2": {"pm_collect_ext": {"p_bits": 3, "vlan_id": 100}}, "cfm": {"portshut_ais": True}}],
     "\n".join([
         "configure ethernet ont 1/1/5/1/3/1/1 phy pm enable",
         "configure ethernet ont 1/1/5/1/3/1/1 l2 pm-collect-ext p-bits 3 vlan-id 100",
         "configure ethernet ont 1/1/5/1/3/1/1 cfm portshut-ais",
     ])),
    ("xdsl_bonding", {"groups": [{"group_id": "1/1/3/1", "group_profile": "profile-one", "up": True}],
                      "boards": [{"board_id": "1/1/3", "vect_fallback": {"group_profile": "profile-two"}}]},
     "\n".join([
         "configure xdsl-bonding group 1/1/3/1 group-profile profile-one up",
         "configure xdsl-bonding board 1/1/3 vect-fallback group-profile profile-two",
     ])),
    ("xstp", {"general": {"priority": 4096, "hello_time": 3},
              "ports": [{"port": "1/1/3/1", "priority": 32, "edge_port": True}]},
     "\n".join([
         "configure xstp general priority 4096 hello-time 3",
         "configure xstp port 1/1/3/1 priority 32 edge-port",
     ])),
    ("isam_equipment", {"slots": [{"id": "lt:1/1/5", "capab_profile": "fttu_lt", "operational_mode": "gpon"}]},
     "configure equipment slot lt:1/1/5 capab-profile fttu_lt operational-mode gpon"),
)


class TestInterruptedAttributeBatch(TestIsamModule):
    def setUp(self):
        super(TestInterruptedAttributeBatch, self).setUp()
        for target in (
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        ):
            mock = patch(target)
            mock.start()
            self.addCleanup(mock.stop)

    def run_state(self, family, state, config=None, text=""):
        self.module = import_module(PREFIX + "modules." + (family if family.startswith("isam_") else "isam_" + family))
        facts_module = import_module(PREFIX + "module_utils.network.isam.facts." + family + "." + family)
        facts_class = getattr(facts_module, family.capitalize() + "Facts")
        args = {"state": state, "_ansible_check_mode": True}
        if state == "parsed":
            args["running_config"] = text
        elif config is not None:
            args["config"] = config
        set_module_args(args, True)
        with patch.object(facts_class, "get_config", return_value=text):
            return self.execute_module(changed=state in ("replaced", "deleted"))

    def test_parse_and_render_round_trip(self):
        for family, config, text in CASES:
            with self.subTest(family=family):
                parsed = self.run_state(family, "parsed", text=text)["parsed"]
                self.assertEqual(parsed, config)
                rendered = self.run_state(family, "rendered", config=config)["rendered"]
                reparsed = self.run_state(family, "parsed", text="\n".join(rendered))["parsed"]
                self.assertEqual(reparsed, config)

    def test_merged_is_idempotent(self):
        for family, config, text in CASES:
            with self.subTest(family=family):
                result = self.run_state(family, "merged", config=config, text=text)
                self.assertEqual(result["commands"], [])

    def test_deleted_resets_attributes(self):
        for family, config, text in CASES:
            with self.subTest(family=family):
                result = self.run_state(family, "deleted", config=config, text=text)
                self.assertTrue(result["commands"])
                self.assertTrue(all(" no " in command for command in result["commands"]))

    def test_bonding_delete_one_group_preserves_other_sections(self):
        text = "\n".join([
            "configure xdsl-bonding group-assembly-time 50",
            "configure xdsl-bonding group 1/1/3/1 group-profile profile-one",
            "configure xdsl-bonding group 1/1/3/2 group-profile profile-sibling",
            "configure xdsl-bonding board 1/1/3 vect-fallback group-profile profile-two",
        ])
        result = self.run_state("xdsl_bonding", "deleted", {"groups": [{"group_id": "1/1/3/1"}]}, text)
        self.assertEqual(result["commands"], ["configure xdsl-bonding group 1/1/3/1 no group-profile"])

    def test_replaced_resets_omitted_subnode_attributes(self):
        for family, config, text in CASES:
            with self.subTest(family=family):
                parsed = self.run_state(family, "parsed", text=text)["parsed"]
                if isinstance(parsed, list):
                    identity = "name" if family == "xdsl_lines" else "uni_idx"
                    wanted = [{identity: parsed[0][identity]}]
                elif family == "xdsl_bonding":
                    wanted = {"groups": [{"group_id": "1/1/3/1"}], "boards": [{"board_id": "1/1/3"}]}
                elif family == "xstp":
                    wanted = {"general": {}, "ports": [{"port": "1/1/3/1"}]}
                else:
                    wanted = {"slots": [{"id": "lt:1/1/5"}]}
                result = self.run_state(family, "replaced", wanted, text)
                self.assertTrue(result["commands"])
