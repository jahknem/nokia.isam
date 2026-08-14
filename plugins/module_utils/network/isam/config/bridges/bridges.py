#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_bridges config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.bridges import (
    BridgesTemplate,
)


# Port-level parsers (fields on configure bridge port <id>)
PORT_PARSERS = [
    "bridge_port",
    "pvid",
    "default_priority",
    "mac_learn_off",
    "max_unicast_mac",
    "qos_profile",
    "prio_regen_prof",
    "prio_regen_name",
    "max_comitted_mac",
    "mirror_mode",
    "mirror_vlan",
    "pvid_tagging_flag",
    "ds_pbit_mode",
]

# Vlan-level parsers (fields on configure bridge port <id> vlan-id <vid>)
VLAN_PARSERS = [
    "tag",
    "l2fwder_vlan",
    "network_vlan",
    "vlan_scope",
    "qos",
    "vlan_qos_profile",
    "prior_best_effort",
    "prior_background",
    "prior_spare",
    "prior_exc_effort",
    "prior_ctrl_load",
    "prior_less_100ms",
    "prior_less_10ms",
    "prior_nw_ctrl",
    "in_qos_prof_name",
    "max_up_qos_policy",
    "max_ip_antispoof",
    "vlan_max_unicast_mac",
    "max_ipv6_antispf",
    "mac_learn_ctrl",
    "min_cvlan_id",
    "max_cvlan_id",
    "ds_dedicated_q",
    "tpid",
]


