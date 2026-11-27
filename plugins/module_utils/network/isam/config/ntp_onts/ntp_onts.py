#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_ntp_onts config file.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    covers_entry,
    is_masked_secret,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ntp_onts import (
    Ntp_ontsTemplate,
)


class Ntp_onts(IsamResourceModule):
    """
    The isam_ntp_onts config class
    """

    def __init__(self, module):
        super(Ntp_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="ntp_onts",
            tmplt=Ntp_ontsTemplate(),
        )
        self.parsers = [
            "ntp_ont.client_state",
            "ntp_ont.config_mode",
            "ntp_ont.server1_ip_addr",
            "ntp_ont.server2_ip_addr",
            "ntp_ont.server3_ip_addr",
            "ntp_ont.oper_mode",
            "ntp_ont.key_identifier",
            "ntp_ont.key",
        ]

    def generate_commands(self):
        """Generate configuration commands to send based on want, have and state."""
        wantd = self._index_by_ont_id(self.want)
        haved = self._index_by_ont_id(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            # The NTP ONT entry exists as long as its ONT, and "configure ntp no ont"
            # is accepted but changes nothing (lab DS-LIN-TEST-01 2026-11-27: present
            # before any write; after "no ont" still present with client-state on).
            # Deleting resets the named attributes, every set one for a whole entry.
            for k, have in iteritems(haved):
                if wantd and k not in wantd:
                    continue
                want = wantd.get(k, {})
                if covers_entry(want, have, ("ont_id",)):
                    self._compare(want={}, have=have)
                else:
                    named = {key: value for key, value in iteritems(have) if key == "ont_id" or want.get(key) is not None}
                    self._compare(want={}, have=named)
            return

        if self.state == "overridden":
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            have = haved.pop(k, {})
            if not have:
                # The object exists on its own: create it even without attributes.
                self.addcmd(want, "ntp_ont")
            self._compare(want=want, have=have)

    def _compare(self, want, have):
        if is_masked_secret(want.get("key")):
            # Shown masked by the device; a masked value is not the key.
            want = dict(want, key=have.get("key"))
        self.compare(parsers=self.parsers, want=want, have=have)

    def _index_by_ont_id(self, data):
        indexed = {}
        for entry in data or []:
            ont_id = entry.get("ont_id")
            if ont_id:
                indexed[ont_id] = entry
        return indexed
