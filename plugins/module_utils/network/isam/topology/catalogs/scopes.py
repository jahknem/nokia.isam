"""Configuration scope classification for resource sections.

Not all configuration belongs to a physical descendant subtree. This catalog
classifies every TARGETED_GATHER section into one of three scopes so consumers
know where it belongs and never attach it to a guessed physical parent:

* ``object_owned``: instance configuration owned by a physical object (bound in
  the domain catalogs via BINDINGS). Recursive refresh reads it per descendant.
* ``device_global``: device-wide settings with no physical owner (system,
  security, software, alarms, traps, global QoS maps, ...). A full-MSAN refresh
  reads it once; a scoped subtree refresh does not claim it.
* ``shared_profile``: named definitions referenced by object configuration
  (xDSL/QoS/voice profiles). Read once and deduplicated; following a reference
  must not pull in the profile's other consumers.

This is a classification, not a parent/child edge. Physical bindings imply
``object_owned`` unless explicitly declared shared definitions; pending object
bindings and nonphysical scopes are listed here explicitly.
A section absent from both is an unclassified gap, never silently device-global.
"""

# resource -> {section: scope}. Only device_global and shared_profile are listed;
# object_owned is derived from physical BINDINGS, with explicit profile scopes.
DEVICE_GLOBAL = {
    "alarm": ("custom_profiles", "entries", "filters", "hgutr069_custs"),
    "equipment_onts": ("sw_ctrls",),
    "igmp": ("packages",),
    "isam_cfm": ("domains", "y1731pm"),
    "isam_dist_service": ("config",),
    "isam_equipment": ("protection_groups",
                       "protection_elements", "external_link_assigns", "external_link_hosts"),
    "isam_system_security": ("operators", "profiles", "snmp_communities", "snmp_views",
                             "snmp_managers", "snmp_notify_profiles", "radius_auth_servers",
                             "radius_policies", "radius_dyn_auth_clients", "snmp_notify_views",
                             "domains", "ssh.sftp_users", "filetransfer.servers",
                             "peripheral_mgnt.mac_filters"),
    "isam_traps": ("definitions", "managers", "v6managers"),
    "l2cp_session": ("config",),
    "linetest": ("parameters", "sessions"),
    "mcast_control": ("packages",),
    "multicast": ("igmp.packages", "mcast_control.packages"),
    "ngpon2_channel_groups": ("config",),
    "qos_maps": ("dn_ctrl_pkt", "dscp_map_dot1p", "tc_map_dot1p", "up_ctrl_pkt"),
    "software_mngt": ("oswp",),
    "system": ("sntp.servers", "syslog.destinations", "syslog.routes",
               "sync_if_timing.ssm", "sync_if_timing.synce"),
    "vlans": ("config",),
}

SHARED_PROFILE = {
    "qos_profiles": ("config",),
    "pppoe_client_ppp_profile": ("config",),
    "voice_sip": ("cas_nsm_prof", "lineid_syn_prof", "redundancy", "redundancy_cmd",
                  "register", "vsp"),
    "xdsl_profiles": ("dpbo_profiles", "service_profiles", "spectrum_profiles",
                      "vce_profiles", "vect_profiles"),
}

# Sections owned by a physical object but not yet bound to a decoder in the domain
# catalogs. Classified object_owned so they are not mistaken for device-global;
# the missing binding remains an explicit gap until a decoder is added. All
# previously pending sections now have documented bindings; the mechanism stays
# for future evidence-gated additions.
OBJECT_OWNED_PENDING = {}

# Singleton/global resources registered in facts.py but not TARGETED_GATHER.
# This is explicit ownership, not a default for unrecognized families.
GLOBAL_RESOURCES = (
    "cwmp_plt", "dhcp_server", "equipment_replan", "error", "generic_pon",
    "interface_alarms", "iphost", "isam_vlan_global", "l2cp", "li_vlan",
    "mcast_general", "nat", "pon_global", "pppox_relay_global", "xdsl_system",
)

# Global scalar settings in otherwise instance-oriented resources. Unlisted
# settings remain gaps; never infer global ownership merely from scalar type.
GLOBAL_SETTINGS = {
    "alarm": ("log", "delta_log"),
    "bridges": ("ageing_time",),
    "isam_system_security": ("general", "default_profile", "radius_auth_super_user", "password", "ssh", "filetransfer"),
    "multicast": ("igmp.mcast_svc_context", "mcast_control.mcast_svc_context"),
    "igmp": ("mcast_svc_context",),
    "mcast_control": ("mcast_svc_context",),
    "software_mngt": ("sw_replacement_mode", "database"),
    "system": ("id", "security", "sntp", "syslog", "loop_id_syntax", "relay_id_syntax", "max_lt_link_speed", "transaction",
               "sync_if_timing.mode", "sync_if_timing.source", "sync_if_timing.revert", "sync_if_timing.wait_time",
               "sync_if_timing.output_ql_thresh", "sync_if_timing.ssmout_en_bits", "sync_if_timing.ssmout_ceiling",
               "sync_if_timing.ais_sensitivity", "sync_if_timing.bits", "sync_if_timing.bits_bind",
               "sync_if_timing.force_reference", "sync_if_timing.ref_order"),
    "voice_sip": ("statistics",),
    "xdsl_bonding": ("group_assembly_time", "ptm_init_mode"),
    "xstp": ("general",),
}


def section_scopes(bindings):
    """{(resource, section): scope} for every classified section.

    bindings is the catalog's binding list (resource/section/identity/decoder).
    Explicit shared definitions retain that scope even when they have a decoder.
    Physical bindings imply object_owned. A physical binding also listed as
    device-global is an error, not a silent override.
    """
    scopes = {}
    profiles = {(resource, section) for resource, sections in SHARED_PROFILE.items() for section in sections}
    for binding in bindings:
        key = (binding["resource"], binding["section"])
        # A definition can have a decoder without becoming physical hardware.
        scopes[key] = "shared_profile" if key in profiles else "object_owned"
    for resource, sections in DEVICE_GLOBAL.items():
        for section in sections:
            key = (resource, section)
            if key in scopes:
                raise ValueError("Section %s.%s is both object-owned and device-global" % key)
            scopes[key] = "device_global"
    for resource, sections in SHARED_PROFILE.items():
        for section in sections:
            key = (resource, section)
            if key in scopes and scopes[key] != "shared_profile":
                raise ValueError("Section %s.%s is both object-owned and shared-profile" % key)
            scopes[key] = "shared_profile"
    for resource, sections in OBJECT_OWNED_PENDING.items():
        for section in sections:
            key = (resource, section)
            if key in scopes:
                raise ValueError("Section %s.%s is both bound and pending object-owned" % key)
            scopes[key] = "object_owned"
    return scopes
