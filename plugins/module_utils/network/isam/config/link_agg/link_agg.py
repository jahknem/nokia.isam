# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.link_agg import (
    Link_aggTemplate,
)


class Link_agg(ResourceModule):
    """The isam_link_agg config class."""

    GROUP_FIELDS = [
        "load_sharing_policy",
        "max_active_port",
        "swo_threshold",
        "priority",
        "swo_revert",
        "mode",
        "master_iwf",
    ]

    def __init__(self, module):
        super(Link_agg, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="link_agg",
            tmplt=Link_aggTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = self._normalize_config(self.want)
        have = self._normalize_config(self.have)

        self._generate_port_commands(want.get("ports", []), have.get("ports", []))
        self._generate_group_commands(want.get("groups", []), have.get("groups", []))

    def _normalize_config(self, config):
        config = deepcopy(config or {})
        config.setdefault("ports", [])
        config.setdefault("groups", [])

        for port in config["ports"]:
            if "name" in port and "id" not in port:
                port["id"] = port["name"]
            if port.get("lacp_mode") is not None and port.get("passive_lacp") is None:
                port["passive_lacp"] = port["lacp_mode"] == "passive"
            if port.get("passive_lacp") is not None and port.get("lacp_mode") is None:
                port["lacp_mode"] = "passive" if port["passive_lacp"] else "active"
            if port.get("timeout") is not None and port.get("short_timeout") is None:
                port["short_timeout"] = port["timeout"] == "short"
            if port.get("short_timeout") is not None and port.get("timeout") is None:
                port["timeout"] = "short" if port["short_timeout"] else "long"

        for group in config["groups"]:
            if "name" in group and "id" not in group:
                group["id"] = group["name"]
            group.setdefault("ports", [])

        return config

    def _generate_port_commands(self, want_ports, have_ports):
        wantd = self._index_by_id(want_ports)
        haved = self._index_by_id(have_ports)

        if self.state == "merged":
            for key, have in iteritems(haved):
                merged = deepcopy(have)
                merged.update(wantd.get(key, {}))
                wantd[key] = merged

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for key, have in iteritems(haved):
                if key not in wantd:
                    self._delete_port(have)

        for key, want in iteritems(wantd):
            self._compare_port(want, haved.get(key, {}))

    def _generate_group_commands(self, want_groups, have_groups):
        wantd = self._index_by_id(want_groups)
        haved = self._index_by_id(have_groups)

        if self.state == "merged":
            for key, have in iteritems(haved):
                merged = deepcopy(have)
                if key in wantd:
                    merged.update(wantd[key])
                    merged["ports"] = sorted(set(have.get("ports", [])) | set(wantd[key].get("ports", [])))
                wantd[key] = merged

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for key, have in iteritems(haved):
                if key not in wantd:
                    self._delete_group(have)

        for key, want in iteritems(wantd):
            self._compare_group(want, haved.get(key, {}))

    def _compare_port(self, want, have):
        port_id = want["id"]
        for field, command in [
            ("passive_lacp", "passive-lacp"),
            ("short_timeout", "short-timeout"),
        ]:
            if field in want and want.get(field) != have.get(field):
                prefix = "" if want[field] else "no "
                self.commands.append("configure link-agg port {0} {1}{2}".format(port_id, prefix, command))
            elif field not in want and have.get(field) is not None and self.state in ["replaced", "overridden"]:
                self.commands.append("configure link-agg port {0} no {1}".format(port_id, command))

        if want.get("actor_port_prio") != have.get("actor_port_prio"):
            if want.get("actor_port_prio") is not None:
                self.commands.append(
                    "configure link-agg port {0} actor-port-prio {1}".format(
                        port_id, want["actor_port_prio"]
                    )
                )
            elif have.get("actor_port_prio") is not None:
                self.commands.append("configure link-agg port {0} no actor-port-prio".format(port_id))

    def _delete_port(self, have):
        port_id = have["id"]
        if have.get("passive_lacp") is not None:
            self.commands.append("configure link-agg port {0} no passive-lacp".format(port_id))
        if have.get("short_timeout") is not None:
            self.commands.append("configure link-agg port {0} no short-timeout".format(port_id))
        if have.get("actor_port_prio") is not None:
            self.commands.append("configure link-agg port {0} no actor-port-prio".format(port_id))

    def _compare_group(self, want, have):
        group_id = want["id"]
        for field in self.GROUP_FIELDS:
            if field in want and want.get(field) != have.get(field):
                self.commands.append(
                    "configure link-agg group {0} {1} {2}".format(
                        group_id, field.replace("_", "-"), want[field]
                    )
                )
            elif field not in want and have.get(field) is not None and self.state in ["replaced", "overridden"]:
                self._delete_group_field(group_id, field)

        want_ports = set(want.get("ports", []))
        have_ports = set(have.get("ports", []))
        if self.state == "merged":
            remove_ports = set()
        else:
            remove_ports = have_ports - want_ports
        add_ports = want_ports - have_ports

        for port in sorted(remove_ports):
            self.commands.append("configure link-agg group {0} no port {1}".format(group_id, port))
        for port in sorted(add_ports):
            self.commands.append("configure link-agg group {0} port {1}".format(group_id, port))

    def _delete_group(self, have):
        group_id = have["id"]
        for port in sorted(have.get("ports", [])):
            self.commands.append("configure link-agg group {0} no port {1}".format(group_id, port))
        for field in self.GROUP_FIELDS:
            self._delete_group_field(group_id, field, have)

    def _delete_group_field(self, group_id, field, have=None):
        have = have or {}
        if have and have.get(field) is None:
            return
        if field in ["max_active_port", "swo_threshold", "priority"]:
            self.commands.append("configure link-agg group {0} no {1}".format(group_id, field.replace("_", "-")))

    def _index_by_id(self, data):
        return {entry["id"]: entry for entry in data or [] if entry.get("id")}
