from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_vlan_global
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamVlanGlobalModule(TestIsamModule):
    module = isam_vlan_global

    def setUp(self):
        super(TestIsamVlanGlobalModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlan_global.vlan_global.Isam_vlan_globalFacts.get_config"
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
        super(TestIsamVlanGlobalModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_vlan_global_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    broadcast_frames=dict(drop_unknown_multicast=True),
                    priority_regen=[
                        dict(dot1p=0, regen_dot1p=0),
                        dict(dot1p=1, regen_dot1p=1),
                        dict(dot1p=2, regen_dot1p=2),
                        dict(dot1p=3, regen_dot1p=3),
                        dict(dot1p=4, regen_dot1p=4),
                        dict(dot1p=5, regen_dot1p=5),
                        dict(dot1p=6, regen_dot1p=6),
                        dict(dot1p=7, regen_dot1p=7),
                    ],
                    tpid=dict(value="8100"),
                    vmac_address_format=dict(format="canonical"),
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            sorted(result["rendered"]),
            sorted([
                "configure vlan broadcast-frames drop-unknown-multicast",
                "configure vlan priority-regen dot1p 0 regen-dot1p 0",
                "configure vlan priority-regen dot1p 1 regen-dot1p 1",
                "configure vlan priority-regen dot1p 2 regen-dot1p 2",
                "configure vlan priority-regen dot1p 3 regen-dot1p 3",
                "configure vlan priority-regen dot1p 4 regen-dot1p 4",
                "configure vlan priority-regen dot1p 5 regen-dot1p 5",
                "configure vlan priority-regen dot1p 6 regen-dot1p 6",
                "configure vlan priority-regen dot1p 7 regen-dot1p 7",
                "configure vlan tpid 8100",
                "configure vlan vmac-address-format canonical",
            ]),
        )

    def test_isam_vlan_global_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure
                    vlan
                    broadcast-frames
                      drop-unknown-multicast
                    exit
                    priority-regen dot1p 0 regen-dot1p 0
                    priority-regen dot1p 1 regen-dot1p 1
                    priority-regen dot1p 2 regen-dot1p 2
                    priority-regen dot1p 3 regen-dot1p 3
                    priority-regen dot1p 4 regen-dot1p 4
                    priority-regen dot1p 5 regen-dot1p 5
                    priority-regen dot1p 6 regen-dot1p 6
                    priority-regen dot1p 7 regen-dot1p 7
                    tpid 8100
                    vmac-address-format canonical
                    exit
                    exit
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["parsed"]["broadcast_frames"],
            dict(drop_unknown_multicast=True),
        )
        self.assertEqual(len(result["parsed"]["priority_regen"]), 8)
        self.assertEqual(result["parsed"]["tpid"], dict(value="8100"))
        self.assertEqual(
            result["parsed"]["vmac_address_format"],
            dict(format="canonical"),
        )

    def test_isam_vlan_global_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure
            vlan
            broadcast-frames
              drop-unknown-multicast
            exit
            priority-regen dot1p 0 regen-dot1p 0
            tpid 8100
            vmac-address-format canonical
            exit
            exit
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    broadcast_frames=dict(drop_unknown_multicast=True),
                    priority_regen=[dict(dot1p=0, regen_dot1p=0)],
                    tpid=dict(value="8100"),
                    vmac_address_format=dict(format="canonical"),
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_vlan_global_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure
            vlan
            broadcast-frames
              drop-unknown-multicast
            exit
            priority-regen dot1p 0 regen-dot1p 0
            tpid 88a8
            vmac-address-format non-canonical
            exit
            exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["gathered"]["broadcast_frames"],
            dict(drop_unknown_multicast=True),
        )
        self.assertEqual(result["gathered"]["tpid"], dict(value="88a8"))
        self.assertEqual(
            result["gathered"]["vmac_address_format"],
            dict(format="non-canonical"),
        )
