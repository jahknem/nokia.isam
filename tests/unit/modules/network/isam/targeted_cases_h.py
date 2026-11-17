"""Targeted gathering cases: igmp / mcast-control packages (isam_igmp, isam_mcast_control, isam_multicast)."""




def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


def _lines(family, index, name):
    return ["configure %s package %s name %s template-name tmpl-%s template-version 3" % (family, index, name, name)]


CASES = {
    "igmp:packages": case(
        "isam_igmp", {"packages": [{"index": 5}]}, _lines("igmp", 5, "basic"),
        {"packages": [{"index": 50}]}, _lines("igmp", 50, "premium"), "basic", "premium"),
    "mcast_control:packages": case(
        "isam_mcast_control", {"packages": [{"index": 5}]}, _lines("mcast-control", 5, "basic"),
        {"packages": [{"index": 50}]}, _lines("mcast-control", 50, "premium"), "basic", "premium"),
    "multicast:igmp.packages": case(
        "isam_multicast", {"igmp": {"packages": [{"index": 5}]}}, _lines("igmp", 5, "basic"),
        {"igmp": {"packages": [{"index": 50}]}}, _lines("igmp", 50, "premium"), "basic", "premium"),
    "multicast:mcast_control.packages": case(
        "isam_multicast", {"mcast_control": {"packages": [{"index": 5}]}}, _lines("mcast-control", 5, "basic"),
        {"mcast_control": {"packages": [{"index": 50}]}}, _lines("mcast-control", 50, "premium"), "basic", "premium"),
}
