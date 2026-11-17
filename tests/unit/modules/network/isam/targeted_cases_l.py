"""Targeted gathering cases: global QoS settings (per line card ``configure qos global <lt>``)."""






def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


CASES = {
    "qos_global:line_cards": case(
        "isam_qos_global", {"line_cards": [{"name": "lt:1/1/2"}]},
        ["configure qos global lt:1/1/2 queue-stats dsload-thresh 31"],
        {"line_cards": [{"name": "lt:1/1/3"}]},
        ["configure qos global lt:1/1/3 buffer-tca dsload-thresh 47"],
        "lt:1/1/2", "lt:1/1/3"),
}
