from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_li_vlan
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamLiVlanModule(TestIsamModule):
    module = isam_li_vlan

    def setUp(self):
        super(TestIsamLiVlanModule, self).setUp()

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
        super(TestIsamLiVlanModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_li_vlan_parsed(self):
        running = dedent(
            """\
            configure li_vlan vlan-id 100
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["vlan_id"], 100)

    def test_isam_li_vlan_gathered(self):
        sample = dedent(
            """\
            configure li_vlan vlan-id 200
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["vlan_id"], 200)

    def test_isam_li_vlan_rendered(self):
        set_module_args(
            dict(
                config=dict(vlan_id=100),
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure li_vlan vlan-id 100"],
        )

    def test_isam_li_vlan_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)
