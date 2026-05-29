# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
import re
__metaclass__ = type

"""
The isam bridges fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.bridges.bridges import (
    BridgesArgs,
)

class BridgesFacts(object):
    """ The isam bridges facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = BridgesArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Bridges network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}

        # if not debugpy.is_client_connected():
        #     debugpy.listen(("localhost",3000))
        #     debugpy.wait_for_client()
        if not data:
            data = connection.get("info configure bridge flat")
        
        bridge_config = self._parse_bridge_config(data)

        ansible_facts['ansible_network_resources'].pop('bridges', None)

        # debugpy.breakpoint()

        facts['bridges'] = utils.remove_empties(bridge_config) or {}
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def _parse_bridge_config(self, config):
        bridge = {"port": []}
        ports = {}
        bridge_port_re = re.compile(r"^configure bridge port (?P<port>\S+)(?:\s+(?P<rest>.*))?$")
        bridge_vlan_re = re.compile(r"^configure bridge port (?P<port>\S+) vlan-id (?P<vlan_id>\S+)(?:\s+(?P<rest>.*))?$")

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or not line.startswith("configure bridge"):
                continue

            if line.startswith("configure bridge ageing-time "):
                try:
                    bridge["ageing_time"] = int(line.rsplit(" ", 1)[1])
                except (TypeError, ValueError):
                    pass
                continue
            if line == "configure bridge no ageing-time":
                bridge["ageing_time"] = 300
                continue

            vlan_match = bridge_vlan_re.match(line)
            if vlan_match:
                port_id = vlan_match.group("port")
                vlan_id = vlan_match.group("vlan_id")
                rest = vlan_match.group("rest") or ""
                port_entry = ports.setdefault(port_id, {"port": port_id, "vlan_id": []})
                vlan_entry = self._ensure_vlan_entry(port_entry, vlan_id)
                self._apply_vlan_rest(vlan_entry, rest)
                continue

            port_match = bridge_port_re.match(line)
            if port_match:
                port_id = port_match.group("port")
                rest = port_match.group("rest") or ""
                port_entry = ports.setdefault(port_id, {"port": port_id, "vlan_id": []})
                self._apply_port_rest(port_entry, rest)

        bridge["port"] = sorted(ports.values(), key=lambda item: item.get("port", ""))
        return bridge

    def _ensure_vlan_entry(self, port_entry, vlan_id):
        for entry in port_entry["vlan_id"]:
            if entry.get("id") == vlan_id:
                return entry
        entry = {"id": vlan_id}
        port_entry["vlan_id"].append(entry)
        return entry

    def _apply_port_rest(self, port_entry, rest):
        if not rest:
            return
        tokens = rest.split()
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "no" and i + 1 < len(tokens):
                key = tokens[i + 1].replace("-", "_")
                if key in {"mac_learn_off"}:
                    port_entry[key] = False
                i += 2
                continue

            key = token.replace("-", "_")
            if key == "mac_learn_off":
                port_entry[key] = True
                i += 1
                continue

            if i + 1 < len(tokens):
                port_entry[key] = self._normalize_value([tokens[i + 1]])
                i += 2
            else:
                i += 1

    def _apply_vlan_rest(self, vlan_entry, rest):
        if not rest:
            return
        tokens = rest.split()
        bool_keys = {
            "prior_best_effort",
            "prior_background",
            "prior_spare",
            "prior_exc_effort",
            "prior_ctrl_load",
            "prior_less_100ms",
            "prior_less_10ms",
            "prior_nw_ctrl",
        }
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token == "no" and i + 1 < len(tokens):
                key = tokens[i + 1].replace("-", "_")
                if key in bool_keys:
                    vlan_entry[key] = False
                i += 2
                continue

            key = token.replace("-", "_")
            if key in bool_keys:
                vlan_entry[key] = True
                i += 1
                continue

            if i + 1 < len(tokens):
                vlan_entry[key] = self._normalize_value([tokens[i + 1]])
                i += 2
            else:
                i += 1

    def _normalize_value(self, parts):
        if not parts:
            return None
        if len(parts) >= 2 and parts[0] == "name" and parts[1] == ":":
            return "name:" + " ".join(parts[2:])
        value = " ".join(parts)
        if value.isdigit():
            return int(value)
        return value
