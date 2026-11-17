"""Targeted gathering cases: PON trouble-shooting counters and thresholds."""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


CASES = {
    "trouble_shooting_pon:interfaces": case(
        "isam_trouble_shooting_pon", {"interfaces": [{"name": "1/1/2/1"}]},
        ["configure trouble-shooting pon statistics interface 1/1/2/1"],
        {"interfaces": [{"name": "1/1/2/2"}]},
        ["configure trouble-shooting pon statistics interface 1/1/2/2"],
        "1/1/2/1", "1/1/2/2"),
    "trouble_shooting_pon:threshold.interfaces": case(
        "isam_trouble_shooting_pon", {"threshold": {"interfaces": [{"name": "1/1/2/1"}]}},
        ["configure trouble-shooting pon statistics threshold interface 1/1/2/1 bw-th-up 1111 no bw-th-dn"],
        {"threshold": {"interfaces": [{"name": "1/1/2/2"}]}},
        ["configure trouble-shooting pon statistics threshold interface 1/1/2/2 no bw-th-up bw-th-dn 2222"],
        "1111", "2222"),
}
