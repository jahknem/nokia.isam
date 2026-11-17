# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_error config file.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.error import (
    ErrorTemplate,
)


class Error(ResourceModule):
    """The isam_error config class (settings block ``configure error``).

    Nothing can be removed; ``deleted`` resets the attributes to the device
    defaults (``no <attribute>``), ``overridden`` behaves like ``replaced``.
    """

    def __init__(self, module):
        super(Error, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="error",
            tmplt=ErrorTemplate(),
        )

    def execute_module(self):
        """Execute the module."""
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        self.commands.extend(ErrorTemplate.commands(self.state, self.want, self.have))
