# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_nat config file.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.nat import (
    NatTemplate,
)


class Nat(IsamResourceModule):
    """The isam_nat config class (settings block ``configure nat``).

    Nothing can be removed; ``deleted`` resets the attributes to the device
    defaults (``no <attribute>``), ``overridden`` behaves like ``replaced``.
    """

    def __init__(self, module):
        super(Nat, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="nat",
            tmplt=NatTemplate(),
        )

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        self.commands.extend(NatTemplate.commands(self.state, self.want, self.have))
