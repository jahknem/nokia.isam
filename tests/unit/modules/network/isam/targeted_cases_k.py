"""Targeted gathering cases: equipment ONT loop detection and XGS-PON PM collection."""


ONT, SIB = "1/1/5/1/3", "1/1/5/1/30"


def ont_case(module, make_config, make_lines):
    # The ONT index is a prefix of its neighbour's: match it with the opening quote.
    return {"module": module, "config": make_config(ONT), "lines": make_lines(ONT),
            "sibling_config": make_config(SIB), "sibling": make_lines(SIB),
            "marker": "'%s" % ONT, "sibling_marker": "'%s" % SIB}


CASES = {
    "equipment_onts:loops": ont_case(
        "isam_equipment_onts", lambda o: {"loops": [{"ont_idx": o}]},
        lambda o: ["configure equipment ont loop %s loop-detect enable loop-portautoshut disable" % o]),
    "equipment_onts:pm_collects": ont_case(
        "isam_equipment_onts", lambda o: {"pm_collects": [{"ont_idx": o}]},
        lambda o: ["configure equipment ont pm-collect %s xg-pm-collect enable" % o]),
}
