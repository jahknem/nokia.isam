"""Targeted gathering cases: QoS maps and profiles, VLANs, xSTP, link aggregation,
distributed services and IPv6 antispoofing slots."""

import re


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker, answer=None):
    built = {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
             "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}
    if answer is not None:
        built["answer"] = answer
    return built


_IPV6_SLOT = re.compile(r"^info configure ipv6-antispoofing slot(?: (\S+))?$")


def ipv6_antispoofing_answer(command, lines):
    """Hierarchical output (the module reads it without flat).

    Whole resource: the ipv6-antispoofing block with all slots. One slot: the block
    of that slot. None when nothing matches.
    """
    match = _IPV6_SLOT.match(command)
    assert match, command
    slots = {}
    for line in lines:
        tokens = line.split()
        slots.setdefault(tokens[3], []).append(" ".join(tokens[4:]))
    slot = match.group(1)
    if slot is None:
        out = ["configure ipv6-antispoofing"]
        for name, attributes in slots.items():
            out += ["  slot %s" % name] + ["    %s" % attribute for attribute in attributes] + ["  exit"]
        return "\n".join(out + ["exit"]) + "\n"
    if slot not in slots:
        return None
    return "\n".join(["configure ipv6-antispoofing slot %s" % slot] + ["  %s" % a for a in slots[slot]] + ["exit"]) + "\n"


CASES = {
    "qos_maps:tc_map_dot1p": case("isam_qos_maps", {"tc_map_dot1p": [{"dot1p": 3}]},
                                  ["configure qos tc-map-dot1p 3 tc 5 dpcolor green"],
                                  {"tc_map_dot1p": [{"dot1p": 4}]},
                                  ["configure qos tc-map-dot1p 4 tc 6 dpcolor yellow"], "green", "yellow"),
    "qos_maps:dscp_map_dot1p": case("isam_qos_maps", {"dscp_map_dot1p": [{"dscp": "af11"}]},
                                    ["configure qos dscp-map-dot1p af11 dot1p 1"],
                                    {"dscp_map_dot1p": [{"dscp": "af41"}]},
                                    ["configure qos dscp-map-dot1p af41 dot1p 4"], "'af11'", "'af41'"),
    "qos_maps:up_ctrl_pkt": case("isam_qos_maps", {"up_ctrl_pkt": [{"protocol": "dhcp"}]},
                                 ["configure qos up-ctrl-pkt dhcp dscp 46 pbit 5 tc 7"],
                                 {"up_ctrl_pkt": [{"protocol": "pppoe"}]},
                                 ["configure qos up-ctrl-pkt pppoe dscp 48 pbit 6 tc 6"], "'dscp': 46", "'dscp': 48"),
    "qos_maps:dn_ctrl_pkt": case("isam_qos_maps", {"dn_ctrl_pkt": [{"protocol": "igmp"}]},
                                 ["configure qos dn-ctrl-pkt igmp dscp 46 tc 7"],
                                 {"dn_ctrl_pkt": [{"protocol": "arp"}]},
                                 ["configure qos dn-ctrl-pkt arp dscp 48 tc 6"], "'dscp': 46", "'dscp': 48"),
    # Composite identity; the neighbour is a marker profile ("marker d1p <name>" on the CLI).
    "qos_profiles": case("isam_qos_profiles", [{"profile_type": "scheduler-node", "name": "SN_Alpha"}],
                         ["configure qos profiles scheduler-node SN_Alpha priority 1 weight 10"],
                         [{"profile_type": "marker-d1p", "name": "MK_Beta"}],
                         ["configure qos profiles marker d1p MK_Beta default-dot1p 5"], "SN_Alpha", "MK_Beta"),
    "vlans": case("isam_vlans", [{"id": "100"}],
                  ["configure vlan id 100 mode residential-bridge name VLAN_Alpha"],
                  [{"id": "1000"}],
                  ["configure vlan id 1000 mode residential-bridge name VLAN_Beta"], "VLAN_Alpha", "VLAN_Beta"),
    # The neighbour is named by the alias "id" of "port".
    "xstp": case("isam_xstp", {"ports": [{"port": "vlan-port:1/1/8/1"}]},
                 ["configure xstp port vlan-port:1/1/8/1 path-cost 20000"],
                 {"ports": [{"id": "vlan-port:1/1/8/10"}]},
                 ["configure xstp port vlan-port:1/1/8/10 path-cost 30000"], "20000", "30000"),
    "link_agg:groups": case("isam_link_agg", {"groups": [{"id": "1/1/8/10"}]},
                            ["configure link-agg group 1/1/8/10 load-sharing-policy mac-src-dst mode dynamic"],
                            {"groups": [{"id": "1/1/8/11"}]},
                            ["configure link-agg group 1/1/8/11 load-sharing-policy mac-src-dst mode static"],
                            "'1/1/8/10'", "'1/1/8/11'"),
    "link_agg:ports": case("isam_link_agg", {"ports": [{"id": "1/1/8/2"}]},
                           ["configure link-agg port 1/1/8/2 passive-lacp short-timeout"],
                           {"ports": [{"id": "1/1/8/3"}]},
                           ["configure link-agg port 1/1/8/3 actor-port-prio 200"], "'1/1/8/2'", "'1/1/8/3'"),
    "isam_dist_service": case("isam_dist_service", [{"name": "100"}],
                              ["configure dist-service 100 service-type epipe qos-profile gold"],
                              [{"name": "101"}],
                              ["configure dist-service 101 service-type tls qos-profile silver"], "gold", "silver"),
    "isam_ipv6_antispoofing_slot": case("isam_ipv6_antispoofing_slot", [{"name": "1/1/5"}],
                                        ["configure ipv6-antispoofing slot 1/1/5 bit-len 72"],
                                        [{"name": "1/1/50"}],
                                        ["configure ipv6-antispoofing slot 1/1/50 bit-len 96"],
                                        "'bit_len': 72", "'bit_len': 96", ipv6_antispoofing_answer),
}
