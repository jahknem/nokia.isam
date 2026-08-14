from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_voice_sip
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.voice_sip.voice_sip import Isam_voice_sipFacts
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

    def test_isam_voice_sip_merged_is_idempotent_for_existing_vsp(self):
        self.get_config.return_value = "configure voice sip vsp vsp1 domain-name DomainName.com"
        set_module_args(
            dict(
                state="merged",
                config={"vsp": [{"name": "vsp1", "domain_name": "DomainName.com"}]},
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("commands", []), [])

    def test_isam_voice_sip_replaced_removes_unrequested_vsp(self):
        self.get_config.return_value = dedent(
            """\
            configure voice sip vsp vsp1 domain-name DomainName.com
            configure voice sip vsp vsp2 domain-name OtherDomain.com
            """
        )
        set_module_args(
            dict(
                state="replaced",
                config={"vsp": [{"name": "vsp1", "domain_name": "DomainName.com"}]},
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertIn("configure voice sip no vsp vsp2", result["commands"])
        self.assertNotIn("configure voice sip no vsp vsp1", result["commands"])

    def test_isam_voice_sip_deleted_targets_only_requested_vsp(self):
        self.get_config.return_value = dedent(
            """\
            configure voice sip vsp vsp1 domain-name DomainName.com
            configure voice sip vsp vsp2 domain-name OtherDomain.com
            configure voice sip cas-nsm-prof cas1 international-prefix "#"
            """
        )
        set_module_args(
            dict(state="deleted", config={"vsp": [{"name": "vsp1"}]}),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure voice sip no vsp vsp1"])

    def test_isam_voice_sip_statistics_positive_and_negative_parse(self):
        parsed = Isam_voice_sipFacts._parse_voice_sip([
            "configure voice sip statistics stats-5min-config",
            "configure voice sip statistics cdr-config",
            "configure voice sip statistics stats-config no per-line per-board",
        ])
        self.assertTrue(parsed["statistics"]["stats_5min_config"])
        self.assertTrue(parsed["statistics"]["cdr_config"])
        self.assertFalse(parsed["statistics"]["per_line"])
        self.assertTrue(parsed["statistics"]["per_board"])

    def test_isam_voice_sip_parses_all_detail_flat_vsp_words(self):
        vsp_words = (
            "no dmpm-intdgt-expid no dial-start-timer no dial-long-timer "
            "no dial-short-timer no uri-type no rfc2833-pl-type no rfc2833-process "
            "no min-data-jitter no init-data-jitter no max-data-jitter no release-mode "
            "no dyn-pt-nego-type no vbd-g711a-pl-type no vbd-g711u-pl-type no vbd-mode "
            "no warmline-dl-timer no reg-sub no dtmf-sip-info no sub-period "
            "no sub-head-start no t38-same-udp no dhcp-option82 no sspprofile "
            "no signaling-ipmode no tls-cafile no media-ipmode"
        )
        set_module_args(
            dict(
                state="parsed",
                running_config=(
                    "configure voice sip vsp vsp1 domain-name DomainName.com "
                    + vsp_words
                ),
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        parsed_vsp = result["parsed"]["vsp"][0]

        assert parsed_vsp["dmpm_intdgt_expid"] is False
        assert parsed_vsp["dial_start_timer"] is False
        assert parsed_vsp["rfc2833_process"] is False
        assert parsed_vsp["media_ipmode"] is False

    def test_isam_voice_sip_parses_all_detail_flat_redundancy_words(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=(
                    "configure voice sip redundancy vsp1 no auto-server-fo "
                    "no auto-server-fb no auto-sos-fo no auto-sos-fb "
                    "no rtry-after-thrsh no options-max-fwd no dns-redun-mode "
                    "no fail-obs-timer no fg-intv-503 no time-thrsh-503 "
                    "no nbr-thrsh-503 no auto-srv-fo-timer"
                ),
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        parsed_redundancy = result["parsed"]["redundancy"][0]

        assert parsed_redundancy["auto_server_fo"] is False
        assert parsed_redundancy["dns_redun_mode"] is False
        assert parsed_redundancy["auto_srv_fo_timer"] is False
