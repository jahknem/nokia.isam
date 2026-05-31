# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ani_onts import (
    Ani_ontsTemplate,
)


class Ani_onts(ResourceModule):
    """The isam_ani_onts config class."""

    def __init__(self, module):
        super(Ani_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="ani_onts",
            tmplt=Ani_ontsTemplate(),
        )
        self.parsers = [
            "tca_profile",
            "admin_state",
        ]

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        wantd = {entry["ont_idx"]: entry for entry in self.want or []}
        haved = {entry["ont_idx"]: entry for entry in self.have or []}

        if self.state == "merged":
            for key, have in iteritems(haved):
                if key not in wantd:
                    wantd[key] = have
                else:
                    wantd[key] = dict(have, **wantd[key])

        if self.state == "deleted":
            for key, have in iteritems(haved):
                if key in wantd or not wantd:
                    self.addcmd(have, "ont_idx", negate=True)
            return

        if self.state in ["overridden", "deleted"]:
            for key, have in iteritems(haved):
                if key not in wantd:
                    self.addcmd(have, "ont_idx", negate=True)

        for key, want in iteritems(wantd):
            have = haved.get(key, {})
            self.compare(parsers=self.parsers, want=want, have=have)
