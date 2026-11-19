#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_interfaces config file.
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
    deleted_targets,
    normalize_resource_keys,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)


# Flags whose device default is off. 'false' is printed only by the targeted 'detail'
# comparison read ('no admin-up'); the plain read omits it, so false means unset.
DEFAULT_OFF_FLAGS = ("admin_up", "link_updown_trap")


def _without_defaults(entry, keep=()):
    """Drop detail-only unset values, retaining explicitly requested resets."""
    return dict((k, v) for k, v in entry.items()
                if k in keep or not ((k in DEFAULT_OFF_FLAGS and v is False)
                                     or (k == "severity" and v == "no-value")))


class Interfaces(IsamResourceModule):
    """
    The isam_interfaces config class
    """

    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure interface port \S+) (?P<suffix>.+)$",
    )

    def __init__(self, module):
        super(Interfaces, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="interfaces",
            tmplt=InterfacesTemplate(),
        )
        self.parsers = [
            "admin_up",
            "link_updown_trap",
            "user",
            "severity",
            "port_type",
        ]

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        wantd = self._index_by_id(self.want)
        haved = self._index_by_id(self.have)
        # replaced/overridden must not re-send the defaults the detail read prints; an
        # explicit false is still sent in merged where the device has the flag set, and
        # rendered renders what was asked for.
        haved = dict((k, _without_defaults(v)) for k, v in iteritems(haved))
        if self.state == "deleted":
            # before want's false flags are dropped: "admin_up: false" names the attribute too
            for target, have in deleted_targets(wantd, haved, ("name", "id")):
                self._compare(want=target, have=have)
            return
        for k, v in iteritems(dict(wantd)):
            if self.state == "rendered":
                keep = list(DEFAULT_OFF_FLAGS) + ["severity"]
            elif self.state == "merged":
                keep = [flag for flag in DEFAULT_OFF_FLAGS if haved.get(k, {}).get(flag)]
            else:
                keep = ()
            if haved.get(k, {}).get("severity") is not None:
                keep = list(keep) + ["severity"]
            wantd[k] = _without_defaults(v, keep)

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # remove superfluous config for overridden
        if self.state == "overridden":
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
           populates the list of commands to be run by comparing
           the `want` and `have` data with the `parsers` defined
           for the Interfaces network resource.
        """
        self.compare(parsers=self.parsers, want=want, have=have)

    def _index_by_id(self, data):
        indexed = {}
        for entry in data or []:
            normalized = normalize_resource_keys(entry, aliases=(("id", "name"),))

            key = normalized.get("name") or normalized.get("id")
            if key:
                indexed[key] = normalized
        return indexed
