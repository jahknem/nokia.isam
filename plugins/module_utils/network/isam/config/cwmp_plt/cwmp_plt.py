# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_cwmp_plt config file.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cwmp_plt import (
    Cwmp_pltTemplate,
)


class Cwmp_plt(IsamResourceModule):
    """The isam_cwmp_plt config class (settings block ``configure cwmp plt``).

    Nothing can be removed; ``deleted`` resets the attributes to the device
    defaults (``no <attribute>``), ``overridden`` behaves like ``replaced``.
    """

    def __init__(self, module):
        super(Cwmp_plt, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="cwmp_plt",
            tmplt=Cwmp_pltTemplate(),
        )

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        self.commands.extend(Cwmp_pltTemplate.commands(self.state, self.want, self.have))
