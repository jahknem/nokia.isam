from pathlib import Path

import yaml

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_variants import (
    Epon_interfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import (
    Equipment_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.isam_equipment.isam_equipment import (
    Isam_equipmentFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dhcp_server.dhcp_server import (
    Isam_dhcp_serverFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_replan.equipment_replan import (
    Equipment_replanFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_onts.ethernet_onts import (
    Ethernet_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_line.ethernet_line import (
    Ethernet_lineFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.generic_pon.generic_pon import (
    Generic_ponFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.bridges.bridges import (
    BridgesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.link_agg.link_agg import (
    Link_aggFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.mcast_general.mcast_general import (
    Mcast_generalFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.multicast.multicast import (
    MulticastFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ntp_onts.ntp_onts import (
    Ntp_ontsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interfaces.interfaces import (
    InterfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces import (
    Pon_interfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_interfaces.qos_interfaces import (
    Qos_interfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.system.system import (
    Isam_systemFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.traps.traps import (
    Isam_trapsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlan_global.vlan_global import (
    Isam_vlan_globalFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlans.vlans import (
    VlansFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_boards.xdsl_boards import (
    Xdsl_boardsFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_bonding.xdsl_bonding import (
    Xdsl_bondingFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_lines.xdsl_lines import (
    Xdsl_linesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xstp.xstp import (
    XstpFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm import (
    AlarmTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.dhcp_server import (
    Isam_dhcp_serverTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_onts import (
    Ethernet_ontsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    Ethernet_lineTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    Generic_ponTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.isam_equipment import (
    Isam_equipmentTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_alarms import (
    Interface_alarmsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_cages import (
    InterfaceCagesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.li_vlan import (
    Li_vlanTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import (
    MulticastTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.link_agg import (
    Link_aggTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ani_onts import (
    Ani_ontsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ntp_onts import (
    Ntp_ontsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pon_interfaces import (
    Pon_interfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_interfaces import (
    Qos_interfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_maps import (
    Qos_mapsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    Software_mngtTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.traps import (
    Isam_trapsTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlan_global import (
    Isam_vlan_globalTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VlansTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    Isam_voice_sipTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    Xdsl_profilesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_bonding import (
    Xdsl_bondingTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_lines import (
    Xdsl_linesTemplate,
)


FIXTURE_ROOT = Path(__file__).parents[4] / "fixtures"
REQUIRED_DESCRIPTOR_FIELDS = {
    "schema_version",
    "resource",
    "device_type",
    "software_version",
    "command",
    "captured_at",
    "source",
}


def fixture_bundle(resource, name):
    bundle = FIXTURE_ROOT / resource / name
    with (bundle / "fixture.yml").open() as descriptor_file:
        descriptor = yaml.safe_load(descriptor_file)
    output = (bundle / "output.txt").read_text()
    return descriptor, output


def test_every_fixture_has_a_device_descriptor():
    descriptors = sorted(FIXTURE_ROOT.glob("*/**/fixture.yml"))
    assert descriptors
    for path in descriptors:
        with path.open() as descriptor_file:
            descriptor = yaml.safe_load(descriptor_file)
        assert REQUIRED_DESCRIPTOR_FIELDS <= set(descriptor)
        assert descriptor["schema_version"] == 1
        assert descriptor["device_type"]
        assert descriptor["software_version"]
        assert descriptor["source"] in {"sanitized-live-capture", "synthetic-regression"}
        assert path.with_name("output.txt").is_file()


def test_voice_fixture_is_parseable():
    descriptor, output = fixture_bundle("voice_sip", "r6.2.04m")
    parsed = Isam_voice_sipTemplate(lines=output.splitlines()).parse()
    assert descriptor["software_version"] == "R6.2.04m"
    assert any(entry["name"] == "vsp1" for entry in parsed["vsp"])


def test_software_fixture_is_parseable():
    descriptor, output = fixture_bundle("software_mngt", "r6.2.04m")
    parsed = Software_mngtTemplate(lines=output.splitlines()).parse()
    assert descriptor["device_type"] == "Nokia ISAM 7330 FTTN"
    assert len(parsed["oswp"]) == 2


def test_pon_variant_fixture_is_parseable():
    descriptor, output = fixture_bundle("pon_variants", "r6.2.04ng")
    parsed = Epon_interfacesTemplate(lines=output.splitlines()).parse()
    assert descriptor["command"] == "info configure epon interface flat"
    assert parsed["1/1/1/1"]["name"] == "1/1/1/1"


def test_bridge_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("bridges", "r6.2.04m")
    parsed = BridgesFacts(module=None)._parse_bridge_config(output)
    port = parsed["port"][0]
    vlans = {entry["id"]: entry for entry in port["vlan_id"]}

    assert descriptor["command"] == "info configure bridge flat"
    assert port["port"] == "1/1/2/1/1/1/1"
    assert port["pvid"] == 99
    assert vlans["20"]["l2fwder_vlan"] == 720
    assert vlans["20"]["qos"] == "priority:5"


def test_vlan_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("vlans", "r6.2.04m")
    facts = VlansFacts(module=None)
    parsed = VlansTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure vlan id flat"
    assert parsed[99]["mode"] == "residential-bridge"
    assert parsed[99]["dhcp-opt82-ext"] == "add-or-forward"
    assert parsed[120]["priority"] == 5


def test_qos_profiles_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("qos_profiles", "r6.2.04m")
    parsed = Qos_profilesTemplate(lines=output.splitlines()).parse()

    assert descriptor["command"] == "info configure qos profiles flat"
    assert parsed["queue:FD_BEQ"]["queue-type"] == "red:24:48:80"
    assert parsed["scheduler-node:NGLT_Default"]["priority"] == 2
    assert parsed["policer:qpp5Mbps"]["committed-info-rate"] == 5120
    assert parsed["session:FD_Voice"]["up-policer"] == "name:FD_Pol_Voice"


def test_interfaces_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("interfaces", "r6.2.04m")
    raw_lines = [line.replace("configure interface ", "", 1) for line in output.splitlines()]
    parsed = InterfacesTemplate(lines=raw_lines).parse()
    parsed = {key: InterfacesFacts._canonicalize_entry(value) for key, value in parsed.items()}

    assert descriptor["command"] == "info configure interface port flat"
    assert parsed["uni:1/1/2/1/100/1/1"]["admin_up"] is True


def test_link_agg_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("link_agg", "r6.2.04m")
    facts = Link_aggFacts(module=None)
    parsed = list(Link_aggTemplate(lines=facts._flatten_config(output)).parse().values())
    ports = [item for item in parsed if item.get("type") == "port"]
    groups = [item for item in parsed if item.get("type") == "group"]

    assert descriptor["command"] == "info configure link-agg flat"
    assert ports[0]["passive_lacp"] is True
    assert groups[0]["load_sharing_policy"] == "mac-src"
    assert groups[0]["ports"]["1/1/8/1"] == "1/1/8/1"


def test_xdsl_profiles_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("xdsl_profiles", "r6.2.04m")
    template = Xdsl_profilesTemplate()
    parsed = template.normalize(template.parse(output))

    assert descriptor["command"] == "info configure xdsl *-profile flat"
    assert parsed["service_profiles"][0]["max_bitrate_down"] == 33000
    assert parsed["spectrum_profiles"][0]["dis_ansi_t1413"] is True
    assert parsed["dpbo_profiles"][0]["es_elect_length"] == 249
    assert parsed["vect_profiles"][0]["band_control_dn"] == "59:512"
    assert parsed["vce_profiles"][0]["vce_join_timeout"] == "auto"


def test_system_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("system", "r6.2.04m")
    facts = Isam_systemFacts(module=None)
    lines = facts._flatten_config(output)
    parsed = facts._parse_flat_config(lines)

    assert descriptor["command"] == "info configure system flat"
    assert parsed["id"]["node_id"] == "SANITIZED-ISAM"
    assert parsed["sntp"]["enabled"] is True
    assert parsed["sntp"]["server_ip_addr"] == "192.0.2.1"
    assert parsed["transaction"]["log_full_action"] == "wrap"
    assert parsed["syslog"]["destinations"][0]["name"] == "ams"


def test_traps_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("traps", "r6.2.04m")
    facts = Isam_trapsFacts(module=None)
    parsed = Isam_trapsTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure trap"
    assert parsed["definitions"]["cold-start"]["priority"] == "medium"
    assert parsed["managers"]["192.0.2.127"]["priority"] == "low"


def test_vlan_global_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("vlan_global", "r6.2.04m")
    facts = Isam_vlan_globalFacts(module=None)
    parsed = Isam_vlan_globalTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure vlan flat"
    assert parsed["tpid"]["value"] == 8100
    assert parsed["vmac_address_format"]["host_id"] == 0
    assert parsed["priority_regen"][1]["profile_name"] == "TrustedPort"


def test_alarm_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("alarm", "r6.2.04m")
    parsed = AlarmTemplate(lines=output.splitlines()).parse()

    assert descriptor["command"] == "info configure alarm flat"
    assert parsed["filters"]["temporal/1"]["alarmid"] == "all"
    assert parsed["log"]["log_sev_level"] == "critical"


def test_interface_alarm_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("interface_alarms", "r6.2.04m")
    parsed = Interface_alarmsTemplate(lines=output.splitlines()).parse()

    assert descriptor["command"] == "info configure interface alarm"
    assert sorted(parsed) == ["eont", "epon", "ont"]


def test_interface_cage_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("interface_cages", "r6.2.04m")
    parsed = InterfaceCagesTemplate(lines=output.splitlines()).parse()

    assert descriptor["command"] == "info configure interface cage flat"
    assert parsed["lt:1/1/2:cage:1"]["operational_mode"] == "gpon"


def test_ntp_onts_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("ntp_onts", "r6.2.04m")
    lines = Ntp_ontsFacts(module=None)._flatten_config(output)
    parsed = Ntp_ontsTemplate(lines=lines).parse()

    assert descriptor["command"] == "info configure ntp flat"
    assert len(parsed) == 74
    assert parsed["1/1/2/1/1"]["ont_id"] == "1/1/2/1/1"


def test_qos_maps_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("qos_maps", "r6.2.04m")
    parsed = Qos_mapsTemplate(lines=output.splitlines()).parse()

    assert descriptor["command"] == "info configure qos *-map/*-ctrl-pkt flat"
    assert len(parsed["tc_map_dot1p"]) == 8
    assert len(parsed["dscp_map_dot1p"]) == 64
    assert parsed["tc_map_dot1p"][0]["dpcolor"] == "green"
    assert parsed["dscp_map_dot1p"][8]["dot1p"] == 1


def test_xdsl_boards_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("xdsl_boards", "r6.2.04m")
    parsed = Xdsl_boardsFacts(module=None)._parse_config(output)

    assert descriptor["command"] == "info configure xdsl board/vp-board flat"
    assert parsed["boards"][0]["board_id"] == "1/1/1"
    assert parsed["boards"][0]["vce_profile"] == "10"
    assert parsed["vp_boards"][0]["vp_link"] == "2"


def test_xdsl_bonding_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("xdsl_bonding", "r6.2.04m")
    facts = Xdsl_bondingFacts(module=None)
    parsed = Xdsl_bondingTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure xdsl-bonding"
    assert parsed["group_assembly_time"] == 0


def test_xdsl_lines_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("xdsl_lines", "r6.2.04m")
    facts = Xdsl_linesFacts(module=None)
    parsed = Xdsl_linesTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure xdsl line flat"
    assert len(parsed) == 96
    assert parsed["1/1/3/1"]["service_profile"] == 13
    assert parsed["1/1/3/1"]["admin_up"] is True


def test_xstp_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("xstp", "r6.2.04m")
    parsed = XstpFacts(module=None)._parse_xstp_config(output)

    assert descriptor["command"] == "info configure xstp flat"
    assert len(parsed["ports"]) == 36
    assert parsed["ports"][0]["path_cost"] == 200000


def test_small_global_live_flat_fixtures_are_parseable():
    descriptor, output = fixture_bundle("li_vlan", "r6.2.04m")
    parsed = Li_vlanTemplate(lines=output.splitlines()).parse()
    assert descriptor["command"] == "info configure li_vlan flat"
    assert parsed["vlan_id"] == 0

    descriptor, output = fixture_bundle("mcast_general", "r6.2.04m")
    parsed = Mcast_generalFacts(module=None)._parse_mcast_general_config(output)
    assert descriptor["command"] == "info configure mcast general flat"
    assert parsed["fast_change"] is True

    descriptor, output = fixture_bundle("equipment_replan", "r6.2.04m")
    parsed = Equipment_replanFacts(module=None)._parse_config(output)
    assert descriptor["command"] == "info configure equipment replan flat"
    assert parsed["board_auto_replan"] == "disable"


def test_multicast_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("multicast", "r6.2.04m")
    lines = MulticastFacts._flatten_config(output)
    parsed = MulticastTemplate(lines=lines).parse()

    assert descriptor["command"] == "info configure igmp/mcast-control flat"
    assert parsed["igmp"]["mcast_svc_context"] == "Default"
    assert parsed["mcast_control"]["mcast_svc_context"] == "Default"


def test_dhcp_server_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("dhcp_server", "r6.2.04m")
    facts = Isam_dhcp_serverFacts(module=None)
    parsed = Isam_dhcp_serverTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure dhcp-server flat"
    assert parsed["start_addr"] == "0.0.0.0"
    assert parsed["restart"] is True


def test_generic_pon_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("generic_pon", "r6.2.04m")
    facts = Generic_ponFacts(module=None)
    parsed = Generic_ponTemplate(lines=facts._split_packed_lines(output)).parse()

    assert descriptor["command"] == "info configure generic-pon flat"
    assert parsed["dpinteg_threshold"] == 0


def test_ethernet_line_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("ethernet_line", "r6.2.04m")
    lines = Ethernet_lineFacts._compact_lines(
        output.splitlines(), "configure ethernet line "
    )
    parsed = Ethernet_lineTemplate(lines=lines).parse()

    assert descriptor["command"] == "info configure ethernet line flat"
    assert parsed["1/1/8/1"]["port_type"] == "uni"
    assert parsed["1/1/8/1"]["mau"][1]["mau_type"] == "1000basebx10d"


def test_equipment_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("equipment", "r6.2.04m")
    facts = Isam_equipmentFacts(module=None)
    parsed = Isam_equipmentTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure equipment flat"
    assert parsed["shelves"]["1/1"]["planned_type"] == "nfxs-b"
    assert parsed["slots"]["vlt:1/1/63"]["unlock"] is True
    assert parsed["protection_groups"][1]["admin_status"] == "lock"


def test_ethernet_onts_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("ethernet_onts", "r6.2.04m")
    facts = Ethernet_ontsFacts(module=None)
    parsed = Ethernet_ontsTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure ethernet ont flat"
    assert parsed["1/1/2/1/1/1/1"]["cust_info"] == "YTest-Proxy"
    assert parsed["1/1/2/1/1/1/1"]["admin_state"] == "up"


def test_qos_interfaces_live_flat_fixture_is_parseable():
    descriptor, output = fixture_bundle("qos_interfaces", "r6.2.04m")
    facts = Qos_interfacesFacts(module=None)
    parsed = Qos_interfacesTemplate(lines=facts._flatten_config(output)).parse()

    assert descriptor["command"] == "info configure qos interface flat"
    assert len(parsed) == 592
    assert parsed["1/1/2/1/1/1/1"]["scheduler_node"] == "name:NGLT_Default"
    assert parsed["1/1/2/1/1/1/1"]["queue"][0]["priority"] == 6


def test_pon_interface_live_detail_fixture_is_parseable():
    descriptor, output = fixture_bundle("pon_interfaces", "r6.2.04m")
    facts = Pon_interfacesFacts(module=None)
    flattened = facts._flatten_config(output)
    parsed = Pon_interfacesTemplate(lines=flattened).parse()
    entry = parsed["1/1/2/1"]

    assert descriptor["command"] == "info configure pon interface flat detail"
    assert entry["admin_state"] == "up"
    assert entry["fec_dn"] == "disable"
    assert entry["tconts_per_frame"] == 64
    assert entry["tc_layer"]["pm_collect"] == "pm-enable"
    assert "pon_pmcollect" not in entry["utilization"]


def test_equipment_onts_live_detail_fixture_is_parseable():
    descriptor, output = fixture_bundle("equipment_onts", "r6.2.04m")
    parsed = Equipment_ontsFacts(module=None)._parse_config(output)

    assert descriptor["command"] == "info configure equipment ont flat detail"
    assert parsed["interfaces"][0]["ont_idx"] == "1/1/2/1/1"
    assert parsed["interfaces"][0]["sernum"] == "ALCL:SANITIZED"
    assert parsed["interfaces"][0]["enable_aes"] == "enable"
    assert parsed["slots"][0]["planned_card_type"] == "ethernet"
    assert parsed["slots"][0]["plndnumdataports"] == 1
    assert parsed["sw_ctrls"][0]["ont_variant"] == "DO"


def test_ani_fixture_is_parseable():
    descriptor, output = fixture_bundle("ani_onts", "r6.2.04m")
    parsed = Ani_ontsTemplate(lines=output.splitlines()).parse()
    assert descriptor["command"] == "info configure ani ont flat"
    assert parsed["1/1/2/1/1"]["tca_thresh"] is True


def test_ani_fixture_supports_the_observed_no_form():
    rendered = Ani_ontsTemplate().render(
        {"ont_idx": "1/1/2/1/1", "tca_thresh": False}, "tca_thresh"
    )
    assert rendered == "configure ani ont no tca-thresh 1/1/2/1/1"


def test_ani_threshold_fields_parse_and_render():
    parsed = Ani_ontsTemplate(
        lines=[
            "configure ani ont tca-thresh 1/1/2/1/1 lower-optical-th -25.5 upper-optical-th 0.5 rssi-profile 12",
        ]
    ).parse()

    assert parsed["1/1/2/1/1"]["lower_optical_th"] == -25.5
    assert parsed["1/1/2/1/1"]["upper_optical_th"] == 0.5
    assert parsed["1/1/2/1/1"]["rssi_profile"] == 12
    assert Ani_ontsTemplate().render(
        {"ont_idx": "1/1/2/1/1", "tca_thresh": True, "lower_optical_th": -25.5},
        "tca_thresh",
    ) == "configure ani ont tca-thresh 1/1/2/1/1 lower-optical-th -25.5"
