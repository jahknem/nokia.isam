import os

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_boards
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_boards.xdsl_boards import (
    Xdsl_boardsFacts,
)

from .isam_module import TestIsamModule, set_module_args


class TestIsamXdslBoardsModule(TestIsamModule):
    module = isam_xdsl_boards

    def setUp(self):
        super(TestIsamXdslBoardsModule, self).setUp()
        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_boards.xdsl_boards.Xdsl_boardsFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()
        # The module needs a (mocked) device connection of its own; it used to ride on
        # patches other test classes leaked.
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamXdslBoardsModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_deleted_board_preserves_vp_board_with_same_id(self):
        self.get_config.return_value = "\n".join([
            "configure xdsl board 1/1/1 vce-profile 10",
            "configure xdsl vp-board 1/1/1 admin-state up",
        ])
        set_module_args(
            {"state": "deleted", "config": {"boards": [{"board_id": "1/1/1"}]}},
            True,
        )
        result = self.execute_module(changed=True)
        # a board is reset, not removed ('no board' is an invalid token, lab ISAM)
        self.assertEqual(result["commands"], ["configure xdsl board 1/1/1 no vce-profile"])

    DETAIL = "\n".join([
        "configure xdsl board 1/1/1 no dpbo-profile vce-profile 10 no vplt-autodiscover no vce-capacity-mode"
        " no leg-upbo-profile no vect-class",
        "configure xdsl board 1/1/1 vect-fallback no fb-vplt-com-fail fb-cpe-cap-mism no fb-conf-not-feas"
        " spectrum-profile 7 no service-profile no dpbo-profile no rtx-profile no sos-profile",
        "configure xdsl board 1/1/1 auto-port-reset max-retry-attempt 3 no reset-interval no reset-threshold",
        "configure xdsl board 1/1/4 no dpbo-profile no vce-profile future-knob 4 future-flag no future-off",
        "configure xdsl vp-board 1/1/1 vp-link 1 lt-expect 1/1/4",
        "configure xdsl vp-board 1/1/1 vp-link 2 lt-expect 1/1/3",
        "configure xdsl vp-board 1/1/1 vp-link 3 no lt-expect",
    ])

    def test_parsed_detail_output_drops_defaults_and_unknown_keywords(self):
        set_module_args({"state": "parsed", "running_config": self.DETAIL}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], {
            "boards": [
                {
                    "board_id": "1/1/1",
                    "vce_profile": "10",
                    "vect_fallback": {"fb_cpe_cap_mism": True, "spectrum_profile": "7"},
                    "auto_port_reset": {"max_retry_attempt": 3},
                },
                {"board_id": "1/1/4"},
            ],
            "vp_boards": [
                {
                    "vp_board_id": "1/1/1",
                    "vp_links": [
                        {"link_id": "1", "lt_expect": "1/1/4"},
                        {"link_id": "2", "lt_expect": "1/1/3"},
                    ],
                },
            ],
        })

    def test_indented_output_is_parsed(self):
        running = "\n".join([
            "configure xdsl",
            "#-------",
            "  board 1/1/3",
            "    dpbo-profile 1",
            "    vect-fallback",
            "      fb-vplt-com-fail",
            "    exit",
            "  exit",
            "  vp-board 1/1/1",
            "    vp-link 2",
            "      lt-expect 1/1/3",
            "    exit",
            "  exit",
            "exit",
        ])
        set_module_args({"state": "parsed", "running_config": running}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["boards"], [
            {"board_id": "1/1/3", "dpbo_profile": "1", "vect_fallback": {"fb_vplt_com_fail": True}},
        ])
        self.assertEqual(result["parsed"]["vp_boards"], [
            {"vp_board_id": "1/1/1", "vp_links": [{"link_id": "2", "lt_expect": "1/1/3"}]},
        ])

    def test_rendered_sub_nodes_are_compacted_per_scope(self):
        set_module_args({"state": "rendered", "config": {
            "boards": [{
                "board_id": "1/1/1",
                "dpbo_profile": "1",
                "vce_profile": "10",
                "vect_fallback": {"fb_vplt_com_fail": True, "fb_cpe_cap_mism": False, "dpbo_profile": "2"},
                "auto_port_reset": {"max_retry_attempt": 3, "reset_interval": 60},
            }],
            "vp_boards": [{"vp_board_id": "1/1/1", "vp_links": [
                {"link_id": "1", "lt_expect": "1/1/4"},
                {"link_id": "2", "lt_expect": "1/1/3"},
            ]}],
        }}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], [
            "configure xdsl board 1/1/1 dpbo-profile 1 vce-profile 10",
            "configure xdsl board 1/1/1 vect-fallback fb-vplt-com-fail no fb-cpe-cap-mism dpbo-profile 2",
            "configure xdsl board 1/1/1 auto-port-reset max-retry-attempt 3 reset-interval 60",
            "configure xdsl vp-board 1/1/1 vp-link 1 lt-expect 1/1/4",
            "configure xdsl vp-board 1/1/1 vp-link 2 lt-expect 1/1/3",
        ])

    def test_merged_is_idempotent_against_detail_output(self):
        self.get_config.return_value = self.DETAIL
        set_module_args({"state": "merged", "config": {
            "boards": [{
                "board_id": "1/1/1",
                "vce_profile": "10",
                "vect_fallback": {"fb_cpe_cap_mism": True, "fb_vplt_com_fail": False, "spectrum_profile": "7"},
                "auto_port_reset": {"max_retry_attempt": 3},
            }],
            "vp_boards": [{"vp_board_id": "1/1/1", "vp_links": [{"link_id": "1", "lt_expect": "1/1/4"}]}],
        }}, True)
        self.execute_module(changed=False)

    def test_merged_changes_only_differing_attributes(self):
        self.get_config.return_value = self.DETAIL
        set_module_args({"state": "merged", "config": {
            "boards": [{
                "board_id": "1/1/1",
                "vect_fallback": {"fb_cpe_cap_mism": False},
                "auto_port_reset": {"reset_threshold": 5},
            }],
            "vp_boards": [{"vp_board_id": "1/1/1", "vp_links": [{"link_id": "3", "lt_expect": "1/1/5"}]}],
        }}, True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], [
            "configure xdsl board 1/1/1 vect-fallback no fb-cpe-cap-mism",
            "configure xdsl board 1/1/1 auto-port-reset reset-threshold 5",
            "configure xdsl vp-board 1/1/1 vp-link 3 lt-expect 1/1/5",
        ])

    def test_replaced_removes_unwanted_attributes_with_no_forms(self):
        self.get_config.return_value = self.DETAIL
        set_module_args({"state": "replaced", "config": {
            "boards": [{"board_id": "1/1/1", "vce_profile": "11"}],
            "vp_boards": [{"vp_board_id": "1/1/1", "vp_links": [{"link_id": "1", "lt_expect": "1/1/4"}]}],
        }}, True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], [
            "configure xdsl board 1/1/1 vce-profile 11",
            "configure xdsl board 1/1/1 vect-fallback no fb-cpe-cap-mism no spectrum-profile",
            "configure xdsl board 1/1/1 auto-port-reset no max-retry-attempt",
            "configure xdsl vp-board 1/1/1 vp-link 2 no lt-expect",
        ])

    def test_overridden_removes_unlisted_boards(self):
        self.get_config.return_value = self.DETAIL
        set_module_args({"state": "overridden", "config": {
            "boards": [{
                "board_id": "1/1/1",
                "vce_profile": "10",
                "vect_fallback": {"fb_cpe_cap_mism": True, "spectrum_profile": "7"},
                "auto_port_reset": {"max_retry_attempt": 3},
            }],
            "vp_boards": [{"vp_board_id": "1/1/1", "vp_links": [
                {"link_id": "1", "lt_expect": "1/1/4"},
                {"link_id": "2", "lt_expect": "1/1/3"},
            ]}],
        }}, True)
        # the unlisted board 1/1/4 is reset, not removed; it has nothing but defaults
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_render_parse_round_trip(self):
        config = {
            "boards": [{
                "board_id": "1/1/1",
                "dpbo_profile": "1",
                "vce_profile": "10",
                "vplt_autodiscover": "enable",
                "vce_capacity_mode": "auto",
                "leg_upbo_profile": "3",
                "vect_class": "2",
                "vect_fallback": {
                    "fb_vplt_com_fail": True, "fb_cpe_cap_mism": True, "fb_conf_not_feas": True,
                    "spectrum_profile": "1", "service_profile": "2", "dpbo_profile": "3",
                    "rtx_profile": "4", "sos_profile": "5",
                },
                "auto_port_reset": {"max_retry_attempt": 3, "reset_interval": 60, "reset_threshold": 9},
            }],
            "vp_boards": [{"vp_board_id": "1/1/1", "admin_state": "up", "vp_links": [
                {"link_id": "1", "lt_expect": "1/1/4"},
            ]}],
        }
        set_module_args({"state": "rendered", "config": config}, True)
        rendered = self.execute_module(changed=False)["rendered"]
        set_module_args({"state": "parsed", "running_config": "\n".join(rendered)}, True)
        self.assertEqual(self.execute_module(changed=False)["parsed"], config)


