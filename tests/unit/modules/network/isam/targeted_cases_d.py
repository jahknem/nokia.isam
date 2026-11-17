"""Targeted gathering cases: PON variants, L2CP, CFM, PPPoE client and PPPoE-L2 resources."""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


def pm(domain, mac):
    return "configure cfm y1731pm domain %s association 2 mep 7 session-id 1 type slm target-mac %s priority 5" % (domain, mac)


CASES = {
    "channel_pair_pm": case(
        "isam_channel_pair_pm", [{"name": "1/1/5/3"}],
        ["configure channel-pair interface 1/1/5/3 fec-tc-layer pm-collect enable",
         "configure channel-pair interface 1/1/5/3 xg-tc-layer pm-collect disable"],
        [{"name": "1/1/5/30"}],
        ["configure channel-pair interface 1/1/5/30 fec-tc-layer pm-collect enable"],
        "1/1/5/3'", "1/1/5/30'"),
    "epon_interfaces": case(
        "isam_epon_interfaces", [{"name": "1/1/6/3"}],
        ["configure epon interface 1/1/6/3 polling-period 10", "configure epon interface 1/1/6/3 admin-state up"],
        [{"name": "1/1/6/30"}],
        ["configure epon interface 1/1/6/30 polling-period 20"],
        "1/1/6/3'", "1/1/6/30'"),
    "ngpon2_channel_groups": case(
        "isam_ngpon2_channel_groups", [{"id": 3}],
        ["configure channel-group id 3 name cg-alpha",
         "configure channel-group id 3 channel-pair 1/1/8/1",
         "configure channel-group id 3 subchannel-group id 1 name scg-alpha",
         "configure channel-group id 3 subchannel-group id 1 channel-pair 1/1/8/1"],
        [{"id": 30}],
        ["configure channel-group id 30 name cg-omega"],
        "scg-alpha", "cg-omega"),
    "l2cp_session": case(
        "isam_l2cp_session", [{"name": "3"}],
        ["configure l2cp session 3 bras-ip-address 192.0.2.10 alive-timer 250"],
        [{"name": "30"}],
        ["configure l2cp session 30 bras-ip-address 192.0.2.99 alive-timer 300"],
        "192.0.2.10", "192.0.2.99"),
    "l2cp_user_port": case(
        "isam_l2cp_user_port", [{"name": "1/1/7/3"}],
        ["configure l2cp user-port 1/1/7/3 partition-id 7"],
        [{"name": "1/1/7/30"}],
        ["configure l2cp user-port 1/1/7/30 partition-id 9"],
        "1/1/7/3'", "1/1/7/30'"),
    "isam_cfm:domains": case(
        "isam_cfm", {"domains": [{"domain_index": 3}]},
        ["configure cfm domain 3 name dom-alpha level 3",
         "configure cfm domain 3 association 2 mep 7 location slot:1/1/1 cci-enable"],
        {"domains": [{"domain_index": 30}]},
        ["configure cfm domain 30 name dom-omega level 5"],
        "dom-alpha", "dom-omega"),
    "isam_cfm:y1731pm": case(
        "isam_cfm", {"y1731pm": [{"domain_index": 3, "association": 2, "mep": 7, "session_id": 1}]},
        [pm(3, "00:11:22:33:44:55")],
        {"y1731pm": [{"domain_index": 30, "association": 2, "mep": 7, "session_id": 1}]},
        [pm(30, "00:11:22:33:44:66")],
        "00:11:22:33:44:55", "00:11:22:33:44:66"),
    "pppoe_client_interface": case(
        "isam_pppoe_client_interface", [{"name": "1/1/1/1/3:100"}],
        ["configure pppoe-client interface 1/1/1/1/3:100 client-id 1 profile-name prof-alpha username alice pbit 3"],
        [{"name": "1/1/1/1/30:100"}],
        ["configure pppoe-client interface 1/1/1/1/30:100 client-id 2 profile-name prof-omega username bobby pbit 5"],
        "alice", "bobby"),
    "pppoe_client_ppp_profile": case(
        "isam_pppoe_client_ppp_profile", [{"name": "prof-alpha"}],
        ["configure pppoe-client ppp-profile prof-alpha ipversion dual authproto pap mru 1492"],
        [{"name": "prof-omega"}],
        ["configure pppoe-client ppp-profile prof-omega ipversion ipv4 authproto chap mru 1400"],
        "prof-alpha", "prof-omega"),
    "pppoel2_statistics": case(
        "isam_pppoel2_statistics", [{"name": "vlan-port:1/1/1/1/3:100"}],
        ["configure pppoel2 statistics vlan-port:1/1/1/1/3:100"],
        [{"name": "vlan-port:1/1/1/1/30:100"}],
        ["configure pppoel2 statistics vlan-port:1/1/1/1/30:100"],
        "1/1/1/1/3:100", "1/1/1/1/30:100"),
}
