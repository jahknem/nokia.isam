# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_xdsl_onts config file.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_onts import (
    ATTRS,
    Xdsl_ontsTemplate,
)

_ATTRS = tuple(attr for attr, _cli in ATTRS)


class Xdsl_onts(IsamResourceModule):
    """The isam_xdsl_onts config class.

    The xDSL interface node of an ONT exists with the ONT itself (it is created
    and removed through M(nokia.isam.isam_equipment_onts)); here its attributes
    are only set or reset (``no <attribute>``). ``deleted`` and ``overridden``
    therefore reset attributes instead of removing interfaces.
    """

    def __init__(self, module):
        super(Xdsl_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="xdsl_onts",
            tmplt=Xdsl_ontsTemplate(),
        )

    @staticmethod
    def _index(entries):
        return dict((entry["ont_idx"], entry) for entry in entries or [] if entry.get("ont_idx"))

    def _reset_all(self, have):
        for attr in _ATTRS:
            if have.get(attr) is not None:
                self.commands.append(Xdsl_ontsTemplate.render_attr({"ont_idx": have["ont_idx"]}, attr))

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        wantd = self._index(self.want)
        haved = self._index(self.have)

        if self.state == "deleted":
            for key, have in iteritems(haved):
                if not wantd or key in wantd:
                    self._reset_all(have)
            return

        if self.state == "overridden":
            for key, have in iteritems(haved):
                if key not in wantd:
                    self._reset_all(have)

        for key, want in iteritems(wantd):
            have = haved.get(key, {})
            for attr in _ATTRS:
                value = want.get(attr)
                if value is not None:
                    if value != have.get(attr):
                        self.commands.append(Xdsl_ontsTemplate.render_attr(want, attr))
                elif self.state in ("replaced", "overridden") and have.get(attr) is not None:
                    self.commands.append(Xdsl_ontsTemplate.render_attr({"ont_idx": key}, attr))
