import ast
from pathlib import Path


SCOPED_RMS = {
    "Bridges",
    "Channel_pair_pm",
    "Epon_interfaces",
    "Equipment_onts",
    "Ethernet_line",
    "Ethernet_onts",
    "Interfaces",
    "Isam_traps",
    "Link_agg",
    "Mcast_general",
    "Ngpon2_channel_groups",
    "Pon_interfaces",
    "Qos_interfaces",
    "Vlans",
    "Xdsl_boards",
    "Xdsl_inm",
    "Xdsl_lines",
    "Pon_global",
    "Pppox_relay_global",
    "Trouble_shooting_pon",
}

# Table families: the attribute table packs one command per CLI node, so there is
# nothing left to compact (module_utils/network/isam/attribute_table.py).
TABLE_RMS = {
    "Generic_pon": "attribute table packs one line per PON settings scope",
    "Isam_voice_sip": "attribute table packs one line per SIP object scope",
    "Software_mngt": "attribute table packs one line per database/OSWP scope",
}

# These RMs have been audited and intentionally have no compactable
# multi-attribute scope: their output is already atomic, has distinct command
# verbs/contexts, or has no device-confirmed packed grammar.
UNSCOPED_RMS = {
    "Alarm": "one command per alarm operation",
    "Ani_onts": "single-field TCA operations",
    "Cfm": "custom renderer already emits object commands atomically",
    "EfmOam": "custom renderer already emits one command per interface",
    "Equipment_replan": "single global option",
    "Interface_alarms": "identity plus one configurable field",
    "InterfaceCages": "live output has one field per cage; packed form unconfirmed",
    "Igmp": "package/system emitted as one line per object; context selector separate",
    "Iphost": "object-level command",
    "Isam_arp_relay": "single global statistics option",
    "Isam_dhcp_relay": "distinct top-level command families",
    "Isam_dhcp_server": "distinct server and pool scopes",
    "Isam_dist_service": "fixture and live device do not confirm joined fields",
    "Isam_equipment": "different hardware object scopes",
    "Isam_ipv6_antispoofing_slot": "single field per slot",
    "Isam_system": "separate system subcommands",
    "Isam_system_security": "custom renderer emits one command per security object",
    "Isam_vlan_global": "global singleton/list scopes already atomic",
    "L2cp": "custom atomic renderer",
    "L2cpSession": "distinct session operations",
    "L2cpUserPort": "distinct user-port operations",
    "Li_vlan": "single VLAN field",
    "Linetest": "custom renderer emits complete per-field session/parameter commands; destroy is atomic",
    "Mcast_control": "package/system emitted as one line per object; context selector separate",
    "Multicast": "package/system emitted as one line per object; context selector separate",
    "Ntp_onts": "per-ONT fields are separate command verbs",
    "PppoeClient": "custom renderer emits complete object commands",
    "Pppoel2": "per-interface operations use distinct verbs",
    "Qos_maps": "map entries are separate operations",
    "Qos_profiles": "profile renderer already emits atomic profile commands",
    "Qos_tca": "per-queue attributes are separate set/reset commands",
    "Xdsl_profiles": "profile commands have distinct nested scopes",
    "Xdsl_bonding": "single global option",
    "Xstp": "global and per-port scopes differ",
    "Qos_global": "custom renderer already packs one command per section/line card",
    "Nat": "single global option",
    "Error": "single global option",
    "Cwmp_plt": "single global option",
    "Xdsl_onts": "single attribute per ONT",
    "Xdsl_system": "single global option",
    "L2uni_onts": "custom renderer already packs one command per UNI scope",
    "Uni_onts": "single field per UNI",
}


def _resource_module_classes():
    root = Path(__file__).resolve().parents[5] / "plugins/module_utils/network/isam/config"
    classes = set()
    for path in root.rglob("*.py"):
        tree = ast.parse(path.read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.ClassDef) or node.name.startswith("_"):
                continue
            if any(
                (isinstance(base, ast.Name) and base.id in {"ResourceModule", "IsamResourceModule", "TableResourceModule", "_Base"})
                for base in node.bases
            ):
                classes.add(node.name)
    return classes


def test_every_resource_module_has_an_explicit_compaction_disposition():
    resource_modules = _resource_module_classes()
    assert resource_modules == SCOPED_RMS | set(UNSCOPED_RMS) | set(TABLE_RMS)
    assert all(UNSCOPED_RMS.values())
