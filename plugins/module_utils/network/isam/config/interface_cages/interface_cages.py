#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_interface_cages config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_cages import (
    InterfaceCagesTemplate,
)


class InterfaceCages(ResourceModule):
    """
    The isam_interface_cages config class
    """

    def __init__(self, module):
        super(InterfaceCages, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="interface_cages",
            tmplt=InterfaceCagesTemplate(),
        )
        self.parsers = [
            "cage.id",
            "cage.description",
            "cage.apply_qos",
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

    def addcmd(self, data, tmplt, negate=False):
        parser = self._tmplt.get_parser(tmplt)
        if negate and parser.get("remval"):
            remval = parser["remval"]
            if callable(remval):
                command = remval(data)
            else:
                command = self._tmplt._template(value=remval, variables=data, fail_on_undefined=False)
            if command:
                if isinstance(command, list):
                    self.commands.extend(command)
                else:
                    self.commands.append(command)
            return
        super(InterfaceCages, self).addcmd(data, tmplt, negate)

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
           populates the list of commands to be run by comparing
           the `want` and `have` data with the `parsers` defined
           for the InterfaceCages network resource.
        """
        self.compare(parsers=self.parsers, want=want, have=have)
