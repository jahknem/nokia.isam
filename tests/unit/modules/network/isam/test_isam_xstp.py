from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_xstp
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamXstpModule(TestIsamModule):
    module = isam_xstp

    def setUp(self):
        super(TestIsamXstpModule, self).setUp()

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
        super(TestIsamXstpModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_xstp_parsed_flat(self):
        running = dedent(
            """
            configure xstp general enable-stp
            configure xstp general region-name LAB
            configure xstp port vlan-port:1/1/8/1 path-cost 20000
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertTrue(result["parsed"]["general"]["enable_stp"])
        self.assertEqual(result["parsed"]["general"]["region_name"], "LAB")
        self.assertEqual(result["parsed"]["ports"][0]["port"], "vlan-port:1/1/8/1")
        self.assertEqual(result["parsed"]["ports"][0]["path_cost"], 20000)

    def test_isam_xstp_gathered_hierarchical(self):
        sample = dedent(
            """
            configure xstp
            general
              enable-stp
              region-name LAB
            exit
            port vlan-port:1/1/8/1
              path-cost 20000
            exit
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertTrue(result["gathered"]["general"]["enable_stp"])
        self.assertEqual(result["gathered"]["general"]["region_name"], "LAB")
        self.assertEqual(result["gathered"]["ports"][0]["path_cost"], 20000)

    def test_isam_xstp_rendered(self):
        set_module_args(
            dict(
                config=dict(
                    general=dict(enable_stp=True, region_name="LAB"),
                    ports=[dict(port="vlan-port:1/1/8/1", path_cost=20000)],
                ),
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(
            set(result["rendered"]),
            {
                "configure xstp general enable-stp",
                "configure xstp general region-name LAB",
                "configure xstp port vlan-port:1/1/8/1 path-cost 20000",
            },
        )

    def test_isam_xstp_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)
