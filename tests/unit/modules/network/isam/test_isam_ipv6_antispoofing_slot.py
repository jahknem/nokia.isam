from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_ipv6_antispoofing_slot

from .isam_module import TestIsamModule, set_module_args


class TestIsamIpv6AntispoofingSlot(TestIsamModule):
    module = isam_ipv6_antispoofing_slot

    def test_rendered(self):
        set_module_args(
            {"state": "rendered", "config": [{"name": "1/1/1", "bit_len": 72}]},
            True,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure ipv6-antispoofing slot 1/1/1 bit-len 72"],
        )

    def test_parsed_flat_and_indented(self):
        set_module_args(
            {
                "state": "parsed",
                "running_config": dedent(
                    """\
                    configure ipv6-antispoofing slot 1/1/1 bit-len 72
                    configure ipv6-antispoofing
                      slot 1/1/2
                        bit-len 96
                    """
                ),
            },
            True,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["parsed"],
            [{"name": "1/1/1", "bit_len": 72}, {"name": "1/1/2", "bit_len": 96}],
        )

    def test_bit_len_range_is_enforced(self):
        for bit_len in (63, 129, 0):
            set_module_args({"state": "rendered", "config": [{"name": "1/1/1", "bit_len": bit_len}]}, True)
            result = self.execute_module(failed=True)
            self.assertIn("between 64 and 128", result["msg"])

    def test_bit_len_range_bounds_are_accepted(self):
        set_module_args(
            {"state": "rendered", "config": [{"name": "1/1/1", "bit_len": 64}, {"name": "1/1/2", "bit_len": 128}]},
            True,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            sorted(result["rendered"]),
            ["configure ipv6-antispoofing slot 1/1/1 bit-len 64", "configure ipv6-antispoofing slot 1/1/2 bit-len 128"],
        )

    def test_argspec_has_no_unsupported_keys(self):
        from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ipv6_antispoofing_slot.ipv6_antispoofing_slot import (
            Isam_ipv6_antispoofing_slotArgs,
        )

        bit_len = Isam_ipv6_antispoofing_slotArgs.argument_spec["config"]["options"]["bit_len"]
        self.assertFalse({"min", "max"} & set(bit_len))
