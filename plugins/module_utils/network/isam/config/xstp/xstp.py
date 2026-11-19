# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xstp import (
    XSTP_GENERAL_FIELDS,
    XSTP_PORT_FIELDS,
    XSTP_PORT_FLAGS,
    XstpTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import deleted_targets, requested_sections


def _without_default(value, default):
    """A value at its device default equals an absent one (detail mode prints it as 'no <attr>')."""
    return None if value is None or value == default else value


class Xstp(IsamResourceModule):
    """The isam_xstp config class."""

    def __init__(self, module):
        super(Xstp, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xstp",
            tmplt=XstpTemplate(),
        )
        self.parsers = [
            "general.enable_stp",
            "general.region_name",
            "ports.path_cost",
        ]
        self.parsers.extend("general." + field for field in XSTP_GENERAL_FIELDS)
        self.parsers.extend("ports." + field for field in XSTP_PORT_FIELDS)
        self.parsers.extend("ports." + field for field in XSTP_PORT_FLAGS)

    def generate_commands(self):
        want = self._normalize(self.want)
        have = self._normalize(self.have)

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            # with config only the named sections and ports (deleting a port must not
            # disable STP globally)
            requested = requested_sections(self._module)
            if not requested or "general" in requested:
                self._compare_general({}, have.get("general", {}))
            if not requested or "ports" in requested:
                self._compare_ports(want.get("ports", []), have.get("ports", []))
            return

        self._compare_general(want.get("general", {}), have.get("general", {}))
        self._compare_ports(want.get("ports", []), have.get("ports", []))

    def _compare_general(self, want, have):
        if self.state in ["overridden", "replaced", "deleted"]:
            if "enable_stp" not in want and have.get("enable_stp") is True:
                self.addcmd({"general": {"enable_stp": False}}, "general.enable_stp")

        if "enable_stp" in want and want.get("enable_stp") != have.get("enable_stp"):
            self.addcmd({"general": {"enable_stp": want.get("enable_stp")}}, "general.enable_stp")

        if "region_name" in want and want.get("region_name") != have.get("region_name"):
            self.addcmd({"general": {"region_name": want.get("region_name")}}, "general.region_name")

        # Attributes with a 'no <attr>' reset: merged keeps unmentioned values (want is merged
        # with have), replaced/overridden/deleted reset them to the device default.
        for field, spec in XSTP_GENERAL_FIELDS.items():
            wanted = _without_default(want.get(field), spec[1])
            current = _without_default(have.get(field), spec[1])
            if wanted == current:
                continue
            if wanted is None:
                self.addcmd({"general": {field: current}}, "general." + field, True)
            else:
                self.addcmd({"general": {field: wanted}}, "general." + field)

    def _compare_ports(self, want, have):
        wantd = self._index_ports(want)
        haved = self._index_ports(have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            for target, have_entry in deleted_targets(wantd, haved, ("port",)):
                self._compare_port_resettable(target, have_entry)
            return

        if self.state == "overridden":
            # path-cost has no documented no-form and stays unchanged on unmentioned ports;
            # the attributes with a 'no <attr>' form are reset there.
            for port, have_entry in iteritems(haved):
                if port not in wantd:
                    self._compare_port_resettable({"port": port}, have_entry)
            haved = {k: v for k, v in iteritems(haved) if k in wantd}

        for port, want_entry in iteritems(wantd):
            have_entry = haved.get(port, {})
            if "path_cost" in want_entry and want_entry.get("path_cost") != have_entry.get("path_cost"):
                self.addcmd(want_entry, "ports.path_cost")
            self._compare_port_resettable(want_entry, have_entry)

    def _compare_port_resettable(self, want, have):
        port = want.get("port") or have.get("port")
        defaults = dict((field, spec[1]) for field, spec in XSTP_PORT_FIELDS.items())
        defaults.update((field, False) for field in XSTP_PORT_FLAGS)
        for field, default in defaults.items():
            if self.state == "rendered":
                # rendered renders what is given, an explicit default ("no <attr>") included
                if want.get(field) is not None:
                    self.addcmd({"port": port, field: want[field]}, "ports." + field, want[field] is False)
                continue
            wanted = _without_default(want.get(field), default)
            current = _without_default(have.get(field), default)
            if wanted == current:
                continue
            if wanted is None:
                self.addcmd({"port": port, field: current}, "ports." + field, True)
            else:
                self.addcmd({"port": port, field: wanted}, "ports." + field)

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        normalized["general"] = self._normalize_general(normalized.get("general") or {})
        normalized["ports"] = list(self._index_ports(normalized.get("ports") or []).values())
        return normalized

    def _normalize_general(self, general):
        normalized = dict(general)
        if "enable-stp" in normalized and "enable_stp" not in normalized:
            normalized["enable_stp"] = normalized.pop("enable-stp")
        if "region-name" in normalized and "region_name" not in normalized:
            normalized["region_name"] = normalized.pop("region-name")
        return normalized

    def _index_ports(self, ports):
        indexed = {}
        for entry in ports or []:
            normalized = dict(entry)
            if "id" in normalized and "port" not in normalized:
                normalized["port"] = normalized.pop("id")
            if "name" in normalized and "port" not in normalized:
                normalized["port"] = normalized.pop("name")
            if "path-cost" in normalized and "path_cost" not in normalized:
                normalized["path_cost"] = normalized.pop("path-cost")
            port = normalized.get("port")
            if port:
                indexed[port] = normalized
        return indexed
