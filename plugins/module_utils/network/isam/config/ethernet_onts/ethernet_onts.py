#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_ethernet_onts config file.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_onts import (
    ETHERNET_ONT_SUBNODE_FLAGS,
    ETHERNET_ONT_SUBNODE_VALUES,
    Ethernet_ontsTemplate,
)

# (path, field, device default) of the sub-node attributes; a requested default equals an absent value.
_SUBNODE_DEFAULTS = tuple(
    (path, field, default) for path, _node, field, _cli, _value_re, default in ETHERNET_ONT_SUBNODE_VALUES
) + tuple((path, field, False) for path, _node, field, _cli in ETHERNET_ONT_SUBNODE_FLAGS)


class Ethernet_onts(ResourceModule):
    """
    The isam_ethernet_onts config class
    """

    # The UNI attributes compact into one command; each sub-node (phy, l2, l2 pm-collect-ext,
    # cfm) is its own command scope and never joins the UNI command.
    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure ethernet ont \S+) (?P<suffix>(?!(?:phy|l2|cfm)(?:\s|$)).+)$",
        r"^(?P<scope>configure ethernet ont \S+ phy) (?P<suffix>.+)$",
        r"^(?P<scope>configure ethernet ont \S+ l2 pm-collect-ext) (?P<suffix>.+)$",
        r"^(?P<scope>configure ethernet ont \S+ l2) (?P<suffix>(?!pm-collect-ext(?:\s|$)).+)$",
        r"^(?P<scope>configure ethernet ont \S+ cfm) (?P<suffix>.+)$",
    )

    def __init__(self, module):
        super(Ethernet_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="ethernet_onts",
            tmplt=Ethernet_ontsTemplate(),
        )
        self.parsers = [
            "ont.cust_info",
            "ont.auto_detect",
            "ont.power_control",
            "ont.pse_class",
            "ont.pse_pw_priority",
            "ont.pwr_override",
            "ont.lpt_mode",
            "ont.admin_state",
        ]
        self.parsers.extend("ont." + path + "." + field for path, field, _default in _SUBNODE_DEFAULTS)

    def execute_module(self):
        """Execute the module."""
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """Generate configuration commands to send based on want, have and state."""
        wantd = self._index_by_uni_idx(self.want)
        haved = self._index_by_uni_idx(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            self._delete(wantd, haved)
            return

        if self.state == "overridden":
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _delete(self, wantd, haved):
        """Ethernet ONTs have no remove command: their settings are reset. Without
        config every UNI, otherwise the named UNIs: all settings for an identity
        alone, else only the named ones (the others are kept)."""
        for uni_idx, have in iteritems(haved):
            if wantd and uni_idx not in wantd:
                continue
            named = set(key for key, value in iteritems(wantd.get(uni_idx) or {})
                        if key not in ("uni_idx", "name") and value is not None)
            keep = dict((key, value) for key, value in iteritems(have) if named and key not in named)
            self._compare(want=keep, have=have)

    def _compare(self, want, have):
        self.compare(parsers=self.parsers, want=self._strip_subnode_defaults(want),
                     have=self._strip_subnode_defaults(have))

    @staticmethod
    def _strip_subnode_defaults(entry):
        """Sub-node attributes at their device default equal absent ones (detail prints 'no <attr>')."""
        if not entry or not any(entry.get(key) for key in ("phy", "l2", "cfm")):
            return entry
        entry = deepcopy(entry)
        for path, field, default in _SUBNODE_DEFAULTS:
            node = entry
            for key in path.split("."):
                node = node.get(key) if isinstance(node, dict) else None
            if isinstance(node, dict) and field in node and (node[field] is None or node[field] == default):
                node.pop(field)
        return entry

    def _index_by_uni_idx(self, data):
        indexed = {}
        for entry in data or []:
            uni_idx = entry.get("uni_idx") or entry.get("name")
            if uni_idx:
                entry["uni_idx"] = uni_idx
                indexed[uni_idx] = entry
        return indexed
