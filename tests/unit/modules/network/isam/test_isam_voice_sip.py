from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_voice_sip
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamVoiceSipModule(TestIsamModule):
    module = isam_voice_sip

    def setUp(self):
        super(TestIsamVoiceSipModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.voice_sip.voice_sip.Isam_voice_sipFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamVoiceSipModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_voice_sip_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure voice sip lineid-syn-prof profile1 isdn-syntax ""
            configure voice sip vsp vsp1 domain-name DomainName.com timer-b 32000 timer-f 32000 timer-t1 500 timer-t2 4000
            configure voice sip redundancy-cmd vsp1 fail-x-type geo-fail-over
            configure voice sip statistics stats-config per-line per-board per-system per-call out-any-rsp in-any-rsp
            configure voice sip cas-nsm-prof common-cas-profile international-prefix "#" country-code "#" outg-cpn-length 0
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        gathered = result["gathered"]

        self.assertIn("lineid_syn_prof", gathered)
        self.assertEqual(len(gathered["lineid_syn_prof"]), 1)
        self.assertEqual(
            gathered["lineid_syn_prof"][0]["name"], "profile1"
        )
        # isdn_syntax is empty ("") so remove_empties strips it

        self.assertIn("vsp", gathered)
        self.assertEqual(len(gathered["vsp"]), 1)
        self.assertEqual(gathered["vsp"][0]["name"], "vsp1")
        self.assertEqual(gathered["vsp"][0]["domain_name"], "DomainName.com")
        self.assertEqual(gathered["vsp"][0]["timer_b"], 32000)
        self.assertEqual(gathered["vsp"][0]["timer_f"], 32000)
        self.assertEqual(gathered["vsp"][0]["timer_t1"], 500)
        self.assertEqual(gathered["vsp"][0]["timer_t2"], 4000)

        self.assertIn("redundancy_cmd", gathered)
        self.assertEqual(len(gathered["redundancy_cmd"]), 1)
        self.assertEqual(gathered["redundancy_cmd"][0]["name"], "vsp1")
        self.assertEqual(
            gathered["redundancy_cmd"][0]["fail_x_type"], "geo-fail-over"
        )

        self.assertIn("statistics", gathered)
        self.assertTrue(gathered["statistics"]["per_line"])
        self.assertTrue(gathered["statistics"]["per_board"])

        self.assertIn("cas_nsm_prof", gathered)
        self.assertEqual(len(gathered["cas_nsm_prof"]), 1)
        self.assertEqual(
            gathered["cas_nsm_prof"][0]["name"], "common-cas-profile"
        )
        self.assertEqual(
            gathered["cas_nsm_prof"][0]["international_prefix"], "#"
        )
        self.assertEqual(gathered["cas_nsm_prof"][0]["outg_cpn_length"], 0)

    def test_isam_voice_sip_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure voice sip lineid-syn-prof profile1 isdn-syntax ""
                    configure voice sip vsp vsp1 domain-name DomainName.com timer-b 32000 timer-f 32000 timer-t1 500 timer-t2 4000
                    configure voice sip redundancy-cmd vsp1 fail-x-type geo-fail-over
                    configure voice sip statistics stats-config per-line per-board per-system per-call out-any-rsp in-any-rsp
                    configure voice sip cas-nsm-prof common-cas-profile international-prefix "#" country-code "#" outg-cpn-length 0
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        parsed = result["parsed"]

        self.assertIn("vsp", parsed)
        self.assertEqual(len(parsed["vsp"]), 1)
        self.assertEqual(
            parsed["vsp"][0],
            dict(
                name="vsp1",
                domain_name="DomainName.com",
                timer_b=32000,
                timer_f=32000,
                timer_t1=500,
                timer_t2=4000,
            ),
        )

        self.assertIn("cas_nsm_prof", parsed)
        self.assertEqual(
            parsed["cas_nsm_prof"][0],
            dict(
                name="common-cas-profile",
                international_prefix="#",
                country_code="#",
                outg_cpn_length=0,
            ),
        )

    def test_isam_voice_sip_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    vsp=[
                        dict(
                            name="vsp1",
                            domain_name="DomainName.com",
                            timer_b=32000,
                            timer_f=32000,
                            timer_t1=500,
                            timer_t2=4000,
                        ),
                    ],
                    cas_nsm_prof=[
                        dict(
                            name="common-cas-profile",
                            international_prefix="#",
                            country_code="#",
                            outg_cpn_length=0,
                        ),
                    ],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("rendered", result)
