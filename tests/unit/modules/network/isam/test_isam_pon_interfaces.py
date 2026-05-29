from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_pon_interfaces
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamPonInterfacesModule(TestIsamModule):
    module = isam_pon_interfaces

    def setUp(self):
        super(TestIsamPonInterfacesModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces.Pon_interfacesFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

    def tearDown(self):
        super(TestIsamPonInterfacesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()

    def test_isam_pon_interfaces_rendered(self):
        set_module_args(
            dict(
                config=[
                    dict(
                        name="1/1/1/1",
                        label="access-pon-1",
                        fec_dn="enable",
                        ponid_interval=10,
                        ponid_identifier="00000000000001",
                        tconts_per_frame=44,
                        admin_state="down",
                        tc_layer=dict(pm_collect="tca-enable"),
                    )
                ],
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertIn("configure pon interface 1/1/1/1 label access-pon-1", result["rendered"])
        self.assertIn("configure pon interface 1/1/1/1 tc-layer pm-collect tca-enable", result["rendered"])

    def test_isam_pon_interfaces_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    configure pon
                      interface 1/1/1/1
                        label access-pon-1
                        fec-dn enable
                        ponid-interval 10
                        ponid-identifier 00000000000001
                        tconts-per-frame 44
                        admin-state down
                        tc-layer
                          pm-collect tca-enable
                        exit
                      exit
                    exit
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"][0]["name"], "1/1/1/1")
        self.assertEqual(result["parsed"][0]["tc_layer"]["pm_collect"], "tca-enable")
