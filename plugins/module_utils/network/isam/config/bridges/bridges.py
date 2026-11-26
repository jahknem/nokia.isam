#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

from collections import OrderedDict

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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    covers_entry,
    normalize_bridge_vlan_alias,
    normalize_resource_keys,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.bridges import (
    PORT_DEFAULTS,
    PORT_SUBNODE_DEFAULTS,
    VLAN_DEFAULTS,
    BridgesTemplate,
    without_bridge_defaults,
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
    "max_committed_mac",
    "mirror_mode",
    "mirror_vlan",
    "pvid_tagging_flag",
    "ds_pbit_mode",
    "outervlancapture",
    "direction",
    "default_tpid",
    "vlan_tpid0",
    "vlan_tpid1",
]

# Vlan-level parsers (fields on configure bridge port <id> vlan-id <vid>)
VLAN_PARSERS = [
    "tag",
    "l2fwder_vlan",
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
    "inner_pbit_remark",
    "groupid",
    "usacceptframetype",
    "oltregenprofile",
]


# Flags whose device default is off: "no <flag>" (read as False) equals unset.
PORT_DEFAULT_OFF_FLAGS = frozenset(("mac_learn_off",))
VLAN_DEFAULT_OFF_FLAGS = frozenset((
    "prior_best_effort", "prior_background", "prior_spare", "prior_exc_effort",
    "prior_ctrl_load", "prior_less_100ms", "prior_less_10ms", "prior_nw_ctrl",
))


