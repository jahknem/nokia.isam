from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_bonding
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamXdslBondingModule(TestIsamModule):
    module = isam_xdsl_bonding

    def setUp(self):
        super(TestIsamXdslBondingModule, self).setUp()

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
        super(TestIsamXdslBondingModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_xdsl_bonding_parsed_flat(self):
        running = dedent(
            """
            configure xdsl-bonding group-assembly-time 50
            """
        )
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["group_assembly_time"], 50)

    def test_isam_xdsl_bonding_gathered_hierarchical(self):
        sample = dedent(
            """
            configure xdsl-bonding
              group-assembly-time 50
            exit
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["group_assembly_time"], 50)

    def test_isam_xdsl_bonding_rendered(self):
        set_module_args(
            dict(
                config=dict(group_assembly_time=50),
                state="rendered",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure xdsl-bonding group-assembly-time 50"],
        )

    def test_isam_xdsl_bonding_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)

    def test_isam_xdsl_bonding_merged(self):
        set_module_args(
            dict(
                config=dict(group_assembly_time=50),
                state="merged",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure xdsl-bonding group-assembly-time 50"],
        )

    def test_isam_xdsl_bonding_deleted(self):
        sample = dedent(
            """
            configure xdsl-bonding
              group-assembly-time 50
            exit
            """
        )

        class FakeConn:
            def get(self, cmd):
                return sample

        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(
            dict(
                config=dict(group_assembly_time=50),
                state="deleted",
            ),
            ignore_provider_arg,
        )

        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure xdsl-bonding no group-assembly-time"],
        )
