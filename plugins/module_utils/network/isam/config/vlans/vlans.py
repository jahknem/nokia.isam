#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_vlans config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import covers_entry, deleted_targets
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VLAN_ATTRS,
    VLAN_DEFAULTS,
    VLAN_LINE_KEYWORDS,
    VlansTemplate,
)

SET_ONLY = tuple(option for option, _cli, kind, _default in VLAN_ATTRS if kind == "set_only")


def _without_defaults(entry):
    """A device default equals an unset value (flags: off)."""
    return dict((key, value) for key, value in entry.items()
                if value is not None and value is not False and VLAN_DEFAULTS.get(key) != value)


class Vlans(IsamResourceModule):
    """
    The isam_vlans config class
    """

    # one command per printed line of the device (two per VLAN), from the attribute table
    COMPACT_COMMAND_SCOPES = tuple(
        (r"^(?P<scope>configure vlan id \S+) (?P<suffix>(?:no )?(?:%s)(?:\s.*)?)$" % "|".join(re.escape(kw) for kw in keywords),
         "vlan-line-%d" % number)
        for number, keywords in enumerate(VLAN_LINE_KEYWORDS, 1)
    )

    def __init__(self, module):
        super(Vlans, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="vlans",
            tmplt=VlansTemplate(),
        )
        self.parsers = [option for option, _cli, _kind, _default in VLAN_ATTRS]

    def generate_commands(self):
        """Generate the commands that bring the VLANs from have to want."""
        rendering = self.state == "rendered"
        wantd = dict((str(entry["id"]), entry if rendering else _without_defaults(entry)) for entry in self.want or [])
        haved = dict((str(entry["id"]), _without_defaults(entry)) for entry in self.have or [])

        if self.state == "deleted":
            # an identity (or a full entry) removes the VLAN; named settings reset only
            # themselves (naming "name" must not delete the VLAN); absent VLANs are skipped
            for target, have in deleted_targets(wantd, haved, ("id",)):
                if covers_entry(wantd.get(str(have["id"]), {}), have, ("id",)):
                    self.addcmd(have, "id", True)
                else:
                    self.compare(parsers=self.parsers, want=target, have=have)
            return

        if self.state == "overridden":
            for vlan_id, have in haved.items():
                if vlan_id not in wantd:
                    self.addcmd(have, "id", True)

        for vlan_id, want in wantd.items():
            have = haved.get(vlan_id, {})
            if not have and not rendering and want.get("mode") is None:
                # mode is a mandatory parameter of a new VLAN (CLI guide)
                self._module.fail_json(msg="vlan %s does not exist; mode is required to create it" % vlan_id)
            if self.state == "merged":
                want = dict(have, **want)
            else:
                # attributes without removal form (mode) stay when not named
                want = dict(dict((k, have[k]) for k in SET_ONLY if k in have), **want)
            before = len(self.commands)
            self.compare(parsers=self.parsers, want=want, have=have)
            if not have and not rendering and len(self.commands) == before:
                self.addcmd(want, "id", False)  # a new VLAN with only default settings
