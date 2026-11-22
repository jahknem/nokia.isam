"""Targeted gathering cases: whole-node catalog families.

These instance lists have no single-instance read: the device only answers the
whole node. A targeted request reads the node once and reports per-instance
outcomes from the parsed catalog; the gathered string is the full catalog
(targeted_harness.run_whole_node).
"""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker,
            "whole_node": True}


CASES = {
    "interface_alarms:config": case(
        "isam_interface_alarms", [{"name": "epon"}],
        ["configure interface alarm epon default-severity indeterminate"],
        [{"name": "eont"}],
        ["configure interface alarm eont default-severity major"],
        "epon", "eont"),
    "isam_vlan_global:priority_regen": case(
        "isam_vlan_global",
        {"priority_regen": [{"id": 100, "profile_name": "ProfileA"}]},
        ["configure vlan priority-regen 100 profile-name ProfileA pbit0 0 pbit1 1 pbit2 2 pbit3 3 pbit4 4 pbit5 5 pbit6 6 pbit7 7"],
        {"priority_regen": [{"id": 200, "profile_name": "ProfileB"}]},
        ["configure vlan priority-regen 200 profile-name ProfileB pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 0 pbit7 0"],
        "100", "200"),
}
