from ansible_collections.nokia.isam.plugins.modules import isam_facts
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIsamFactsModule(TestIsamModule):
    module = isam_facts

    def setUp(self):
        super(TestIsamFactsModule, self).setUp()
        # Patch the resource connection used by facts to avoid real device calls
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

        class FakeConn:
            def get(self, cmd):
                # Return empty outputs for any resource request
                return ""

        self.fake_conn = FakeConn()
        self.get_resource_connection_facts.return_value = self.fake_conn

    def tearDown(self):
        super(TestIsamFactsModule, self).tearDown()
        self.get_resource_connection_facts.stop()

    def test_isam_facts_minimal_interfaces(self):
        # Gather only interfaces to keep scope small and deterministic
        set_module_args(
            dict(
                gather_network_resources=["interfaces"],
            )
        )

        result = self.execute_module(changed=False)
        self.assertIn("ansible_facts", result)
        af = result["ansible_facts"]
        self.assertIn("ansible_network_resources", af)
        anr = af["ansible_network_resources"]
        # interfaces key should be present and a list (empty due to fake conn)
        self.assertIn("interfaces", anr)
        self.assertIsInstance(anr["interfaces"], list)
        self.assertEqual(anr["interfaces"], [])
