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

    def test_isam_voice_sip_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    registrar=dict(server="10.0.0.1", port=5060, realm="example.com"),
                    proxy=dict(server="10.0.0.2", port=5060),
                    codec=[
                        dict(priority=1, type="g711a"),
                        dict(priority=2, type="g711u"),
                    ],
                    sip_profile=[
                        dict(name="default", timer_t1=500, timer_t2=4000),
                    ],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "configure voice sip registrar server 10.0.0.1",
                "configure voice sip registrar port 5060",
                "configure voice sip registrar realm example.com",
                "configure voice sip proxy server 10.0.0.2",
                "configure voice sip proxy port 5060",
                "configure voice sip codec priority 1 type g711a",
                "configure voice sip codec priority 2 type g711u",
                "configure voice sip sip-profile default timer-t1 500",
                "configure voice sip sip-profile default timer-t2 4000",
            ],
        )

    def test_isam_voice_sip_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure voice sip registrar server 10.0.0.1
                    configure voice sip registrar port 5060
                    configure voice sip registrar realm example.com
                    configure voice sip proxy server 10.0.0.2
                    configure voice sip proxy port 5060
                    configure voice sip codec priority 1 type g711a
                    configure voice sip codec priority 2 type g711u
                    configure voice sip sip-profile default timer-t1 500
                    configure voice sip sip-profile default timer-t2 4000
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["parsed"]["registrar"],
            dict(server="10.0.0.1", port=5060, realm="example.com"),
        )
        self.assertEqual(
            result["parsed"]["proxy"],
            dict(server="10.0.0.2", port=5060),
        )
        self.assertEqual(
            result["parsed"]["codec"],
            [dict(priority=1, type="g711a"), dict(priority=2, type="g711u")],
        )
        self.assertEqual(
            result["parsed"]["sip_profile"],
            [dict(name="default", timer_t1=500, timer_t2=4000)],
        )

    def test_isam_voice_sip_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure voice sip registrar server 10.0.0.1
            configure voice sip registrar port 5060
            configure voice sip registrar realm example.com
            configure voice sip proxy server 10.0.0.2
            configure voice sip proxy port 5060
            configure voice sip codec priority 1 type g711a
            configure voice sip codec priority 2 type g711u
            configure voice sip sip-profile default timer-t1 500
            configure voice sip sip-profile default timer-t2 4000
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["gathered"]["registrar"],
            dict(server="10.0.0.1", port=5060, realm="example.com"),
        )
        self.assertEqual(
            result["gathered"]["proxy"],
            dict(server="10.0.0.2", port=5060),
        )
        self.assertEqual(
            result["gathered"]["codec"],
            [dict(priority=1, type="g711a"), dict(priority=2, type="g711u")],
        )
        self.assertEqual(
            result["gathered"]["sip_profile"],
            [dict(name="default", timer_t1=500, timer_t2=4000)],
        )

    def test_isam_voice_sip_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure voice sip registrar server 10.0.0.1
            configure voice sip registrar port 5060
            configure voice sip registrar realm example.com
            configure voice sip proxy server 10.0.0.2
            configure voice sip proxy port 5060
            configure voice sip codec priority 1 type g711a
            configure voice sip codec priority 2 type g711u
            configure voice sip sip-profile default timer-t1 500
            configure voice sip sip-profile default timer-t2 4000
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    registrar=dict(server="10.0.0.1", port=5060, realm="example.com"),
                    proxy=dict(server="10.0.0.2", port=5060),
                    codec=[
                        dict(priority=1, type="g711a"),
                        dict(priority=2, type="g711u"),
                    ],
                    sip_profile=[
                        dict(name="default", timer_t1=500, timer_t2=4000),
                    ],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
