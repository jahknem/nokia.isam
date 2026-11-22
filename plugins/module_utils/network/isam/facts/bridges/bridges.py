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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    normalize_bridge_vlan_alias,
    parse_cli_key_values,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read_outcomes import (
    ReadOutcomeCollector,
)


PORT_BOOL_KEYS = {
    "mac_learn_off",
}

VLAN_BOOL_KEYS = {
    "prior_best_effort",
    "prior_background",
    "prior_spare",
    "prior_exc_effort",
    "prior_ctrl_load",
    "prior_less_100ms",
    "prior_less_10ms",
    "prior_nw_ctrl",
}

# str-typed options whose device values may be all digits (e.g. TPID 8100).
PORT_STR_KEYS = ("default_tpid",)
VLAN_STR_KEYS = ("tpid", "inner_pbit_remark", "groupid", "usacceptframetype", "oltregenprofile")

VLAN_TPID_RE = re.compile(r"^vlan-tpid(?P<index>\d+)\s+\S+(?:\s+(?P<rest>.*))?$")


class BridgesFacts(object):
    """ The isam bridges facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = BridgesArgs.argument_spec

    def get_config(self, connection):
        config = self._module.params.get("config") or {}
        ports = config.get("port", []) if isinstance(config, dict) else config
        ports = ports or []
        # A gathered read must match the complete read's compact form: 'flat detail' also
        # prints every default ("no <attr>"), which the complete read omits, so the two would
        # parse into different configurations. Writes keep the detail form.
        suffix = "flat" if self._module.params.get("state") == "gathered" else "flat detail"
        commands = []
        selectors = {}
        for item in ports:
            port_id = item.get("port") or item.get("id")
            if port_id:
                command = "info configure bridge port %s %s" % (port_id, suffix)
                commands.append(command)
                selectors[command] = port_id
        collector = None
        if self._module.params.get("state") == "gathered":
            collector = ReadOutcomeCollector("bridges")
        data = get_scoped_config(
            self._module,
            connection,
            config,
            "info configure bridge flat",
            commands,
            outcomes=collector,
            selectors=selectors,
            # A gathered read that names port entries is explicitly targeted: if none of
            # them can become a read command, fail rather than silently widen to the whole
            # family.
            require_targeted=bool(ports),
        )
        if commands:
            data = "\n".join(
                line for line in data.splitlines()
                if not line.startswith("configure bridge ageing-time ")
                and not line.startswith("configure bridge no ageing-time")
            )
        if collector is not None:
            # _parse_bridge_config processes lines independently and silently skips lines it
            # does not recognize, and the read is combined across ports; it cannot demonstrate
            # full coverage of the owned lines, so the parse outcome is unverified.
            collector.record_parse("unverified")
            self._module._isam_read_outcomes = collector.to_result()
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Bridges network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}

        if not data:
            data = self.get_config(connection)

        bridge_config = self._parse_bridge_config(data)

        ansible_facts['ansible_network_resources'].pop('bridges', None)

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
        # "vlan-tpid<n> <n> [no] tpid <hex>": a per-port sub-node, not a key/value pair.
        tpid_match = VLAN_TPID_RE.match(rest)
        if tpid_match:
            sub = parse_cli_key_values((tpid_match.group("rest") or "").split())
            self._stringify(sub, ("tpid",))
            if sub:
                key = "vlan_tpid%s" % tpid_match.group("index")
                port_entry.setdefault(key, {}).update(sub)
            return
        self._apply_rest(port_entry, rest, PORT_BOOL_KEYS)
        self._stringify(port_entry, PORT_STR_KEYS)

    @staticmethod
    def _stringify(entry, keys):
        # Hex TPIDs such as 8100 and free-form values must not be read back as int.
        for key in keys:
            if entry.get(key) is not None and not isinstance(entry[key], str):
                entry[key] = str(entry[key])

    def _apply_vlan_rest(self, vlan_entry, rest):
        static_user_match = re.match(
            r"^static-user\s+ip-address\s+(?P<ip_address>\S+)$", rest
        )
        if static_user_match:
            static_user = vlan_entry.setdefault("static_user", [])
            ip_address = static_user_match.group("ip_address")
            if not any(entry.get("ip_address") == ip_address for entry in static_user):
                static_user.append({"ip_address": ip_address})
            return
        # Legacy "network-vlan" is reported as the canonical l2fwder_vlan key.
        self._apply_rest(
            vlan_entry, rest, VLAN_BOOL_KEYS, normalize_bridge_vlan_alias
        )
        self._stringify(vlan_entry, VLAN_STR_KEYS)

    def _apply_rest(self, entry, rest, bool_keys, canonicalize=None):
        if not rest:
            return
        parsed = parse_cli_key_values(
            rest.split(),
            bool_fields=bool_keys,
            infer_numeric=True,
        )
        if canonicalize is not None:
            parsed = canonicalize(parsed)
        entry.update(parsed)
