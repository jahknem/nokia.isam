"""Targeted gathering cases: ONT UNI PM (isam_l2uni_onts, isam_uni_onts)."""



def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


CASES = {
    "l2uni_onts:performance_monitor": case(
        "isam_l2uni_onts", {"performance_monitor": [{"uni_idx": "1/1/2/1/1/1/1"}]},
        ["configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect tca-enable no pm-collect-64bit",
         "configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext pm-collect enable no p-bits vlan-id 100"],
        {"performance_monitor": [{"uni_idx": "1/1/2/1/100/1/1"}]},
        ["configure l2uni ont performance-monitor 1/1/2/1/100/1/1 pm-collect pm-enable no pm-collect-64bit"],
        "1/1/2/1/1/1/1", "1/1/2/1/100/1/1"),
    "l2uni_onts:tc_layer_threshold": case(
        "isam_l2uni_onts", {"tc_layer_threshold": [{"uni_idx": "1/1/2/2/100/1/1"}]},
        ["configure l2uni ont tc-layer-threshold 1/1/2/2/100/1/1 dropped-frames-up 1000 no dropped-frames-dn"],
        {"tc_layer_threshold": [{"uni_idx": "1/1/2/3/100/1/1"}]},
        ["configure l2uni ont tc-layer-threshold 1/1/2/3/100/1/1 no dropped-frames-up dropped-frames-dn 5"],
        "1/1/2/2/100/1/1", "1/1/2/3/100/1/1"),
    "uni_onts": case(
        "isam_uni_onts", [{"uni_idx": "1/1/2/1/1/1/1"}],
        ["configure uni ont tc-layer 1/1/2/1/1/1/1 pm-collect enable"],
        [{"uni_idx": "1/1/2/1/100/1/1"}],
        ["configure uni ont tc-layer 1/1/2/1/100/1/1 pm-collect enable"],
        "1/1/2/1/1/1/1", "1/1/2/1/100/1/1"),
}
