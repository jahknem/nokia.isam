# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_error config file.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.error import (
    ErrorTemplate,
)


class Error(IsamResourceModule):
    """The isam_error config class (settings block ``configure error``).

    Nothing can be removed; ``deleted`` resets the named attributes (all without config) to the device
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

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        self.commands.extend(ErrorTemplate.commands(self.state, self.want, self.have))
