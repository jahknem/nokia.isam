from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_link_agg
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamLinkAggModule(TestIsamModule):
    module = isam_link_agg

    def setUp(self):
        super(TestIsamLinkAggModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.link_agg.link_agg.Link_aggFacts.get_config"
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
        super(TestIsamLinkAggModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_link_agg_rendered(self):
        set_module_args(
            dict(
                config=dict(
                    ports=[dict(id="1/1/8/1", lacp_mode="passive", timeout="short")],
                    groups=[
                        dict(
                            id="1/1/8/10",
                            load_sharing_policy="mac-src-dst",
                            swo_revert="enable",
                            mode="dynamic",
                            master_iwf="auto",
                            ports=["1/1/8/1"],
                        )
                    ],
                ),
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            set(result["rendered"]),
            set(
                [
                    "configure link-agg port 1/1/8/1 passive-lacp",
                    "configure link-agg port 1/1/8/1 short-timeout",
                    "configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst",
                    "configure link-agg group 1/1/8/10 swo-revert enable",
                    "configure link-agg group 1/1/8/10 mode dynamic",
                    "configure link-agg group 1/1/8/10 master-iwf auto",
                    "configure link-agg group 1/1/8/10 port 1/1/8/1",
                ]
            ),
        )

    def test_isam_link_agg_parsed_flat(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """
                    configure link-agg port 1/1/8/1 passive-lacp
                    configure link-agg port 1/1/8/1 short-timeout
                    configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst
                    configure link-agg group 1/1/8/10 swo-revert enable
                    configure link-agg group 1/1/8/10 mode dynamic
                    configure link-agg group 1/1/8/10 master-iwf auto
                    configure link-agg group 1/1/8/10 port 1/1/8/1
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["ports"][0]["id"], "1/1/8/1")
        self.assertEqual(result["parsed"]["ports"][0]["lacp_mode"], "passive")
        self.assertEqual(result["parsed"]["ports"][0]["timeout"], "short")
        self.assertEqual(result["parsed"]["groups"][0]["id"], "1/1/8/10")
        self.assertEqual(result["parsed"]["groups"][0]["ports"], ["1/1/8/1"])

    def test_isam_link_agg_parsed_packed_flat(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """
                    configure link-agg port 1/1/8/1 passive-lacp short-timeout actor-port-prio 32768
                    configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst mode dynamic port 1/1/8/1
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["ports"][0]["lacp_mode"], "passive")
        self.assertEqual(result["parsed"]["ports"][0]["timeout"], "short")
        self.assertEqual(result["parsed"]["ports"][0]["actor_port_prio"], "32768")
        self.assertEqual(result["parsed"]["groups"][0]["mode"], "dynamic")
        self.assertEqual(result["parsed"]["groups"][0]["ports"], ["1/1/8/1"])

    def test_isam_link_agg_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """
            configure link-agg port 1/1/8/1 passive-lacp
            configure link-agg port 1/1/8/1 short-timeout
            configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst
            configure link-agg group 1/1/8/10 swo-revert enable
            configure link-agg group 1/1/8/10 mode dynamic
            configure link-agg group 1/1/8/10 master-iwf auto
            configure link-agg group 1/1/8/10 port 1/1/8/1
            """
        )
        set_module_args(
            dict(
                config=dict(
                    ports=[dict(id="1/1/8/1", lacp_mode="passive", timeout="short")],
                    groups=[
                        dict(
                            id="1/1/8/10",
                            load_sharing_policy="mac-src-dst",
                            swo_revert="enable",
                            mode="dynamic",
                            master_iwf="auto",
                            ports=["1/1/8/1"],
                        )
                    ],
                ),
                state="merged",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_link_agg_replaced_port_fields(self):
        self.get_config.return_value = dedent(
            """
            configure link-agg port 1/1/8/1 passive-lacp
            configure link-agg port 1/1/8/1 short-timeout
            configure link-agg port 1/1/8/1 actor-port-prio 32768
            """
        )
        set_module_args(
            dict(
                config=dict(
                    ports=[dict(id="1/1/8/1", passive_lacp=True)],
                ),
                state="replaced",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            set(result["commands"]),
            set([
                "configure link-agg port 1/1/8/1 no short-timeout",
                "configure link-agg port 1/1/8/1 no actor-port-prio",
            ]),
        )
