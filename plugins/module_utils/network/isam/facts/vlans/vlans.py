# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import re
import shlex

__metaclass__ = type

"""
The isam vlans fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VlansTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import (
    VlansArgs,
)


class VlansFacts(object):
    """ The isam vlans facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = VlansArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Vlans network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = connection.get("info configure vlan id flat")

        # parse native config using the Vlans template
        vlans_parser = VlansTemplate(lines=self._flatten_config(data), module=self._module)
        objs = list(vlans_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('vlans', None)

        params = utils.remove_empties(
            vlans_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}

        facts['vlans'] = params.get('config') or []
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def _flatten_config(self, data):
        if any(line.strip().startswith("configure vlan id ") for line in (data or "").splitlines()):
            result = []
            flag_keys = {
                "sntp-proxy", "vmac-not-in-opt61", "drly-srv-usr-side", "dhcp-opt82-nni",
                "dhcp-opt82-uplink", "relay-id-dhcp", "dhcp-linerate", "pppoe-linerate",
                "dhcpv6-linerate", "pppoe-l2-encaps", "dhcp-l2-encaps", "dhcpv6-l2-encaps",
                "l2-encaps1", "pppoer-vlanaware", "dhcpr-vlanaware", "dhcpv6r-vlanaware",
                "dhcpv6-relay-id", "dhcpv6-trst-port", "vmac-translation", "vmac-dnstr-filter",
                "icmpv6-sec-fltr", "l2cp-transparent", "ipv4-mcast-ctrl", "ipv6-mcast-ctrl",
                "mac-mcast-ctrl", "dis-proto-rip", "proto-ntp", "dis-ip-antispoof",
                "unknown-unicast", "pt2ptgem-flooding", "mac-movement-ctrl", "arp-snooping",
                "arp-polling", "mac-unauth",
            }
            value_keys = {
                "mode", "name", "priority", "new-broadcast", "protocol-filter", "pppoe-relay-tag",
                "new-secure-fwd", "aging-time", "in-qos-prof-name", "dhcp-opt82-ext",
                "circuit-id-dhcp", "remote-id-dhcp", "circuit-id-pppoe", "remote-id-pppoe",
                "dhcpv6-itf-id", "dhcpv6-remote-id", "enterprise-number", "arp-polling-ip",
                "cvlan4095passthru",
            }
            for line in data.splitlines():
                line = line.strip()
                if not line.startswith("configure vlan id "):
                    continue
                match = re.match(r"configure vlan id (\S+)\s+(.*)", line)
                if not match:
                    result.append(line)
                    continue
                vlan_id, body = match.groups()
                tokens = shlex.split(body)
                result.append("id {0}".format(vlan_id))
                index = 0
                while index < len(tokens):
                    negate = tokens[index] == "no"
                    key_index = index + 1 if negate else index
                    if key_index >= len(tokens):
                        break
                    key = tokens[key_index]
                    if key in flag_keys:
                        result.append("  {0}{1}".format("no " if negate else "", key))
                        index = key_index + 1
                    elif key in value_keys and key_index + 1 < len(tokens):
                        result.append(
                            "  {0}{1} {2}".format(
                                "no " if negate else "", key, tokens[key_index + 1]
                            )
                        )
                        index = key_index + 2
                    else:
                        index += 1
            return result
        lines = []
        current_id = None
        for line in (data or "").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("echo"):
                continue
            if stripped in ("configure", "configure vlan", "exit"):
                continue

            if stripped.startswith("id "):
                parts = stripped.split()
                if len(parts) > 1:
                    current_id = parts[1]
                lines.append(stripped)
            elif current_id and line[:1].isspace():
                lines.append("id {0} {1}".format(current_id, stripped))
            else:
                lines.append(stripped)
        return lines
