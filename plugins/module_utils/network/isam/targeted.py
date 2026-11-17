# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Targeted gathering: which resources read single instances, by which identity field.

When ``config`` names instances, ``state: gathered`` reads only those instances.
Without ``config`` the whole resource is read, as before. Only identity fields matter
for the selection; absent instances are simply missing from the result.

Pure data without imports, so tools outside Ansible can read it.

resource (facts name) -> {instance list: identity}
  instance list: "config" when config itself is the list, else the key in config
                 (dotted for nested keys, e.g. "syslog.destinations").
  identity:      a field name, or a list of field names for a composite identity.

Lists inside an instance (QoS queues, bridge VLANs, ...) are read with their instance.
Resources without instance lists (dhcp_server, generic_pon, l2cp, ...) are single
settings blocks and always read completely. Resources not read through the facts
registry (pppoe_client_*, pppoel2_statistics) are keyed by their module name.

TARGETED_WRITES: resources whose merged/replaced/deleted also compare against only
the named instances (resources made of instance lists, where that is exact).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

TARGETED_GATHER = {
    "alarm": {"custom_profiles": "name", "entries": "index", "filters": ["fltr_type", "filterid"], "hgutr069_custs": "alarm_id"},
    "ani_onts": {"config": "ont_idx"},
    "bridges": {"port": "port"},
    "channel_pair_pm": {"config": "name"},
    "efm_oam_interface": {"config": "name"},
    "epon_interfaces": {"config": "name"},
    "equipment_onts": {"interfaces": "ont_idx", "slots": "ont_slot_idx", "sw_ctrls": "sw_ctrl_id"},
    "ethernet_line": {"config": "if_index"},
    "ethernet_onts": {"config": "uni_idx"},
    "interface_cages": {"config": "id"},
    "interfaces": {"config": "name"},
    "isam_arp_relay": {"config": "name"},
    "isam_cfm": {"domains": "domain_index", "y1731pm": ["domain_index", "association", "mep", "session_id"]},
    "isam_dhcp_relay": {"config": "name"},
    "isam_dist_service": {"config": "name"},
    "isam_equipment": {"appliques": "id", "protection_groups": "id", "shelves": "id", "slots": "id"},
    "isam_ipv6_antispoofing_slot": {"config": "name"},
    "isam_traps": {"definitions": "name", "managers": "address", "v6managers": "ipv6address"},
    "l2cp_session": {"config": "name"},
    "l2cp_user_port": {"config": "name"},
    "link_agg": {"groups": "id", "ports": "id"},
    "linetest": {"parameters": ["session_id", "test_name"], "sessions": "session_id"},
    "ngpon2_channel_groups": {"config": "id"},
    "ntp_onts": {"config": "ont_id"},
    "pon_interfaces": {"config": "name"},
    "pppoe_client_interface": {"config": "name"},
    "pppoe_client_ppp_profile": {"config": "name"},
    "pppoel2_statistics": {"config": "name"},
    "qos_interfaces": {"config": "name"},
    "qos_maps": {"dn_ctrl_pkt": "protocol", "dscp_map_dot1p": "dscp", "tc_map_dot1p": "dot1p", "up_ctrl_pkt": "protocol"},
    "qos_profiles": {"config": ["profile_type", "name"]},
    "qos_tca": {"config": ["name", "queue"]},
    "software_mngt": {"oswp": "id"},
    "system": {"sntp.servers": "ip_address", "syslog.destinations": "name", "syslog.routes": "destination"},
    "vlans": {"config": "id"},
    "voice_sip": {"cas_nsm_prof": "name", "lineid_syn_prof": "name", "redundancy": "name", "redundancy_cmd": "name",
                  "register": "name", "vsp": "name"},
    "xdsl_boards": {"boards": "board_id", "vp_boards": "vp_board_id"},
    "xdsl_lines": {"config": "name"},
    "xdsl_profiles": {"dpbo_profiles": "id", "service_profiles": "id", "spectrum_profiles": "id", "vce_profiles": "id",
                      "vect_profiles": "id"},
    "xstp": {"ports": "port"},
}

TARGETED_WRITES = (
    "ani_onts", "bridges", "efm_oam_interface", "equipment_onts", "ethernet_onts", "interfaces",
    "isam_arp_relay", "isam_dhcp_relay", "ntp_onts", "pon_interfaces", "qos_interfaces",
)