class Bridges(ResourceModule):
    """
    The isam_bridges config class
    """

    def __init__(self, module):
        super(Bridges, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="bridges",
            tmplt=BridgesTemplate(),
        )
        # Top-level parsers (bridge-wide fields)
        self.parsers = [
            "ageing_time",
        ]

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        try:
            if self.state == "rendered":
                self.generate_commands()
            elif self.state not in ["parsed", "gathered"]:
                self.generate_commands()
                if not self._module.check_mode:
                    self.run_commands()
                else:
                    self.changed = bool(self.commands)
        except ValueError as exc:
            self._module.fail_json(msg=str(exc))
        return self.result

    @staticmethod
    def _normalize_keys(data):
        """Add underscored versions of hyphenated keys for template matching.
        Returns a new dict; does not modify the original.
        """
        if not isinstance(data, dict):
            return data
        result = dict(data)
        for key in list(data.keys()):
            if "-" in key:
                result[key.replace("-", "_")] = data[key]
        return result

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        # Handle top-level bridge-wide fields (e.g. ageing_time)
        want_top = {}
        have_top = {}
        if isinstance(self.want, dict):
            want_top = {k: v for k, v in self.want.items() if k != "port"}
        if isinstance(self.have, dict):
            have_top = {k: v for k, v in self.have.items() if k != "port"}
        if self.state != "deleted":
            self.compare(parsers=self.parsers, want=want_top, have=have_top)

        # Handle port-level fields
        wantd = self._index_by_port(self.want)
        haved = self._index_by_port(self.have)

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # Keep requested identities for targeted deletion.  A bridge port can
        # contain several VLANs, so deleting the port entry wholesale would
        # incorrectly remove VLAN siblings.
        if self.state == "deleted":
            if not wantd:
                wantd = {}
            else:
                haved = {k: v for k, v in iteritems(haved) if k in wantd}

        # remove superfluous config for overridden and unqualified deleted
        if self.state == "overridden" or (self.state == "deleted" and not self.want):
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        """Compare want vs have for a single bridge port,
        including per-vlan entries.
        """
        # Normalize hyphenated keys in both want and have so that
        # template parsers with underscored names (e.g. default_priority)
        # can find values stored under hyphenated argspec keys.
        want = self._normalize_keys(want)
        have = self._normalize_keys(have)

        # Add 'id' (port name) for template setvals that reference {{ id }}
        if isinstance(want, dict) and "port" in want and "id" not in want:
            want["id"] = want["port"]
        if isinstance(have, dict) and "port" in have and "id" not in have:
            have["id"] = have["port"]

        # Compare VLAN-level fields.
        port_name = None
        if isinstance(want, dict):
            port_name = want.get("port") or want.get("id")
        if port_name is None and isinstance(have, dict):
            port_name = have.get("port") or have.get("id")

        # want vlans come from the argspec 'vlan_id' list
        want_vlans = {}
        if isinstance(want, dict):
            vlan_list = want.get("vlan_id", [])
            if isinstance(vlan_list, list):
                for entry in vlan_list:
                    if isinstance(entry, dict) and "id" in entry:
                        want_vlans[entry["id"]] = entry

        # have vlans: support both 'vlan_id' list (facts module) and
        # 'vlan' dict (template parser result)
        have_vlans = {}
        if isinstance(have, dict):
            vlan_list = have.get("vlan_id", [])
            if isinstance(vlan_list, list):
                for entry in vlan_list:
                    if isinstance(entry, dict) and "id" in entry:
                        have_vlans[entry["id"]] = entry
            vlan_dict = have.get("vlan", {})
            if isinstance(vlan_dict, dict):
                for vid, entry in vlan_dict.items():
                    if vid not in have_vlans:
                        have_vlans[vid] = entry

        if self.state == "deleted":
            requested_vlans = set(want_vlans)
            requested_port_fields = {
                key for key in want
                if key not in {"port", "id", "vlan_id"}
            }
            if requested_vlans:
                for vid in requested_vlans:
                    if vid in have_vlans:
                        self.commands.append(
                            "configure bridge port %s no vlan-id %s" % (port_name, vid)
                        )
                return
            if requested_port_fields:
                selected = {
                    key: value for key, value in have.items()
                    if key in requested_port_fields
                }
                for field, value in iteritems(selected):
                    if field in PORT_PARSERS:
                        if field == "pvid":
                            self.commands.append(
                                "configure bridge port %s no pvid" % port_name
                            )
                        else:
                            self.addcmd(
                                {"id": port_name, field: value}, field, negate=True
                            )
                return
            if have.get("pvid") is not None:
                self.commands.append(
                    "configure bridge port %s no pvid" % port_name
                )
            for vid in have_vlans:
                self.commands.append(
                    "configure bridge port %s no vlan-id %s" % (port_name, vid)
                )
            return

        # Compare port-level fields after the deletion branch so a targeted
        # deletion cannot reset unrelated port settings through defaults.
        port_start = len(self.commands)
        self.compare(parsers=PORT_PARSERS, want=want, have=have)
        port_commands = self.commands[port_start:]
        self.commands[port_start:] = [
            command for command in port_commands if " pvid " not in command
        ]
        deferred_pvid_commands = [
            command for command in port_commands if " pvid " in command
        ]

        service_vlans = [
            vid for vid, entry in want_vlans.items()
            if isinstance(entry, dict) and entry.get("l2fwder_vlan") is not None
        ]
        if service_vlans and want.get("pvid") is not None and self.state != "rendered":
            pvid_vid = str(want["pvid"])
            pvid_present = any(str(key) == pvid_vid for key in have_vlans)
            if not pvid_present:
                raise ValueError(
                    "bridge port %s requires VLAN %s/PVID to be configured "
                    "before service VLANs %s; apply the bridge bootstrap "
                    "state first" % (port_name, pvid_vid, ", ".join(map(str, service_vlans)))
                )

        for vid in want_vlans:
            want_vlan = want_vlans[vid]
            have_vlan = have_vlans.pop(vid, {})
            want_vlan = dict(want_vlan) if isinstance(want_vlan, dict) else {}
            have_vlan = dict(have_vlan) if isinstance(have_vlan, dict) else {}
            want_vlan = self._normalize_keys(want_vlan)
            have_vlan = self._normalize_keys(have_vlan)
            if want_vlan.get("l2fwder_vlan") is not None:
                want_vlan["l2fwder_vlan"] = str(want_vlan["l2fwder_vlan"])
            if have_vlan.get("l2fwder_vlan") is not None:
                have_vlan["l2fwder_vlan"] = str(have_vlan["l2fwder_vlan"])
            if want_vlan.get("network_vlan") is not None and want_vlan.get("l2fwder_vlan") is None:
                raise ValueError(
                    "bridge VLAN %s on %s requires l2fwder_vlan before network_vlan" %
                    (vid, port_name)
                )
            # Strip "none" string values — these come from argspec defaults
            # (qos, qos_profile) and represent "not set" in the Nokia CLI.
            want_vlan = {k: v for k, v in want_vlan.items() if v != "none"}
            have_vlan = {k: v for k, v in have_vlan.items() if v != "none"}
            # Inject template variables needed by VLAN-level setvals
            want_vlan["vlan_id"] = vid
            want_vlan["id"] = port_name
            vlan_start = len(self.commands)
            self.compare(parsers=VLAN_PARSERS, want=want_vlan, have=have_vlan)
            vlan_commands = self.commands[vlan_start:]
            vlan_prefix = "configure bridge port %s vlan-id %s" % (port_name, vid)
            tag_command = next(
                (command for command in vlan_commands if command.startswith(vlan_prefix + " tag ")), None
            )
            l2fwder_command = next(
                (
                    command for command in vlan_commands
                    if command.startswith(vlan_prefix + " l2fwder-vlan ")
                ),
                None,
            )
            if tag_command and l2fwder_command:
                vlan_commands = [
                    command for command in vlan_commands
                    if command != tag_command and command != l2fwder_command
                ]
                vlan_commands.insert(
                    0,
                    "%s %s %s" % (
                        vlan_prefix,
                        tag_command[len(vlan_prefix) + 1:],
                        l2fwder_command[len(vlan_prefix) + 1:],
                    ),
                )
            self.commands[vlan_start:] = vlan_commands

        # remaining vlans in have (present in running but not in want)
        for vid, have_vlan in iteritems(have_vlans):
            have_vlan = dict(have_vlan) if isinstance(have_vlan, dict) else {}
            have_vlan = self._normalize_keys(have_vlan)
            # Strip "none" string values
            have_vlan = {k: v for k, v in have_vlan.items() if v != "none"}
            have_vlan["vlan_id"] = vid
            have_vlan["id"] = port_name
            self.compare(parsers=VLAN_PARSERS, want={}, have=have_vlan)

        self.commands.extend(deferred_pvid_commands)

    def _index_by_port(self, data):
        if not data:
            return {}
        if isinstance(data, dict):
            data = data.get("port", [])
        indexed = {}
        for entry in data:
            port = entry.get("port") or entry.get("id")
            if port:
                indexed[port] = entry
        return indexed
