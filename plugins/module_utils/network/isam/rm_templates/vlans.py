# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Parser templates for the isam_vlans resource.

The device prints a VLAN as two packed lines ('flat detail', lab ISAM)::

    configure vlan id 99 mode residential-bridge name TR69-1 no sntp-proxy no priority ...
    configure vlan id 99 no vmac-translation ... dhcp-opt82-ext add-or-forward ...

VLAN_ATTRS below is the single description of that grammar: the facts split packed lines
into one attribute per line with it, the parsers are generated from it (one per
attribute), and the config class takes the device defaults from it.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

# (option, CLI keyword, kind, device default) in the device's order. Kinds and defaults
# follow the CLI guide's syntax ("[ [ no ] kw ]" is a flag, "[ no kw | kw <type> ]" a
# value); the value kinds were confirmed on the lab ISAM (a bare value keyword is "not
# complete"). "dhcp-opt-82" is not modelled: the device stores it as dhcp-opt82-ext enable.
# kind: "flag" ([no] <kw>), "value" (<kw> <value> / no <kw>), "int" (value as int),
# "set_only" (<kw> <value>, no removal form). A device default equals an unset value.
VLAN_ATTRS = (
    ("mode", "mode", "set_only", None),
    ("name", "name", "value", None),
    ("sntp_proxy", "sntp-proxy", "flag", False),
    ("priority", "priority", "int", None),
    ("vmac_not_in_opt61", "vmac-not-in-opt61", "flag", False),
    ("new_broadcast", "new-broadcast", "value", "inherit"),
    ("protocol_filter", "protocol-filter", "value", "pass-all"),
    ("pppoe_relay_tag", "pppoe-relay-tag", "value", None),
    ("drly_srv_usr_side", "drly-srv-usr-side", "value", "disable"),
    ("new_secure_fwd", "new-secure-fwd", "value", None),
    ("aging_time", "aging-time", "int", None),
    ("l2cp_transparent", "l2cp-transparent", "flag", False),
    ("in_qos_prof_name", "in-qos-prof-name", "value", None),
    ("ipv4_mcast_ctrl", "ipv4-mcast-ctrl", "flag", False),
    ("ipv6_mcast_ctrl", "ipv6-mcast-ctrl", "flag", False),
    ("mac_mcast_ctrl", "mac-mcast-ctrl", "flag", False),
    ("dis_proto_rip", "dis-proto-rip", "flag", False),
    ("proto_ntp", "proto-ntp", "flag", False),
    ("dis_ip_antispoof", "dis-ip-antispoof", "flag", False),
    ("unknown_unicast", "unknown-unicast", "flag", False),
    ("pt2ptgem_flooding", "pt2ptgem-flooding", "flag", False),
    ("mac_movement_ctrl", "mac-movement-ctrl", "flag", False),
    ("cvlan4095passthru", "cvlan4095passthru", "value", None),
    ("arp_snooping", "arp-snooping", "flag", False),
    ("arp_polling", "arp-polling", "flag", False),
    ("arp_polling_ip", "arp-polling-ip", "value", None),
    ("mac_unauth", "mac-unauth", "flag", False),
    ("vmac_translation", "vmac-translation", "flag", False),
    ("vmac_dnstr_filter", "vmac-dnstr-filter", "flag", False),
    ("dhcp_opt82_ext", "dhcp-opt82-ext", "value", None),
    ("dhcp_opt82_nni", "dhcp-opt82-nni", "value", "disable"),
    ("dhcp_opt82_uplink", "dhcp-opt82-uplink", "value", "disable"),
    ("circuit_id_dhcp", "circuit-id-dhcp", "value", None),
    ("remote_id_dhcp", "remote-id-dhcp", "value", None),
    ("relay_id_dhcp", "relay-id-dhcp", "value", "disable"),
    ("dhcp_linerate", "dhcp-linerate", "value", "notadd"),
    ("pppoe_linerate", "pppoe-linerate", "value", "notadd"),
    ("dhcpv6_linerate", "dhcpv6-linerate", "value", "notadd"),
    ("pppoe_l2_encaps", "pppoe-l2-encaps", "value", "notadd"),
    ("dhcp_l2_encaps", "dhcp-l2-encaps", "value", "notadd"),
    ("dhcpv6_l2_encaps", "dhcpv6-l2-encaps", "value", "notadd"),
    ("l2_encaps1", "l2-encaps1", "value", "not-applicable"),
    ("pppoer_vlanaware", "pppoer-vlanaware", "value", "system-default"),
    ("dhcpr_vlanaware", "dhcpr-vlanaware", "value", "system-default"),
    ("dhcpv6r_vlanaware", "dhcpv6r-vlanaware", "value", "system-default"),
    ("circuit_id_pppoe", "circuit-id-pppoe", "value", None),
    ("remote_id_pppoe", "remote-id-pppoe", "value", None),
    ("dhcpv6_itf_id", "dhcpv6-itf-id", "value", None),
    ("dhcpv6_remote_id", "dhcpv6-remote-id", "value", None),
    ("dhcpv6_relay_id", "dhcpv6-relay-id", "value", "disable"),
    ("dhcpv6_trst_port", "dhcpv6-trst-port", "value", "untrusted"),
    ("enterprise_number", "enterprise-number", "int", None),
    ("icmpv6_sec_fltr", "icmpv6-sec-fltr", "flag", False),
)

