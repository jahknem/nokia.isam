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
