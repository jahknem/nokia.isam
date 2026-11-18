# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_xdsl_system config file.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_system import (
    NODES,
    Xdsl_systemTemplate,
)

# Device default of each attribute (what ``no <attribute>`` leaves behind).
_DEFAULTS = {("auto_port_reset", "enable"): False}


class Xdsl_system(IsamResourceModule):
    """The isam_xdsl_system config class (system-wide settings block).

    Nothing here can be removed; ``deleted`` resets the configured attributes
    to the device defaults, ``overridden`` behaves like ``replaced``.
    """

    def __init__(self, module):
        super(Xdsl_system, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xdsl_system",
            tmplt=Xdsl_systemTemplate(),
        )

    def execute_module(self):
        """Execute the module."""
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def _reset(self, node, attr, have_value):
        default = _DEFAULTS.get((node, attr))
        if have_value is not None and have_value != default:
            self.commands.append(Xdsl_systemTemplate.render_attr(node, attr, default))

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        want = self.want or {}
        have = self.have or {}
        for node, _cli, attrs in NODES:
            wnode = want.get(node) or {}
            hnode = have.get(node) or {}
            for attr, _cli_attr, _kind in attrs:
                wv = wnode.get(attr)
                hv = hnode.get(attr)
                if self.state == "deleted":
                    if not want or node in want:
                        self._reset(node, attr, hv)
                elif wv is not None:
                    # Output without detail omits defaults: absent means the default.
                    if wv != (hv if hv is not None else _DEFAULTS.get((node, attr))):
                        self.commands.append(Xdsl_systemTemplate.render_attr(node, attr, wv))
                elif self.state in ("replaced", "overridden"):
                    self._reset(node, attr, hv)
