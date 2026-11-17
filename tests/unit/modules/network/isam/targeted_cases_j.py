"""Targeted gathering cases: xDSL impulse noise sensors and xDSL ONT interfaces."""



def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


CASES = {
    "xdsl_inm:near_end": case(
        "isam_xdsl_inm", {"near_end": [{"name": "1/1/3/1"}]},
        ["configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-eq-inp-mode 1 inm-iat-offset 11"],
        {"near_end": [{"name": "1/1/3/2"}]},
        ["configure xdsl imp-noise-sensor near-end 1/1/3/2 inm-eq-inp-mode 2 inm-iat-offset 22"],
        "'11'", "'22'"),
    "xdsl_inm:far_end": case(
        "isam_xdsl_inm", {"far_end": [{"name": "1/1/3/1"}]},
        ["configure xdsl imp-noise-sensor far-end 1/1/3/1 inm-cluster-cont 33"],
        {"far_end": [{"name": "1/1/3/2"}]},
        ["configure xdsl imp-noise-sensor far-end 1/1/3/2 inm-cluster-cont 44"],
        "'33'", "'44'"),
    "xdsl_onts:config": case(
        "isam_xdsl_onts", [{"ont_idx": "1/1/2/1/1"}],
        ["configure xdsl ont interface 1/1/2/1/1 dpbo-profile 5"],
        [{"ont_idx": "1/1/2/1/2"}],
        ["configure xdsl ont interface 1/1/2/1/2 dpbo-profile 6"],
        "1/1/2/1/1", "1/1/2/1/2"),
}
