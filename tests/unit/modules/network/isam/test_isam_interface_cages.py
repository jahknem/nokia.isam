from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_interface_cages
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamInterfaceCagesModule(TestIsamModule):
    module = isam_interface_cages

    def setUp(self):
        super(TestIsamInterfaceCagesModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_cages.interface_cages.InterfaceCagesFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def tearDown(self):
        super(TestIsamInterfaceCagesModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_config.stop()

    def test_isam_interface_cages_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        id="1",
                        description="Main cage",
                        apply_qos=True,
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("configure interface cage 1 description Main cage", result["rendered"])
        self.assertIn("configure interface cage 1 apply-qos", result["rendered"])

    def test_isam_interface_cages_rendered_no_qos(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        id="2",
                        description="No QoS cage",
                        apply_qos=False,
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("configure interface cage 2 description No QoS cage", result["rendered"])

    def test_isam_interface_cages_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    configure interface
                      cage 1
                        description Main cage
                        apply-qos
                      exit
                    exit
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["id"], "1")
        self.assertEqual(result["parsed"][0]["description"], "Main cage")
        self.assertTrue(result["parsed"][0]["apply_qos"])

    def test_isam_interface_cages_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure interface
              cage 1
                description Main cage
                apply-qos
              exit
            exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"][0]["id"], "1")
        self.assertEqual(result["gathered"][0]["description"], "Main cage")
        self.assertTrue(result["gathered"][0]["apply_qos"])

    def test_isam_interface_cages_gathered_tuple_response(self):
        """Connection responses wrapped in a tuple (output, error) are unwrapped like in other facts classes."""
        self.get_config.return_value = ("configure interface cage lt:1/1/2:cage:1 operational-mode gpon\n", "")
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [{"id": "lt:1/1/2:cage:1", "operational_mode": "gpon"}])

    def test_isam_interface_cages_parsed_capture_lines(self):
        """Every 'configure interface cage' line of the lab capture is parsed, nothing is dropped."""
        import os

        capture = os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..",
                               "local_captures", "DS-LIN-TEST-01", "info_configure_flat.txt")
        if not os.path.exists(capture):
            self.skipTest("lab capture not available")
        with open(capture) as handle:
            lines = [line.rstrip() for line in handle if line.startswith("configure interface cage ")]
        self.assertTrue(lines)
        set_module_args(dict(state="parsed", running_config="\n".join(lines)), ignore_provider_arg)
        result = self.execute_module(changed=False)
        expected = [{"id": line.split()[3], "operational_mode": line.split()[5]} for line in lines]
        self.assertEqual(sorted(result["parsed"], key=lambda item: item["id"]), sorted(expected, key=lambda item: item["id"]))
