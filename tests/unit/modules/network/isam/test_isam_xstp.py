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
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

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

    def test_isam_xstp_parsed_several_options_on_one_line(self):
        running = dedent(
            """
            configure xstp general enable-stp region-name e4:a1:e6:dd:f3:8f
            configure xstp port 1/1/8/1 priority 128 path-cost 200000
            configure xstp port 1/1/8/2
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["general"], {"enable_stp": True, "region_name": "e4:a1:e6:dd:f3:8f"})
        self.assertEqual(
            result["parsed"]["ports"],
            [{"port": "1/1/8/1", "path_cost": 200000}, {"port": "1/1/8/2"}],
        )

    def test_isam_xstp_hierarchical_inline_port_options(self):
        running = dedent(
            """
            configure xstp
            port 1/1/8/3 path-cost 300
            exit
            port 1/1/8/4
            exit
            exit
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["ports"], [{"port": "1/1/8/3", "path_cost": 300}, {"port": "1/1/8/4"}])

    def test_isam_xstp_option_less_port_renders_nothing(self):
        set_module_args(dict(config=dict(ports=[dict(port="1/1/8/2")]), state="rendered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], [])

    def test_isam_xstp_facts_are_validated_and_unwrapped(self):
        from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xstp.xstp import XstpFacts
        from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xstp import XstpTemplate

        facts = {"ansible_network_resources": {}}
        with patch.object(XstpTemplate, "validate_config", autospec=True, side_effect=lambda self, spec, data, redact=False: data) as validate:
            XstpFacts(module=None).populate_facts(None, facts, data=("configure xstp port 1/1/8/1 path-cost 7\n", ""))
        self.assertTrue(validate.called)
        self.assertEqual(facts["ansible_network_resources"]["xstp"], {"ports": [{"port": "1/1/8/1", "path_cost": 7}]})

    def test_isam_xstp_parsed_capture_lines(self):
        """Every 'configure xstp' line of the lab capture is parsed, nothing is dropped."""
        import os

        capture = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..",
                               "local_captures", "DS-LIN-TEST-01", "info_configure_flat.txt")
        if not os.path.exists(capture):
            self.skipTest("lab capture not available")
        with open(capture) as handle:
            lines = [line.rstrip() for line in handle if line.startswith("configure xstp ")]
        port_lines = [line for line in lines if line.startswith("configure xstp port ")]
        self.assertTrue(port_lines)
        set_module_args(dict(running_config="\n".join(lines), state="parsed"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["general"], {"enable_stp": True, "region_name": "e4:a1:e6:dd:f3:8f"})
        expected = sorted(
            ({"port": line.split()[3], "path_cost": int(line.split()[5])} for line in port_lines),
            key=lambda item: item["port"],
        )
        self.assertEqual(result["parsed"]["ports"], expected)