_CAPTURES = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "..", "..", "..", "..", "..", "..",
    "pon-migration-planner", ".local",
)


@pytest.mark.parametrize("capture", ["root-detail-flat.txt", "root-flat.txt"])
def test_lab_capture_xdsl_board_lines_parse_through_facts(capture):
    """Every xdsl board/vp-board line of the lab captures gathers without failure."""
    path = os.path.normpath(os.path.join(_CAPTURES, capture))
    if not os.path.exists(path):
        pytest.skip("lab capture %s not available" % path)
    with open(path) as handle:
        lines = [line.strip() for line in handle
                 if line.strip().startswith(("configure xdsl board ", "configure xdsl vp-board "))]
    assert lines
    facts = Xdsl_boardsFacts(module=None)
    ansible_facts = {"ansible_network_resources": {}}
    facts.populate_facts(None, ansible_facts, data="\n".join(lines))
    gathered = ansible_facts["ansible_network_resources"]["xdsl_boards"]
    boards = dict((board["board_id"], board) for board in gathered["boards"])
    assert boards["1/1/1"]["vce_profile"] == "10"
    assert boards["1/1/3"]["dpbo_profile"] == "1"
    assert gathered["vp_boards"][0]["vp_links"] == [
        {"link_id": "1", "lt_expect": "1/1/4"},
        {"link_id": "2", "lt_expect": "1/1/3"},
    ]
    # Each line also parses on its own (targeted reads return single lines).
    for line in lines:
        single = {"ansible_network_resources": {}}
        facts.populate_facts(None, single, data=line)
