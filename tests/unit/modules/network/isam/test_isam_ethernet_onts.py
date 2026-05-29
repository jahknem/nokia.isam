from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_ethernet_onts
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamEthernetOntsModule(TestIsamModule):
    module = isam_ethernet_onts

    def setUp(self):
        super(TestIsamEthernetOntsModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_onts.ethernet_onts.Ethernet_ontsFacts.get_config"
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
        super(TestIsamEthernetOntsModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_ethernet_onts_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    '''
                    configure ethernet ont 1/1/1/1/1/1/1 cust-info "Customer port 1"
                    configure ethernet ont 1/1/1/1/1/1/1 auto-detect auto
                    configure ethernet ont 1/1/1/1/1/1/1 admin-state up
                    '''
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["uni_idx"], "1/1/1/1/1/1/1")
        self.assertEqual(result["parsed"][0]["cust_info"], "Customer port 1")
        self.assertEqual(result["parsed"][0]["auto_detect"], "auto")
        self.assertEqual(result["parsed"][0]["admin_state"], "up")

    def test_isam_ethernet_onts_gathered_nested(self):
        self.get_config.return_value = dedent(
            '''
            configure ethernet
              ont 1/1/1/1/1/1/1
                cust-info "Customer port 1"
                auto-detect auto
                admin-state up
              exit
            exit
            '''
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"][0]["uni_idx"], "1/1/1/1/1/1/1")
        self.assertEqual(result["gathered"][0]["cust_info"], "Customer port 1")
        self.assertEqual(result["gathered"][0]["auto_detect"], "auto")
        self.assertEqual(result["gathered"][0]["admin_state"], "up")

    def test_isam_ethernet_onts_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        uni_idx="1/1/1/1/1/1/1",
                        cust_info="Customer port 1",
                        auto_detect="auto",
                        admin_state="up",
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertIn('configure ethernet ont 1/1/1/1/1/1/1 cust-info "Customer port 1"', result["rendered"])
        self.assertIn("configure ethernet ont 1/1/1/1/1/1/1 auto-detect auto", result["rendered"])
        self.assertIn("configure ethernet ont 1/1/1/1/1/1/1 admin-state up", result["rendered"])

    def test_isam_ethernet_onts_merged_idempotent(self):
        self.get_config.return_value = dedent(
            '''
            configure ethernet ont 1/1/1/1/1/1/1 cust-info "Customer port 1"
            configure ethernet ont 1/1/1/1/1/1/1 auto-detect auto
            configure ethernet ont 1/1/1/1/1/1/1 admin-state up
            '''
        )
        set_module_args(
            dict(
                config=[
                    dict(
                        uni_idx="1/1/1/1/1/1/1",
                        cust_info="Customer port 1",
                        auto_detect="auto",
                        admin_state="up",
                    )
                ],
                state="merged",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
