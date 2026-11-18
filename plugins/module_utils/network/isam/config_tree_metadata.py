"""Evidence-backed root-tree paths absent from the crawled CLI grammar.

Use the resource schemas as the authority for fields; do not infer identities from
their spelling (lowercase names are valid identities too). This supplements, not
edits, the generated grammar. Unknown nodes still use the lossless fallback.
"""
from functools import lru_cache


@lru_cache(maxsize=1)
def resource_grammar():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
        NODES, _options,
    )
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
        SYSLOG_SEVERITIES, SYNC_SSM_FIELDS, SYNC_SSMOUT_FIELDS,
    )
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system.system import Isam_systemArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.mcast_general.mcast_general import Mcast_generalArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.traps.traps import Isam_trapsArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import PROFILE_TYPES, SCHEMAS

    records = []

    def add(pattern, options, extra=None, positionals=()):
        parts = pattern.split()
        attrs = {key.replace("_", "-"): {"value": spec.get("type") != "bool"}
                 for key, spec in options.items() if spec.get("type") not in ("list", "dict")}
        attrs.update(extra or {})
        records.append({
            "path": [("id",) if part == "{}" else ("kw", part) for part in parts],
            "node": tuple(part for part in parts if part != "{}"),
            "attrs": attrs,
            "positionals": positionals,
        })

    for cli, section, identities, sub in NODES:
        options = _options(section, sub)
        pattern = "system security" + (" " + cli if cli else "")
        if identities:
            pattern += " {}"
            if len(identities) > 1:
                pattern += " " + identities[1].replace("_", "-") + " {}"
        # Identity fields belong to the path, not the attribute list.
        fields = {k: v for k, v in options.items() if k not in (identities or ())}
        add(pattern, fields)
        if section == "radius_policies":
            add(pattern + " servers {}", {
                k: v for k, v in options["servers"]["options"].items() if k != "index"
            })

    # The route identity and severity flags must not be mistaken for node names
    # or name/value pairs, regardless of line ordering or spelling of the identity.
    add("system syslog route {}", {}, {
        name: {"value": name not in SYSLOG_SEVERITIES}
        for name in ("msg-type", "facility", "syslog-vlan") + SYSLOG_SEVERITIES
    })
    add("system sync-if-timing synce {}", {"port": {"type": "str"}}, positionals=("port",))
    for cli, fields in (("ssm", SYNC_SSM_FIELDS), ("ssmout-synce", SYNC_SSMOUT_FIELDS)):
        add("system sync-if-timing " + cli + " {}", {k: {"type": t} for k, t in fields.items()})

    system = Isam_systemArgs.argument_spec["config"]["options"]
    id_options = {k: v for k, v in system["id"]["options"].items() if k != "node_id"}
    for pattern in ("system id {}", "system id"):
        add(pattern, id_options, {"contact-person": {"value": True}})
    sync = system["sync_if_timing"]["options"]
    add("system sync-if-timing", sync)
    for name in ("bits_bind", "ref_order"):
        add("system sync-if-timing " + name.replace("_", "-"), sync[name]["options"])

    add("mcast general", Mcast_generalArgs.argument_spec["config"]["options"])
    traps = Isam_trapsArgs.argument_spec["config"]["options"]
    for cli, section, identity in (("manager", "managers", "address"), ("v6manager", "v6managers", "ipv6address")):
        add("trap " + cli + " {}", {k: v for k, v in traps[section]["options"].items() if k != identity})

    def profile(pattern, schema):
        add(pattern, {}, {cli: {"value": kind != "flag"} for _option, cli, kind in schema["attrs"]})
        for _option, cli, child in schema["nodes"]:
            profile(pattern + " " + cli, child)
        for _option, cli, child in schema["lists"]:
            profile(pattern + " " + cli + " {}", child)

    for section, cli in PROFILE_TYPES.items():
        profile("xdsl " + cli + " {}", SCHEMAS[section])

    # Prefer the deepest exact match; a missing optional compound identity falls
    # back to the parent node without discarding its original CLI line.
    return tuple(sorted(records, key=lambda r: len(r["path"]), reverse=True))


# CLI spellings that intentionally differ from the stable resource option names.
# Scope mappings to the exact family/node, rather than accepting a spelling
# everywhere in that family. Targets must exist in the current argspec.
OPTION_NAMES = {
    ("equipment_replan", "equipment replan", "boardautoreplan"): "board_auto_replan",
    ("cwmp_plt", "cwmp plt", "adminstate"): "admin_state",
    ("software_mngt", "software-mngt database", "auto-backup-intvl"): "auto_backup_interval",
    ("qos_maps", "qos dscp-map-dot1p", "dot1p-value"): "dot1p",
    ("qos_profiles", "qos profiles shaper", "type"): "shaper_type",
    ("ethernet_line", "ethernet line mau", "type"): "mau_type",
    ("system", "system id", "contact-person"): "contact",
    ("system", "system sntp server-ip-addr", "enable"): "enabled",
    ("system", "system max-lt-link-speed", "link-speed"): "max_lt_link_speed",
}


def modelled_name(family, node, attr, known):
    """An explicit spelling mapping, list member or schema-less permission key."""
    target = OPTION_NAMES.get((family, node, attr))
    if target and target in known:
        return True
    if family == "isam_system_security" and node in (
        "system security profile", "system security default-profile",
    ):
        # The typed resource deliberately accepts arbitrary permission areas in a
        # dictionary. They are not missing scalar options.
        return "permissions" in known
    if family == "system" and node == "system syslog route":
        from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import SYSLOG_SEVERITIES
        return "severities" in known and attr in SYSLOG_SEVERITIES
    return False