class Bridges(IsamResourceModule):
    """
    The isam_bridges config class
    """

    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure bridge port \S+) (?P<suffix>(?!(?:no\s+)?(?:vlan-id(?:\s|$)|pvid(?:\s|$)|vlan-tpid\d+(?:\s|$))).+)$",
        r"^(?P<scope>configure bridge port \S+ vlan-id \S+) (?P<suffix>(?!static-user(?:\s|$)).+)$",
        r"^(?P<scope>configure bridge port \S+ vlan-tpid\d+) (?P<suffix>.+)$",
    )

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
                if self._module.check_mode:
                    self.changed = bool(self.commands)
                else:
                    self.run_commands()
        except ValueError as exc:
            self._module.fail_json(msg=str(exc))
        # read_outcomes (targeted gathered reads) is attached centrally by the base
        # result property; whole-family reads carry none.
        return self.result

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
            wantd = self._merge_ports(haved, wantd)

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

    @staticmethod
    def _merge_ports(haved, wantd):
        """merged: want onto have, VLAN entries merged by id.

        netcommon's dict_merge appends lists of dicts, so a partial VLAN entry would
        sit next to the full one and replace it (its omitted attributes removed).
        """
        merged = {}
        for key in dict.fromkeys(list(haved) + list(wantd)):
            have, want = haved.get(key, {}), wantd.get(key)
            if want is None:
                merged[key] = have
                continue
            have_rest = {k: v for k, v in have.items() if k != "vlan_id"}
            want_rest = {k: v for k, v in want.items() if k != "vlan_id"}
            entry = dict_merge(have_rest, want_rest)
            if have.get("vlan_id") or want.get("vlan_id"):
                vlans = OrderedDict((str(v.get("id")), v) for v in have.get("vlan_id") or [])
                for vlan in want.get("vlan_id") or []:
                    vid = str(vlan.get("id"))
                    vlans[vid] = dict_merge(vlans[vid], vlan) if vid in vlans else vlan
                entry["vlan_id"] = list(vlans.values())
            merged[key] = entry
        return merged

    def _compare(self, want, have):
        """Compare want vs have for a single bridge port,
        including per-vlan entries.
        """
        want = self._normalize_port(want)
        have = self._normalize_port(have)
        port_name = self._port_name(want, have)
        want_vlans = self._index_vlans(want, include_template_vlan=False)
        have_vlans = self._index_vlans(have)

        if self.state == "deleted":
            self._delete_bridge_port(port_name, want, have, want_vlans, have_vlans)
            return

        deferred_pvid_commands = self._compare_port_fields(want, have)
        self._validate_vlan_dependencies(port_name, want, want_vlans, have_vlans)

        # A new port is built PVID VLAN first, then the PVID, then the service VLANs:
        # the device rejects service VLANs on a port without its PVID VLAN.
        pvid = str(want["pvid"]) if want.get("pvid") is not None else None
        pvid_vlan_new = pvid is not None and not any(str(vid) == pvid for vid in have_vlans)
        order = sorted(want_vlans, key=lambda vid: 0 if pvid_vlan_new and str(vid) == pvid else 1)
        for vid in order:
            have_vlan = have_vlans.pop(vid, {})
            self._compare_vlan(port_name, vid, want_vlans[vid], have_vlan)
            if pvid_vlan_new and str(vid) == pvid:
                self.commands.extend(deferred_pvid_commands)
                deferred_pvid_commands = []

        self.commands.extend(deferred_pvid_commands)

        # VLANs on the device but not wanted (replaced/overridden) leave the port,
        # after a new PVID is set. Resetting their attributes instead is refused for
        # service VLANs ("VLAN MGT error 81 : Given L2-forwarder has not been created
        # yet", lab ISAM).
        for vid in have_vlans:
            self.commands.append("configure bridge port %s no vlan-id %s" % (port_name, vid))

    def _normalize_port(self, data):
        data = normalize_resource_keys(data)
        if isinstance(data, dict) and "port" in data and "id" not in data:
            data["id"] = data["port"]
        return data

    @staticmethod
    def _port_name(want, have):
        if isinstance(want, dict):
            port_name = want.get("port") or want.get("id")
            if port_name is not None:
                return port_name
        if isinstance(have, dict):
            return have.get("port") or have.get("id")
        return None

    @staticmethod
    def _index_vlans(data, include_template_vlan=True):
        """Index per-vlan entries by VLAN id using the canonical alias mapping.

        This is the single entry point for both requested and gathered VLAN
        data, so the obsolete ``network_vlan`` alias is resolved before any
        validation, comparison or rendering. Contradictory values under both
        names are rejected here.
        """
        indexed = {}
        if not isinstance(data, dict):
            return indexed

        vlan_list = data.get("vlan_id", [])
        if isinstance(vlan_list, list):
            for entry in vlan_list:
                if isinstance(entry, dict) and "id" in entry:
                    indexed[entry["id"]] = normalize_bridge_vlan_alias(
                        entry, strict=True
                    )

        if not include_template_vlan:
            return indexed

        # Facts use vlan_id; raw template parser output may still contain vlan.
        vlan_dict = data.get("vlan", {})
        if isinstance(vlan_dict, dict):
            for vid, entry in vlan_dict.items():
                if vid not in indexed:
                    indexed[vid] = normalize_bridge_vlan_alias(entry)
        return indexed

    def _delete_bridge_port(self, port_name, want, have, want_vlans, have_vlans):
        """deleted for one requested port: an identity alone (or a whole entry) removes
        the port; named attributes reset only themselves.

        A VLAN entry is whole when it carries just its id or names every attribute the
        VLAN has (covers_entry); it is removed ("no vlan-id"). The port itself is removed
        when the request names only the port, or names every port setting it has and
        every VLAN on it as a whole entry (e.g. as gathered).
        """
        if not have:
            return
        port_keys = ("port", "id", "vlan_id", "vlan")
        want_fields = dict((k, v) for k, v in want.items() if k not in port_keys)
        have_fields = without_bridge_defaults(
            dict((k, v) for k, v in have.items() if k not in port_keys), PORT_DEFAULTS, PORT_SUBNODE_DEFAULTS)
        named_fields = set(k for k, v in want_fields.items() if v is not None)

        whole_vlans = set()
        for vid, want_vlan in want_vlans.items():
            have_vlan = have_vlans.get(vid)
            if have_vlan is not None and covers_entry(
                    want_vlan, without_bridge_defaults(have_vlan, VLAN_DEFAULTS), ("id",)):
                whole_vlans.add(str(vid))

        if not named_fields and not want_vlans:
            self.commands.append("configure bridge no port %s" % port_name)
            return
        all_vlans_whole = set(map(str, have_vlans)) <= whole_vlans
        if all_vlans_whole and covers_entry(want_fields, have_fields, ()) and (want_vlans or not have_vlans):
            self.commands.append("configure bridge no port %s" % port_name)
            return

        for field in PORT_PARSERS:  # the device's order
            if field not in named_fields or field not in have_fields:
                continue
            if field == "pvid":
                self.commands.append("configure bridge port %s no pvid" % port_name)
            else:
                self.addcmd(dict(have_fields, id=port_name), field, negate=True)

        for vid in sorted(want_vlans, key=str):
            if vid not in have_vlans:
                continue
            if str(vid) in whole_vlans:
                self.commands.append("configure bridge port %s no vlan-id %s" % (port_name, vid))
                continue
            self._reset_vlan_attributes(port_name, vid, want_vlans[vid], have_vlans[vid])

    def _reset_vlan_attributes(self, port_name, vid, want_vlan, have_vlan):
        """deleted: reset only the attributes a VLAN entry names (and remove the
        static-user addresses it names, CLI guide 24: "static-user no ip-address")."""
        named = set(k for k, v in want_vlan.items() if k != "id" and v is not None)
        have_vlan = self._normalize_vlan(port_name, vid, without_bridge_defaults(have_vlan, VLAN_DEFAULTS))
        keep = dict((k, v) for k, v in have_vlan.items() if k not in named or k in ("id", "vlan_id"))
        self.compare(parsers=VLAN_PARSERS, want=keep, have=have_vlan)
        if "static_user" in named:
            for ip_address in sorted(self._static_user_addresses(want_vlan) & self._static_user_addresses(have_vlan)):
                self.commands.append("configure bridge port %s vlan-id %s static-user no ip-address %s"
                                     % (port_name, vid, ip_address))

    @staticmethod
    def _without_default_off(data, keys):
        """Treat False of a default-off flag as absent on both sides of a compare.

        A "flat detail" read reports e.g. "no mac-learn-off" as False. Comparing that
        with an unset want made the base compare re-issue the flag in its positive
        form ("mac-learn-off", "prior-best-effort False"). False and absent mean the
        same device state, so neither side needs a command for it.
        """
        if not isinstance(data, dict):
            return data
        return {
            k: v for k, v in data.items()
            if not (v is False and (k in keys or k.replace("-", "_") in keys))
        }

    @staticmethod
    def _without_held_defaults(want, have, defaults, subnode_defaults=None):
        """An explicit default the device already has (have without defaults lacks the
        key) is no change; against a non-default value it resets to the default."""
        if not isinstance(want, dict):
            return want
        result = {}
        for key, value in want.items():
            if key in defaults and value is not None and str(defaults[key]) == str(value) and key not in have:
                continue
            if subnode_defaults and key in subnode_defaults and isinstance(value, dict):
                value = Bridges._without_held_defaults(value, have.get(key) or {}, subnode_defaults[key])
                if not value:
                    continue
            result[key] = value
        return result

    def _compare_port_fields(self, want, have):
        # Targeted deletion runs before this so defaults cannot reset unrelated settings.
        port_start = len(self.commands)
        have = without_bridge_defaults(have, PORT_DEFAULTS, PORT_SUBNODE_DEFAULTS)
        if self.state != "rendered":  # rendered has no device state: "no <flag>" stays explicit
            want = self._without_default_off(want, PORT_DEFAULT_OFF_FLAGS)
            want = self._without_held_defaults(want, have, PORT_DEFAULTS, PORT_SUBNODE_DEFAULTS)
        self.compare(parsers=PORT_PARSERS, want=want, have=have)
        return self._defer_pvid_commands(port_start)

    def _defer_pvid_commands(self, start):
        port_commands = self.commands[start:]
        deferred = [command for command in port_commands if " pvid " in command]
        self.commands[start:] = [
            command for command in port_commands if command not in deferred
        ]
        return deferred

    def _validate_vlan_dependencies(self, port_name, want, want_vlans, have_vlans):
        service_vlans = [
            vid for vid, entry in want_vlans.items()
            if isinstance(entry, dict) and entry.get("l2fwder_vlan") is not None
        ]
        if not service_vlans or want.get("pvid") is None or self.state == "rendered":
            return

        pvid_vid = str(want["pvid"])
        # Present on the device, or created first in this same request.
        pvid_present = any(str(key) == pvid_vid for key in list(have_vlans) + list(want_vlans))
        if not pvid_present:
            raise ValueError(
                "bridge port %s requires VLAN %s/PVID to be configured "
                "before service VLANs %s; apply the bridge bootstrap "
                "state first" % (port_name, pvid_vid, ", ".join(map(str, service_vlans)))
            )

    def _normalize_vlan(self, port_name, vid, data):
        data = dict(data) if isinstance(data, dict) else {}
        # Aliases are already resolved by _index_vlans; this only stamps the
        # addressing keys the parsers and templates expect.
        data = {k: v for k, v in data.items() if v != "none"}
        data["vlan_id"] = vid
        data["id"] = port_name
        return data

    def _compare_vlan(self, port_name, vid, want_vlan, have_vlan):
        # Decide on the raw gathered entry: _normalize_vlan stamps addressing
        # keys, so the normalized dict is never empty.
        vlan_exists = bool(have_vlan)
        have_vlan = without_bridge_defaults(have_vlan, VLAN_DEFAULTS)
        if self.state != "rendered":
            want_vlan = self._without_held_defaults(want_vlan, have_vlan, VLAN_DEFAULTS)
        want_vlan = self._normalize_vlan(port_name, vid, want_vlan)
        have_vlan = self._normalize_vlan(port_name, vid, have_vlan)
        vlan_start = len(self.commands)
        self.compare(
            parsers=VLAN_PARSERS,
            want=want_vlan if self.state == "rendered" else self._without_default_off(want_vlan, VLAN_DEFAULT_OFF_FLAGS),
            have=self._without_default_off(have_vlan, VLAN_DEFAULT_OFF_FLAGS),
        )
        self._compare_static_users(port_name, vid, want_vlan, have_vlan)
        vlan_commands = self.commands[vlan_start:]
        # The vlan_id parser is used by facts, not command generation. A VLAN
        # requested without any attribute still needs its base command, but an
        # already configured VLAN must not be re-created.
        if not vlan_commands and not vlan_exists:
            vlan_commands = [
                "configure bridge port %s vlan-id %s" % (port_name, vid)
            ]
        self.commands[vlan_start:] = self._order_vlan_commands(
            port_name, vid, vlan_commands
        )

    @staticmethod
    def _static_user_addresses(vlan):
        entries = vlan.get("static_user", []) if isinstance(vlan, dict) else []
        if not isinstance(entries, list):
            return set()
        return {
            entry.get("ip_address")
            for entry in entries
            if isinstance(entry, dict) and entry.get("ip_address")
        }

    def _compare_static_users(self, port_name, vid, want_vlan, have_vlan):
        """Render requested static-user addresses missing from gathered state."""
        want_addresses = self._static_user_addresses(want_vlan)
        have_addresses = self._static_user_addresses(have_vlan)
        for ip_address in sorted(want_addresses - have_addresses):
            self.commands.append(
                "configure bridge port %s vlan-id %s static-user ip-address %s"
                % (port_name, vid, ip_address)
            )

    # Attributes that the device requires to be issued together with
    # "tag"/"l2fwder-vlan" on a single "vlan-id <id> ..." command. Live
    # device captures show the full working syntax as one line, e.g.
    # "vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local
    # qos priority:5". Issuing vlan-scope or qos as separate trailing
    # commands after tag+l2fwder-vlan has already been applied is
    # rejected by the device with "VLAN MGT error 149: Such
    # configuration mode of VLAN port is not permitted".
    _MERGE_WITH_TAG_AND_L2FWDER = ("vlan-scope ", "qos ")

    @staticmethod
    def _order_vlan_commands(port_name, vid, vlan_commands):
        vlan_prefix = "configure bridge port %s vlan-id %s" % (port_name, vid)
        tag_command = Bridges._first_command_with_prefix(
            vlan_commands, vlan_prefix + " tag "
        )
        l2fwder_command = Bridges._first_command_with_prefix(
            vlan_commands, vlan_prefix + " l2fwder-vlan "
        )
        if not tag_command or not l2fwder_command:
            return vlan_commands

        mergeable = [tag_command, l2fwder_command]
        for suffix in Bridges._MERGE_WITH_TAG_AND_L2FWDER:
            command = Bridges._first_command_with_prefix(
                vlan_commands, vlan_prefix + " " + suffix
            )
            if command:
                mergeable.append(command)

        ordered = [
            command for command in vlan_commands if command not in mergeable
        ]
        merged = " ".join(
            command[len(vlan_prefix) + 1:] for command in mergeable
        )
        ordered.insert(0, "%s %s" % (vlan_prefix, merged))
        return ordered

    @staticmethod
    def _first_command_with_prefix(commands, prefix):
        return next(
            (command for command in commands if command.startswith(prefix)),
            None,
        )

    def _index_by_port(self, data):
        if not data:
            return {}
        if isinstance(data, dict):
            data = data.get("port", [])
        indexed = {}
        for entry in data:
            # Normalize before merged combines facts (underscore keys) with
            # historical CLI-spelled input keys, or the old fact value can win.
            entry = self._normalize_port(entry)
            port = entry.get("port") or entry.get("id")
            if port:
                indexed[port] = entry
        return indexed
