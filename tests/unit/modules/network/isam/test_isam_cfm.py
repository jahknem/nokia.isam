from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_cfm
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from .isam_module import TestIsamModule, set_module_args


class TestCfmModule(TestIsamModule):
    module = isam_cfm

    def setUp(self):
        super(TestCfmModule, self).setUp()
        self.connection_patch = patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection")
        self.connection_patch.start()
        self.facts_patch = patch("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.cfm.cfm.CfmFacts.get_facts")
        self.get_facts = self.facts_patch.start()
        self.get_facts.return_value = ({"ansible_network_resources": {"isam_cfm": {"domains": [], "slm": {}, "y1731pm": []}}}, [])

    def tearDown(self):
        self.facts_patch.stop()
        self.connection_patch.stop()
        super(TestCfmModule, self).tearDown()

    def test_rendered_core_domain_and_mep(self):
        set_module_args({"state": "rendered", "config": {"domains": [{"domain_index": 1, "name": "string operator", "level": 3, "associations": [{"association_index": 2, "ccm_interval": "10", "meps": [{"mepid": 7, "location": "slot:1/1/1"}]}]}]}}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure cfm domain 1 name string operator level 3", "configure cfm domain 1 association 2 ccm-interval 10", "configure cfm domain 1 association 2 mep 7 location slot:1/1/1"])

    def test_parsed(self):
        self.facts_patch.stop()
        set_module_args({"state": "parsed", "running_config": dedent("""\
            configure cfm domain 1 name string operator level 3
            configure cfm domain 1 association 2 mep 7 location slot:1/1/1 cci-enable
        """)}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["domains"][0]["level"], 3)
        self.assertTrue(result["parsed"]["domains"][0]["associations"][0]["meps"][0]["cci_enable"])

    def test_merged_check_mode(self):
        self.get_facts.return_value = ({"ansible_network_resources": {"isam_cfm": {"domains": [{"domain_index": 1, "name": "string operator", "level": 3}], "slm": {}, "y1731pm": []}}}, [])
        set_module_args({"state": "merged", "config": {"domains": [{"domain_index": 1, "name": "string operator", "level": 3, "associations": [{"association_index": 2, "ccm_interval": "10"}]}]}}, True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure cfm domain 1 association 2 ccm-interval 10"])
