"""Targeted gathering cases: per-queue QoS TCA (composite name+queue identity)."""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


CASES = {
    "qos_tca:config": case(
        "isam_qos_tca",
        [{"name": "1/1/5/1/3/1/1", "queue": 0}],
        ["configure qos tca 1/1/5/1/3/1/1 queue 0 tca-enable load-thresh 80"],
        [{"name": "1/1/5/1/3/1/1", "queue": 1}],
        ["configure qos tca 1/1/5/1/3/1/1 queue 1 tca-enable load-thresh 90"],
        "'queue': 0", "'queue': 1",
    ),
}
