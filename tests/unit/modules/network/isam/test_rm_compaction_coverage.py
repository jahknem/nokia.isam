import ast
from pathlib import Path


SCOPED_RMS = {
    "Bridges",
    "Channel_pair_pm",
    "Epon_interfaces",
    "Equipment_onts",
    "Ethernet_line",
    "Ethernet_onts",
    "Generic_pon",
    "Interfaces",
    "Isam_traps",
    "Link_agg",
    "Mcast_general",
    "Ngpon2_channel_groups",
    "Pon_interfaces",
    "Qos_interfaces",
    "Vlans",
    "Xdsl_boards",
    "Xdsl_lines",
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
    "Igmp": "live output only confirms context selector",
    "Iphost": "object-level command",
    "Isam_arp_relay": "single global statistics option",
    "Isam_dhcp_relay": "distinct top-level command families",
    "Isam_dhcp_server": "distinct server and pool scopes",
    "Isam_dist_service": "fixture and live device do not confirm joined fields",
    "Isam_equipment": "different hardware object scopes",
    "Isam_ipv6_antispoofing_slot": "single field per slot",
    "Isam_system": "separate system subcommands",
    "Isam_voice_sip": "distinct SIP object scopes",
    "Isam_vlan_global": "global singleton/list scopes already atomic",
    "L2cp": "custom atomic renderer",
    "L2cpSession": "distinct session operations",
    "L2cpUserPort": "distinct user-port operations",
    "Li_vlan": "single VLAN field",
    "Mcast_control": "live output only confirms context selector",
    "Multicast": "live output only confirms context selector",
    "Ntp_onts": "per-ONT fields are separate command verbs",
    "PppoeClient": "custom renderer emits complete object commands",
    "Pppoel2": "per-interface operations use distinct verbs",
    "Qos_maps": "map entries are separate operations",
    "Qos_profiles": "profile renderer already emits atomic profile commands",
    "Software_mngt": "database and OSWP renderers already group supported options",
    "Xdsl_profiles": "profile commands have distinct nested scopes",
    "Xdsl_bonding": "single global option",
    "Xstp": "global and per-port scopes differ",
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
                (isinstance(base, ast.Name) and base.id in {"ResourceModule", "_Base"})
                for base in node.bases
            ):
                classes.add(node.name)
    return classes


def test_every_resource_module_has_an_explicit_compaction_disposition():
    resource_modules = _resource_module_classes()
    assert resource_modules == SCOPED_RMS | set(UNSCOPED_RMS)
    assert all(UNSCOPED_RMS.values())
