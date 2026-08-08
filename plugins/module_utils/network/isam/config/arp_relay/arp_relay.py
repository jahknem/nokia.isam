# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from copy import deepcopy

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.arp_relay.arp_relay import Isam_arp_relayFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.arp_relay import Isam_arp_relayTemplate


class Isam_arp_relay(ResourceModule):
    def __init__(self, module):
        super(Isam_arp_relay, self).__init__(
            empty_fact_val=[], facts_module=Isam_arp_relayFacts(module), module=module,
            resource="isam_arp_relay", tmplt=Isam_arp_relayTemplate(),
        )
        self.want = self._by_name(self.want)
        self.have = self._by_name(self.have)

    @staticmethod
    def _by_name(items):
        return {item["name"]: item for item in (items or [])}

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ("parsed", "gathered"):
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        want = dict(self.want)
        have = dict(self.have)
        if self.state == "merged":
            for name, item in have.items():
                want.setdefault(name, item)
        elif self.state == "deleted":
            want = {name: {} for name in (want or have)}
        elif self.state in ("replaced", "overridden"):
            want = dict(want)
            for name in set(have) - set(want):
                self._add_command(have[name], False)

        for name, item in want.items():
            current = have.get(name, {})
            if self.state == "deleted":
                if current:
                    self._add_command(current, False)
            elif item.get("statistics") is not None and item.get("statistics") != current.get("statistics"):
                self._add_command(item, item["statistics"])

    def _add_command(self, item, enabled):
        self.commands.append(
            "configure arp-relay {0}statistics {1}".format("" if enabled else "no ", item["name"])
        )
