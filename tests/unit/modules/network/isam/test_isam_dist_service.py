from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_dist_service
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIsamDistServiceModule(TestIsamModule):
    module = isam_dist_service

    def setUp(self):
        super(TestIsamDistServiceModule, self).setUp()
        self.connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        ).start()
        self.get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dist_service.dist_service.Isam_dist_serviceFacts.get_config"
        ).start()

    def tearDown(self):
        super(TestIsamDistServiceModule, self).tearDown()
        patch.stopall()

    def test_rendered(self):
        set_module_args(dict(state="rendered", config=[dict(name="100", service_type="epipe", qos_profile="gold")]), True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure dist-service 100 service-type epipe", "configure dist-service 100 qos-profile gold"])

    def test_parsed_flat_and_defaults(self):
        set_module_args(dict(state="parsed", running_config=dedent("""\
            configure dist-service 100 service-type epipe
            configure dist-service 100 qos-profile gold
            configure dist-service 101 no qos-profile
        """)), True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [dict(name="100", service_type="epipe", qos_profile="gold"), dict(name="101", service_type="apipe", qos_profile="none")])

    def test_gathered_hierarchical_config(self):
        self.get_config.return_value = dedent("""\
            configure dist-service 100
              service-type epipe
              qos-profile gold
            exit
        """)
        set_module_args(dict(state="gathered"), True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"], [dict(name="100", service_type="epipe", qos_profile="gold")])

    def test_merged_check_mode(self):
        self.get_config.return_value = "configure dist-service 100 service-type epipe"
        set_module_args(dict(state="merged", config=[dict(name="100", service_type="epipe", qos_profile="gold")]), True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure dist-service 100 qos-profile gold"])

    def test_deleted_check_mode(self):
        self.get_config.return_value = "configure dist-service 100 service-type epipe\nconfigure dist-service 100 qos-profile gold"
        set_module_args(dict(state="deleted", config=[dict(name="100")]), True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["no configure dist-service 100 no service-type", "no configure dist-service 100 no qos-profile"])
