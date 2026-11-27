import os
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
        self.mock_get_resource_connection.stop()
        self.mock_get_config.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_isam_vlan_global_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    broadcast_frames=dict(drop_unknown_multicast=True),
                    priority_regen=[
                        dict(id=1, profile_name="TrustedPort", pbit0=0, pbit1=1, pbit2=2, pbit3=3,
                             pbit4=4, pbit5=5, pbit6=6, pbit7=7),
                        dict(id=11, profile_name="Custom"),
                        dict(id=12, pbit6=6, pbit7=6),
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
                "configure vlan priority-regen 1 profile-name TrustedPort pbit0 0 pbit1 1 pbit2 2 pbit3 3 pbit4 4 pbit5 5 pbit6 6 pbit7 7",
                "configure vlan priority-regen 11 profile-name Custom",
                "configure vlan priority-regen 12 pbit6 6 pbit7 6",
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
                    priority-regen 1 profile-name TrustedPort pbit0 0 pbit1 1 pbit2 2 pbit3 3 pbit4 4 pbit5 5 pbit6 6 pbit7 7
                    priority-regen 2 profile-name BestEffort pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 0 pbit7 0
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
        self.assertEqual(result["parsed"]["broadcast_frames"], dict(drop_unknown_multicast=True))
        self.assertEqual(
            result["parsed"]["priority_regen"],
            [
                dict(id=1, profile_name="TrustedPort", pbit0=0, pbit1=1, pbit2=2, pbit3=3, pbit4=4, pbit5=5, pbit6=6, pbit7=7),
                dict(id=2, profile_name="BestEffort", pbit0=0, pbit1=0, pbit2=0, pbit3=0, pbit4=0, pbit5=0, pbit6=0, pbit7=0),
            ],
        )
        self.assertEqual(result["parsed"]["tpid"], dict(value="8100"))
        self.assertEqual(result["parsed"]["vmac_address_format"], dict(format="canonical"))

    def test_isam_vlan_global_parsed_capture_priority_regen_lines(self):
        """Every 'configure vlan priority-regen' line of the lab capture is parsed completely."""
        from . import lab_captures

        lines = [line.rstrip() for line in lab_captures.configured().splitlines() if line.startswith("configure vlan priority-regen ")]
        self.assertTrue(lines)
        set_module_args(dict(state="parsed", running_config="\n".join(lines)), ignore_provider_arg)
        result = self.execute_module(changed=False)
        entries = result["parsed"]["priority_regen"]
        self.assertEqual(len(entries), len(lines))
        for line, entry in zip(lines, entries):
            tokens = line.split()
            expected = dict(id=int(tokens[3]), profile_name=tokens[5])
            expected.update((tokens[i], int(tokens[i + 1])) for i in range(6, len(tokens), 2))
            self.assertEqual(entry, expected)
        # and the parsed entries render back to exactly the device lines
        set_module_args(dict(state="rendered", config=dict(priority_regen=entries)), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        self.assertEqual(sorted(rendered), sorted(lines))

    def test_isam_vlan_global_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure vlan broadcast-frames drop-unknown-multicast
            configure vlan priority-regen 2 profile-name BestEffort pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 0 pbit7 0
            configure vlan tpid 8100
            configure vlan vmac-address-format canonical
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    broadcast_frames=dict(drop_unknown_multicast=True),
                    priority_regen=[dict(id=2, profile_name="BestEffort", pbit6=0)],
                    tpid=dict(value="8100"),
                    vmac_address_format=dict(format="canonical"),
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_isam_vlan_global_merged_changes_pbit(self):
        self.get_config.return_value = (
            "configure vlan priority-regen 2 profile-name BestEffort pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 0 pbit7 0\n"
        )
        set_module_args(dict(state="merged", config=dict(priority_regen=[dict(id=2, pbit6=6)])), ignore_provider_arg)
        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure vlan priority-regen 2 profile-name BestEffort pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 6 pbit7 0"],
        )

    def test_isam_vlan_global_deleted_and_overridden_remove_profile(self):
        self.get_config.return_value = dedent(
            """\
            configure vlan priority-regen 2 profile-name BestEffort pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 0 pbit7 0
            configure vlan priority-regen 11 profile-name Custom pbit0 1 pbit1 1 pbit2 1 pbit3 1 pbit4 1 pbit5 1 pbit6 1 pbit7 1
            """
        )
        set_module_args(dict(state="deleted", config=dict(priority_regen=[dict(id=11)])), ignore_provider_arg)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure vlan no priority-regen 11"])

        set_module_args(
            dict(state="overridden", config=dict(priority_regen=[
                dict(id=2, profile_name="BestEffort", pbit0=0, pbit1=0, pbit2=0, pbit3=0, pbit4=0, pbit5=0, pbit6=0, pbit7=0),
            ])),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure vlan no priority-regen 11"])

    def test_isam_vlan_global_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure
            vlan
            broadcast-frames
              drop-unknown-multicast
            exit
            priority-regen 3 profile-name ControlledLoad3 pbit0 3 pbit1 3 pbit2 3 pbit3 3 pbit4 3 pbit5 3 pbit6 3 pbit7 3
            tpid 88a8
            vmac-address-format non-canonical
            exit
            exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["broadcast_frames"], dict(drop_unknown_multicast=True))
        self.assertEqual(result["gathered"]["priority_regen"][0]["id"], 3)
        self.assertEqual(result["gathered"]["priority_regen"][0]["profile_name"], "ControlledLoad3")
        self.assertEqual(result["gathered"]["tpid"], dict(value="88a8"))
        self.assertEqual(result["gathered"]["vmac_address_format"], dict(format="non-canonical"))

    def test_isam_vlan_global_old_dot1p_form_is_not_parsed(self):
        """The former invented 'priority-regen dot1p N regen-dot1p M' form is not a device form."""
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure vlan
                    priority-regen dot1p 3 regen-dot1p 3
                    no tpid
                    no vmac-address-format
                    exit
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertNotIn("priority_regen", result["parsed"])
        self.assertNotIn("tpid", result["parsed"])
        self.assertNotIn("vmac_address_format", result["parsed"])
