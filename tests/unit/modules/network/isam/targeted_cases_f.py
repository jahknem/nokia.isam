"""Targeted gathering cases: system security (operator / SNMP view / RADIUS auth-server)."""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


CASES = {
    "isam_system_security:operators": case(
        "isam_system_security", {"operators": [{"name": "isadmin"}]},
        ["configure system security operator isadmin profile admin"],
        {"operators": [{"name": "ypmonitor"}]},
        ["configure system security operator ypmonitor profile ypmonprofil"],
        "isadmin", "ypmonitor"),
    "isam_system_security:snmp_views": case(
        "isam_system_security", {"snmp_views": [{"name": "everything"}]},
        ["configure system security snmp view everything subtree * type include"],
        {"snmp_views": [{"name": "nothing"}]},
        ["configure system security snmp view nothing subtree * type exclude"],
        "everything", "nothing"),
    "isam_system_security:radius_auth_servers": case(
        "isam_system_security", {"radius_auth_servers": [{"name": "RAD1"}]},
        ["configure system security radius auth-server RAD1 ip-address 10.0.0.1 timeout-limit 5"],
        {"radius_auth_servers": [{"name": "RAD2"}]},
        ["configure system security radius auth-server RAD2 ip-address 10.0.0.2 timeout-limit 6"],
        "RAD1", "RAD2"),
}

CASES.update({
    "isam_system_security:profiles": case(
        "isam_system_security", {"profiles": [{"name": "admin"}]},
        ["configure system security profile admin description admin-group aaa write"],
        {"profiles": [{"name": "ypmonprofil"}]},
        ["configure system security profile ypmonprofil description monitor aaa read"],
        "admin-group", "monitor"),
    "isam_system_security:snmp_communities": case(
        "isam_system_security", {"snmp_communities": [{"name": "comm-a"}]},
        ["configure system security snmp community comm-a host-address 10.0.0.1/32"],
        {"snmp_communities": [{"name": "comm-b"}]},
        ["configure system security snmp community comm-b host-address 10.0.0.2/32"],
        "10.0.0.1/32", "10.0.0.2/32"),
    "isam_system_security:snmp_managers": case(
        "isam_system_security", {"snmp_managers": [{"name": "mgr-a"}]},
        ["configure system security snmp manager mgr-a destination 127.0.0.1:161 nt"],
        {"snmp_managers": [{"name": "mgr-b"}]},
        ["configure system security snmp manager mgr-b destination 127.0.0.2:161 nt"],
        "127.0.0.1:161", "127.0.0.2:161"),
    "isam_system_security:snmp_notify_profiles": case(
        "isam_system_security", {"snmp_notify_profiles": [{"name": "np-a"}]},
        ["configure system security snmp notify-profile np-a snmp-version v2c:comm"],
        {"snmp_notify_profiles": [{"name": "np-b"}]},
        ["configure system security snmp notify-profile np-b snmp-version v3:other"],
        "np-a", "np-b"),
    "isam_system_security:radius_policies": case(
        "isam_system_security", {"radius_policies": [{"name": "PolA"}]},
        ["configure system security radius policy PolA nas-id iSAM-A"],
        {"radius_policies": [{"name": "PolB"}]},
        ["configure system security radius policy PolB nas-id iSAM-B"],
        "iSAM-A", "iSAM-B"),
    "isam_system_security:radius_dyn_auth_clients": case(
        "isam_system_security", {"radius_dyn_auth_clients": [{"name": "DynA"}]},
        ["configure system security radius dyn-auth-client DynA ip-address 10.0.0.1"],
        {"radius_dyn_auth_clients": [{"name": "DynB"}]},
        ["configure system security radius dyn-auth-client DynB ip-address 10.0.0.2"],
        "DynA", "DynB"),
})