# The device prints a VLAN as two lines; the second starts with this attribute. Commands
# are packed the same way (COMPACT_COMMAND_SCOPES of the config class).
VLAN_SECOND_LINE_START = "vmac_translation"
_SPLIT = [option for option, _cli, _kind, _default in VLAN_ATTRS].index(VLAN_SECOND_LINE_START)
VLAN_LINE_KEYWORDS = (tuple(cli for _o, cli, _k, _d in VLAN_ATTRS[:_SPLIT]),
                      tuple(cli for _o, cli, _k, _d in VLAN_ATTRS[_SPLIT:]))

VLAN_DEFAULTS = dict((option, default) for option, _cli, _kind, default in VLAN_ATTRS if default is not None)
VLAN_FLAG_KEYWORDS = tuple(cli for _option, cli, kind, _default in VLAN_ATTRS if kind == "flag")
VLAN_VALUE_KEYWORDS = tuple(cli for _option, cli, kind, _default in VLAN_ATTRS if kind != "flag")

_ID = r"^configure\svlan\sid\s(?P<id>\d+|stacked:\d+:\d+)\s"
_SCOPE = "configure vlan id {{ id }}"


def _result(option, value):
    return {"{{ id }}": {"id": "{{ id }}", option: value}}


def _flag(option, cli):
    return {
        "name": option,
        "getval": re.compile(_ID + r"(?P<negate>no\s)?" + re.escape(cli) + r"$"),
        "setval": _SCOPE + " " + cli,
        "remval": _SCOPE + " no " + cli,
        "result": _result(option, "{{ False if negate is defined else True }}"),
    }


def _value(option, cli, kind):
    parser = {
        "name": option,
        # a value may be quoted by the device ("name \"a b\"")
        "getval": re.compile(_ID + r"(?:(?P<negate>no\s)" + re.escape(cli) + r"|" + re.escape(cli)
                             + r"\s\"?(?P<value>.+?)\"?)$"),
        "setval": _SCOPE + " " + cli + " {{ " + option + " }}",
        "remval": _SCOPE + " no " + cli,
        "result": _result(option, "{{ none if negate is defined else value" + ("|int" if kind == "int" else "") + " }}"),
    }
    if kind == "set_only":
        del parser["remval"]
        parser["no_remval"] = True
    return parser


def _name_setval(data):
    """A name with characters beyond letters, digits and _.:- is sent in double quotes,
    as the device prints it; single quotes are an invalid token (lab ISAM)."""
    name = str(data["name"])
    value = name if re.fullmatch(r"[A-Za-z0-9_.:-]+", name) else '"%s"' % name.replace('"', '\\"')
    return "configure vlan id %s name %s" % (data["id"], value)


PARSERS = [{
    # identity: a VLAN without attributes, creation and removal of the VLAN
    "name": "id",
    "getval": re.compile(r"^configure\svlan\sid\s(?P<id>\d+|stacked:\d+:\d+)$"),
    "setval": _SCOPE,
    "remval": "configure vlan no id {{ id }}",
    "result": {"{{ id }}": {"id": "{{ id }}"}},
}]
for _option, _cli, _kind, _default in VLAN_ATTRS:
    PARSERS.append(_flag(_option, _cli) if _kind == "flag" else _value(_option, _cli, _kind))
for _parser in PARSERS:
    if _parser["name"] == "name":
        _parser["setval"] = _name_setval


class VlansTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(VlansTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = PARSERS
