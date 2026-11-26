"""Attribute gaps closed against the lab capture: isam_system settings (id, sntp, syslog,
transaction, external-leds, auto-laser-shutdown, auto-switch, zero-touch-provision, pon-ont,
nt-sftp, syslog destination/route attributes), isam_cfm slm, isam_vlan_global
broadcast-frames priority-policy and isam_mcast_general fast channel change attributes.

Plus a capture test: the gap report of these families (and of the single-attribute
families checked alongside) is down to the listed false positives.
"""
import os
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import (
    isam_cfm,
    isam_mcast_general,
    isam_system,
    isam_vlan_global,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
    gap_report,
    parse_config_tree,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures

ignore_provider_arg = True



class _Conn(object):
    def __init__(self, text):
        self.text, self.commands = text, []

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        return self.text


class _Base(TestIsamModule):
    def setUp(self):
        super(_Base, self).setUp()
        self._patches = [
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"),
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection"),
            patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"),
            patch("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.cfm.cfm.get_resource_connection"),
        ]
        self.connections = [p.start() for p in self._patches]

    def tearDown(self):
        super(_Base, self).tearDown()
        for p in self._patches:
            p.stop()

    def device(self, text):
        self.connections[2].return_value = self.connections[3].return_value = _Conn(dedent(text))

    def run_state(self, state, changed, **args):
        set_module_args(dict(args, state=state), ignore_provider_arg)
        return self.execute_module(changed=changed)


# ---------------------------------------------------------------- isam_system

# realistic 'info configure detail flat' lines (lab values replaced)
SYSTEM_DETAIL = """\
configure system id NODE-1 name NODE-1 location "Lab - Room 1" no access-oper-id no system-40gkr4 contact-person Ops en-snmp-auth-trap nt-intercon-vlan 4092 no periph-mgnt-vlan internal-nw-vlan 4089 no periph-mgnt-ctrl system-mac 00:00:5e:00:53:01/00:00:5e:00:53:02/24 port-num-in-proto type-based no ont-trc-dbg-vlan no ntr-ssmout-vlan no ntr-ptp-vlan no customer-id voiceoswp sip no scalingmode no arp-polling-inter bsnap-state disable bsnap-server-ip 169.254.1.1 bsnap-server-port 0 no arp-tca-threshold
configure system external-leds no status
configure system sntp server-ip-addr 192.0.2.57 no server-port polling-rate 60 enable timezone-offset 60
configure system max-lt-link-speed link-speed ten-gb
configure system transaction no time-out-value log-full-action wrap
configure system syslog no version no time-format
configure system syslog destination ams type udp:192.0.2.10:514:unlimited no disable no upload-rotate no persist-enable no persist-timer
configure system syslog destination diagnostic type file:diagnostic:2000 no disable no upload-rotate no persist-enable no persist-timer
configure system syslog route ams msg-type all facility local4 no syslog-vlan emergency alert critical error warning notice information no debug
configure system syslog route diagnostic msg-type eqpt facility local0 no syslog-vlan no emergency no alert no critical no error no warning notice no information no debug
configure system pon-ont no slid-mode no pwrbrst-mode no sn-bundle-timer no sw-ver-mis-block no sn-autounlock
configure system auto-laser-shutdown no action
configure system auto-switch no xdsl-atm-ptm no xdsl-stepup-delay
configure system zero-touch-provision no action
configure system nt-sftp no write-enable
configure system security welcome-banner "not read here"
"""

# the same node with non-default values everywhere
SYSTEM_SET = """\
configure system id NODE-1 name NODE-1 access-oper-id op1 system-40gkr4 enable contact-person Ops en-snmp-auth-trap periph-mgnt-vlan 30 periph-mgnt-ctrl enable port-num-in-proto position-based ont-trc-dbg-vlan 31 ntr-ssmout-vlan 32 ntr-ptp-vlan 33 customer-id cust-1 voiceoswp sip scalingmode mode-a arp-polling-inter 20 bsnap-state enable bsnap-server-ip 192.0.2.5 bsnap-server-port 4000 arp-tca-threshold 50
configure system external-leds status disable
configure system sntp server-ip-addr 192.0.2.57 server-port 1123 polling-rate 60 enable timezone-offset 60
configure system transaction time-out-value 900 log-full-action wrap
configure system syslog version rfc5424 time-format utc
configure system syslog destination ams type udp:192.0.2.10:514:unlimited disable upload-rotate persist-enable persist-timer 15
configure system syslog route ams msg-type all facility local4 syslog-vlan 100 emergency no debug
configure system pon-ont slid-mode ascii pwrbrst-mode enable sn-bundle-timer 5 sw-ver-mis-block disable sn-autounlock enable
configure system auto-laser-shutdown action enable
configure system auto-switch xdsl-atm-ptm xdsl-stepup-delay 1800
configure system zero-touch-provision action enable
configure system nt-sftp write-enable
"""

SYSTEM_SET_PARSED = {
    "id": {
        "node_id": "NODE-1", "name": "NODE-1", "contact": "Ops", "access_oper_id": "op1", "system_40gkr4": "enable",
        "en_snmp_auth_trap": True, "periph_mgnt_vlan": 30, "periph_mgnt_ctrl": "enable", "port_num_in_proto": "position-based",
        "ont_trc_dbg_vlan": 31, "ntr_ssmout_vlan": 32, "ntr_ptp_vlan": 33, "customer_id": "cust-1", "voiceoswp": "sip",
        "scalingmode": "mode-a", "arp_polling_inter": 20, "bsnap_state": "enable", "bsnap_server_ip": "192.0.2.5",
        "bsnap_server_port": 4000, "arp_tca_threshold": 50,
    },
    "external_leds": {"status": "disable"},
    "sntp": {"server_ip_addr": "192.0.2.57", "server_port": 1123, "polling_rate": 60, "enabled": True, "timezone_offset": 60},
    "transaction": {"time_out_value": 900, "log_full_action": "wrap"},
    "syslog": {
        "version": "rfc5424", "time_format": "utc",
        "destinations": [{"name": "ams", "type": "udp:192.0.2.10:514:unlimited", "disable": True, "upload_rotate": True,
                          "persist_enable": True, "persist_timer": 15}],
        "routes": [{"destination": "ams", "msg_type": "all", "facility": "local4", "severities": ["emergency"], "syslog_vlan": 100}],
    },
    "pon_ont": {"slid_mode": "ascii", "pwrbrst_mode": "enable", "sn_bundle_timer": 5, "sw_ver_mis_block": "disable", "sn_autounlock": "enable"},
    "auto_laser_shutdown": {"action": "enable"},
    "auto_switch": {"xdsl_atm_ptm": True, "xdsl_stepup_delay": 1800},
    "zero_touch_provision": {"action": "enable"},
    "nt_sftp": {"write_enable": True},
}

# the settings attributes only (what the new renderer writes)
SYSTEM_NEW = {
    "id": dict((k, v) for k, v in SYSTEM_SET_PARSED["id"].items() if k not in ("name", "contact")),
    "external_leds": SYSTEM_SET_PARSED["external_leds"],
    "sntp": {"server_port": 1123},
    "transaction": {"time_out_value": 900},
    "syslog": {
        "version": "rfc5424", "time_format": "utc",
        "destinations": [{"name": "ams", "disable": True, "upload_rotate": True, "persist_enable": True, "persist_timer": 15}],
        "routes": [{"destination": "ams", "syslog_vlan": 100}],
    },
    "pon_ont": SYSTEM_SET_PARSED["pon_ont"],
    "auto_laser_shutdown": SYSTEM_SET_PARSED["auto_laser_shutdown"],
    "auto_switch": SYSTEM_SET_PARSED["auto_switch"],
    "zero_touch_provision": SYSTEM_SET_PARSED["zero_touch_provision"],
    "nt_sftp": SYSTEM_SET_PARSED["nt_sftp"],
}

SYSTEM_RENDERED = [
    "configure system id NODE-1 access-oper-id op1 system-40gkr4 enable en-snmp-auth-trap periph-mgnt-vlan 30 periph-mgnt-ctrl enable "
    "port-num-in-proto position-based ont-trc-dbg-vlan 31 ntr-ssmout-vlan 32 ntr-ptp-vlan 33 customer-id cust-1 voiceoswp sip "
    "scalingmode mode-a arp-polling-inter 20 bsnap-state enable bsnap-server-ip 192.0.2.5 bsnap-server-port 4000 arp-tca-threshold 50",
    "configure system sntp server-port 1123",
    "configure system syslog version rfc5424 time-format utc",
    "configure system syslog destination ams disable upload-rotate persist-enable persist-timer 15",
    "configure system syslog route ams syslog-vlan 100",
    "configure system transaction time-out-value 900",
    "configure system external-leds status disable",
    "configure system auto-laser-shutdown action enable",
    "configure system auto-switch xdsl-atm-ptm xdsl-stepup-delay 1800",
    "configure system zero-touch-provision action enable",
    "configure system pon-ont slid-mode ascii pwrbrst-mode enable sn-bundle-timer 5 sw-ver-mis-block disable sn-autounlock enable",
    "configure system nt-sftp write-enable",
]


class TestSystemGaps(_Base):
    module = isam_system

    def test_parsed_detail_reports_no_defaults_and_ignores_security(self):
        parsed = self.run_state("parsed", False, running_config=SYSTEM_DETAIL)["parsed"]
        assert parsed["id"] == {
            "node_id": "NODE-1", "name": "NODE-1", "location": "Lab - Room 1", "contact": "Ops",
            "nt_intercon_vlan": 4092, "internal_nw_vlan": 4089, "system_mac": "00:00:5e:00:53:01/00:00:5e:00:53:02/24",
            "en_snmp_auth_trap": True, "port_num_in_proto": "type-based", "voiceoswp": "sip",
            "bsnap_state": "disable", "bsnap_server_ip": "169.254.1.1", "bsnap_server_port": 0,
        }
        assert parsed["sntp"] == {"server_ip_addr": "192.0.2.57", "polling_rate": 60, "enabled": True, "timezone_offset": 60}
        assert parsed["transaction"] == {"log_full_action": "wrap"}
        assert parsed["syslog"]["destinations"] == [
            {"name": "ams", "type": "udp:192.0.2.10:514:unlimited"},
            {"name": "diagnostic", "type": "file:diagnostic:2000"},
        ]
        assert parsed["syslog"]["routes"] == [
            {"destination": "ams", "msg_type": "all", "facility": "local4",
             "severities": ["emergency", "alert", "critical", "error", "warning", "notice", "information"]},
            {"destination": "diagnostic", "msg_type": "eqpt", "facility": "local0", "severities": ["notice"]},
        ]
        for section in ("external_leds", "pon_ont", "auto_laser_shutdown", "auto_switch", "zero_touch_provision",
                        "nt_sftp", "security"):
            assert section not in parsed
        assert "version" not in parsed["syslog"]

    def test_parsed_set_values(self):
        assert self.run_state("parsed", False, running_config=SYSTEM_SET)["parsed"] == SYSTEM_SET_PARSED

    def test_sntp_no_enable_is_not_enabled(self):
        parsed = self.run_state("parsed", False, running_config="configure system sntp server-ip-addr 192.0.2.1 no enable")["parsed"]
        assert parsed["sntp"] == {"server_ip_addr": "192.0.2.1"}

    def test_unknown_and_non_numeric_tokens_never_fail(self):
        parsed = self.run_state("parsed", False, running_config=(
            "configure system pon-ont sn-bundle-timer soon future-knob 3 sn-autounlock enable\n"
            "configure system nt-sftp write-enable read-enable\n"))["parsed"]
        assert parsed["pon_ont"] == {"sn_autounlock": "enable"}
        assert parsed["nt_sftp"] == {"write_enable": True}

    def test_rendered_and_round_trip(self):
        rendered = self.run_state("rendered", False, config=SYSTEM_NEW)["rendered"]
        assert rendered == SYSTEM_RENDERED
        parsed = self.run_state("parsed", False, running_config="\n".join(rendered))["parsed"]
        assert parsed == SYSTEM_NEW

    def test_merged_idempotent(self):
        self.device(SYSTEM_SET)
        result = self.run_state("merged", False, config=SYSTEM_SET_PARSED)
        assert result["commands"] == []
        # a False flag or a value equal to the device default: nothing to send against the detail capture
        self.device(SYSTEM_DETAIL)
        assert self.run_state("merged", False, config={"nt_sftp": {"write_enable": False}, "id": {"system_40gkr4": "disable"}, "auto_switch": {"xdsl_stepup_delay": 3600}})["commands"] == []

    def test_merged_changes(self):
        self.device(SYSTEM_DETAIL)
        result = self.run_state("merged", True, config={
            "id": {"customer_id": "c2", "en_snmp_auth_trap": False},
            "pon_ont": {"sn_bundle_timer": 7},
            "syslog": {"destinations": [{"name": "ams", "persist_timer": 9}]},
        })
        assert result["commands"] == [
            "configure system id NODE-1 no en-snmp-auth-trap customer-id c2",
            "configure system syslog destination ams persist-timer 9",
            "configure system pon-ont sn-bundle-timer 7",
        ]

    def test_replaced_resets_omitted_attributes_of_given_sections(self):
        self.device(SYSTEM_SET)
        result = self.run_state("replaced", True, config={
            "pon_ont": {"sn_bundle_timer": 5},
            "syslog": {"version": "rfc5424", "destinations": [{"name": "ams", "disable": True}]},
        })
        assert result["commands"] == [
            "configure system syslog no time-format",
            "configure system syslog destination ams no upload-rotate no persist-enable no persist-timer",
            "configure system pon-ont no slid-mode no pwrbrst-mode no sw-ver-mis-block no sn-autounlock",
        ]

    def test_deleted_resets_given_sections(self):
        self.device(SYSTEM_SET)
        result = self.run_state("deleted", True, config={
            "nt_sftp": {"write_enable": True}, "auto_switch": {"xdsl_atm_ptm": True}, "syslog": {"version": "x"}})
        assert result["commands"] == [
            "configure system syslog no version no time-format",
            "configure system syslog destination ams no disable no upload-rotate no persist-enable no persist-timer",
            "configure system syslog route ams no syslog-vlan",
            "configure system auto-switch no xdsl-atm-ptm no xdsl-stepup-delay",
            "configure system nt-sftp no write-enable",
        ]

    def test_overridden_resets_omitted_sections(self):
        self.device(SYSTEM_SET)
        commands = self.run_state("overridden", True, config=dict(SYSTEM_SET_PARSED, nt_sftp=None, pon_ont={"sn_autounlock": "enable"}))["commands"]
        assert commands == [
            "configure system pon-ont no slid-mode no pwrbrst-mode no sn-bundle-timer no sw-ver-mis-block",
            "configure system nt-sftp no write-enable",
        ]


# ---------------------------------------------------------------- isam_cfm slm

class TestCfmSlm(_Base):
    module = isam_cfm

    def test_parsed_default_and_value(self):
        assert self.run_state("parsed", False, running_config="configure cfm slm no inactivity-time")["parsed"]["slm"] == {}
        assert self.run_state("parsed", False, running_config="configure cfm slm inactivity-time 100")["parsed"]["slm"] == {}
        assert self.run_state("parsed", False, running_config="configure cfm slm inactivity-time 30")["parsed"]["slm"] == {"inactivity_time": 30}

    def test_round_trip(self):
        rendered = self.run_state("rendered", False, config={"slm": {"inactivity_time": 30}})["rendered"]
        assert rendered == ["configure cfm slm inactivity-time 30"]
        assert self.run_state("parsed", False, running_config=rendered[0])["parsed"]["slm"] == {"inactivity_time": 30}

    def test_merged_idempotent_and_change(self):
        self.device("configure cfm slm inactivity-time 30\n")
        assert self.run_state("merged", False, config={"slm": {"inactivity_time": 30}})["commands"] == []
        assert self.run_state("merged", True, config={"slm": {"inactivity_time": 40}})["commands"] == ["configure cfm slm inactivity-time 40"]

    def test_replaced_and_deleted_reset(self):
        self.device("configure cfm slm inactivity-time 30\n")
        assert self.run_state("replaced", False, config={"domains": [{"domain_index": 1}]})["commands"] == []
        assert self.run_state("replaced", True, config={"domains": [{"domain_index": 1}], "slm": {}})["commands"] == [
            "configure cfm slm no inactivity-time"]
        assert self.run_state("deleted", True)["commands"] == ["configure cfm slm no inactivity-time"]
        self.device("configure cfm slm no inactivity-time\n")
        assert self.run_state("deleted", False)["commands"] == []


# ---------------------------------------------------------------- isam_vlan_global

class TestVlanBroadcastPriorityPolicy(_Base):
    module = isam_vlan_global

    def test_parsed(self):
        parsed = self.run_state("parsed", False, running_config="configure vlan broadcast-frames priority-policy vlan-specific")["parsed"]
        assert parsed == {"broadcast_frames": {"priority_policy": "vlan-specific"}}
        parsed = self.run_state("parsed", False, running_config="configure vlan broadcast-frames no priority-policy")["parsed"]
        assert parsed == {}

    def test_round_trip(self):
        config = {"broadcast_frames": {"priority_policy": "port-default"}}
        rendered = self.run_state("rendered", False, config=config)["rendered"]
        assert rendered == ["configure vlan broadcast-frames priority-policy port-default"]
        assert self.run_state("parsed", False, running_config=rendered[0])["parsed"] == config

    def test_merged_idempotent_replaced_deleted(self):
        self.device("configure vlan broadcast-frames priority-policy vlan-specific\n")
        assert self.run_state("merged", False, config={"broadcast_frames": {"priority_policy": "vlan-specific"}})["commands"] == []
        assert self.run_state("replaced", True, config={"broadcast_frames": {"drop_unknown_multicast": True}})["commands"] == [
            "configure vlan broadcast-frames no priority-policy",
            "configure vlan broadcast-frames drop-unknown-multicast",
        ]
        assert self.run_state("deleted", True)["commands"] == ["configure vlan broadcast-frames no priority-policy"]


# ---------------------------------------------------------------- isam_mcast_general

class TestMcastFastChangeAttributes(_Base):
    module = isam_mcast_general

    def test_parsed_detail_and_values(self):
        detail = "configure mcast general fast-change no pkg-memb-bitmap no max-bitrate no mean-bit-rate"
        assert self.run_state("parsed", False, running_config=detail)["parsed"] == {"fast_change": True}
        parsed = self.run_state("parsed", False, running_config=(
            "configure mcast general fast-change pkg-memb-bitmap 0x0f max-bitrate 20000 mean-bit-rate 8000"))["parsed"]
        assert parsed == {"fast_change": True, "pkg_memb_bitmap": "0x0f", "max_bitrate": 20000, "mean_bit_rate": 8000}

    def test_round_trip(self):
        config = {"pkg_memb_bitmap": "0x0f", "max_bitrate": 20000, "mean_bit_rate": 8000}
        rendered = self.run_state("rendered", False, config=config)["rendered"]
        assert self.run_state("parsed", False, running_config="\n".join(rendered))["parsed"] == config

    def test_merged_idempotent_replaced_deleted(self):
        self.device("configure mcast general fast-change pkg-memb-bitmap 0x0f max-bitrate 20000 no mean-bit-rate\n")
        assert self.run_state("merged", False, config={"fast_change": True, "max_bitrate": 20000})["commands"] == []
        replaced = self.run_state("replaced", True, config={"fast_change": True, "max_bitrate": 100})["commands"]
        assert " ".join(replaced).replace("configure mcast general ", "") == "no pkg-memb-bitmap max-bitrate 100"
        deleted = self.run_state("deleted", True)["commands"]
        assert "no pkg-memb-bitmap" in " ".join(deleted) and "no max-bitrate" in " ".join(deleted)
        assert "mean-bit-rate" not in " ".join(deleted)


# ---------------------------------------------------------------- capture gap report

# What the gap report still lists for these families against the lab capture: all false
# positives (attribute modelled under another option name, identity tokens, list members,
# or names the report itself mangles), never a real gap.
FALSE_POSITIVES = {
    "system": {
        "system id": ["contact-person"],                     # -> id.contact
        "system sntp server-ip-addr": ["enable"],             # -> sntp.enabled
        "system max-lt-link-speed": ["link-speed"],           # -> max_lt_link_speed
        "system sync-if-timing synce": ["synce-1", "synce-2"],  # identity -> sync_if_timing.synce[].reference
        # severity flags -> syslog.routes[].severities (list members); the heuristic node name
        # differs per route and only the not-learned names are listed
        "system syslog route": None,
        "system syslog route ams": None,
        "system syslog route ntb": None,
        "system syslog route diagnostic": None,
    },
    "equipment_replan": {"equipment replan": ["boardautoreplan"]},   # -> board_auto_replan
    "software_mngt": {"software-mngt database": ["auto-backup-intvl"]},  # -> database.auto_backup_interval
    "cwmp_plt": {"cwmp plt": ["adminstate"]},                          # -> admin_state
    "qos_maps": {"qos dscp-map-dot1p": ["dot1p-value"]},               # -> dscp_map_dot1p[].dot1p
    "ethernet_line": {"ethernet line mau": ["type"]},                  # -> mau[].mau_type
    # alarm names ending in auth/key (e.g. reg-auth) make the report redact the next token
    "alarm": {"alarm entry": ["<redacted>"]},
    "isam_vlan_global": {},
    "mcast_general": {},
    "isam_cfm": {},
}
SEVERITIES = {"emergency", "alert", "critical", "error", "warning", "notice", "information", "debug"}


def test_gap_report_down_to_false_positives():
    report = gap_report(parse_config_tree(lab_captures.detail()))["families"]
    for family, expected in FALSE_POSITIVES.items():
        unmodelled = report.get(family, {}).get("unmodelled", {})
        assert set(unmodelled) <= set(expected), (family, sorted(set(unmodelled) - set(expected)))
        for node, attrs in unmodelled.items():
            if expected[node] is None:
                assert set(attrs) <= SEVERITIES, (family, node, attrs)
            else:
                assert attrs == expected[node], (family, node, attrs)
