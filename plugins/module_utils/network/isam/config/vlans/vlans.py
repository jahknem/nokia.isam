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

from ansible.module_utils.six import iteritems
from ansible.module_utils.six.moves import shlex_quote
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VlansTemplate,
)


class Vlans(ResourceModule):
    """
    The isam_vlans config class
    """

    def __init__(self, module):
        super(Vlans, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="vlans",
            tmplt=VlansTemplate(),
        )
        self.parsers = [
            "id",
            "id_with_mode",
            "name",
            "mode",
            "sntp-proxy",
            "priority",
            "vmac-not-in-opt61",
            "new-broadcast",
            "protocol-filter",
            "pppoe-relay-tag",
            "drly-srv-usr-side",
            "new-secure-fwd",
            "aging-time",
            "l2cp-transparent",
            "in-qos-prof-name",
            "ipv4-mcast-ctrl",
            "ipv6-mcast-ctrl",
            "mac-mcast-ctrl",
            "dis-proto-rip",
            "proto-ntp",
            "dis-ip-antispoof",
            "unknown-unicast",
            "pt2ptgem-flooding",
            "mac-movement-ctrl",
            "cvlan4095passthru",
            "arp-snooping",
            "arp-polling",
            "arp-polling-ip",
            "mac-unauth",
            "dhcp-opt82-ext",
            "dhcp-opt82-nni",
            "dhcp-opt82-uplink",
            "circuit-id-dhcp",
            "remote-id-dhcp",
            "relay-id-dhcp",
            "linerates",
            "l2-encaps",
            "vlanaware",
            "circuit-id-pppoe",
            "remote-id-pppoe",
            "dhcpv6-identifiers",
            "dhcpv6-flags",
            "enterprise-number",
            "icmpv6-sec-fltr",
            "vmac-translation",
            "vmac-dnstr-filter",
        ]

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        if self.state == "rendered":
            rendered = self._render_vlan_config(
                self._module.params.get("config") or self.want
            )
            self.commands = rendered
            self.result["rendered"] = rendered
            return

        if self.state in ("merged", "replaced", "overridden", "deleted"):
            commands = self._generate_vlan_state_commands()
            self.commands = commands
            self.result["commands"] = commands
            return

        wantd = {entry['id']: entry for entry in self.want}
        haved = {entry['id']: entry for entry in self.have}

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state == "deleted":
            haved = {
                k: v for k, v in iteritems(haved) if k in wantd or not wantd
            }
            wantd = {}

        # remove superfluous config for overridden and deleted
        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
           populates the list of commands to be run by comparing
           the `want` and `have` data with the `parsers` defined
           for the Vlans network resource.
        """
        self.compare(parsers=self.parsers, want=want, have=have)

    def _render_vlan_config(self, config):
        commands = []
        for vlan in config or []:
            prefix = "configure vlan id {0}".format(vlan["id"])
            for field in self.parsers:
                if field in ("id", "id_with_mode") or vlan.get(field) is None:
                    continue
                value = vlan[field]
                if field == "name":
                    value = shlex_quote(str(value))
                if value is False:
                    commands.append("{0} no {1}".format(prefix, field))
                elif value is True:
                    commands.append("{0} {1}".format(prefix, field))
                else:
                    commands.append("{0} {1} {2}".format(prefix, field, value))
        return commands

    def _generate_vlan_state_commands(self):
        want = {str(item["id"]): item for item in self.want or []}
        have = {str(item["id"]): item for item in self.have or []}
        commands = []

        if self.state == "deleted":
            targets = want.keys() if want else have.keys()
            return ["configure vlan no id {0}".format(vlan_id) for vlan_id in targets]

        if self.state == "overridden":
            for vlan_id in have:
                if vlan_id not in want:
                    commands.append("configure vlan no id {0}".format(vlan_id))

        for vlan_id, desired in want.items():
            current = have.get(vlan_id, {})
            if self.state == "replaced":
                for field in current:
                    if field not in desired and field != "id":
                        commands.append("configure vlan id {0} no {1}".format(vlan_id, field))
            elif self.state == "merged":
                desired = dict(current, **desired)

            for field, value in desired.items():
                if field == "id" or value is None:
                    continue
                if value == current.get(field):
                    continue
                if value is False:
                    commands.append("configure vlan id {0} no {1}".format(vlan_id, field))
                elif value is True:
                    commands.append("configure vlan id {0} {1}".format(vlan_id, field))
                else:
                    rendered = shlex_quote(str(value)) if field == "name" else value
                    commands.append("configure vlan id {0} {1} {2}".format(vlan_id, field, rendered))
        return commands
