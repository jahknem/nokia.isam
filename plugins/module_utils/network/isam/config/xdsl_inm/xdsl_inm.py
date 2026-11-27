# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_xdsl_inm config file.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import deleted_targets
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import (
    ATTRS,
    SIDES,
    Xdsl_inmTemplate,
)

_ATTRS = tuple(attr for attr, _cli in ATTRS)


class Xdsl_inm(IsamResourceModule):
    """The isam_xdsl_inm config class.

    A sensor exists for every xDSL line and cannot be removed; its attributes are
    set or reset (``no <attribute>``) in place. ``deleted`` and ``overridden``
    therefore reset attributes instead of removing sensors.
    """

    # Detail output packs all attributes of one sensor on one line.
    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure xdsl imp-noise-sensor (?:near-end|far-end) \S+) (?P<suffix>.+)$",
    )

    def __init__(self, module):
        super(Xdsl_inm, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="xdsl_inm",
            tmplt=Xdsl_inmTemplate(),
        )

    @staticmethod
    def _index(entries):
        return dict((entry["name"], entry) for entry in entries or [] if entry.get("name"))

    def _set(self, side, entry, attr):
        self.commands.append(Xdsl_inmTemplate.render_attr(side, entry, attr))

    def _reset(self, side, name, attr):
        self.commands.append(Xdsl_inmTemplate.render_attr(side, {"name": name}, attr))

    def _reset_all(self, side, have):
        for attr in _ATTRS:
            if have.get(attr) is not None:
                self._reset(side, have["name"], attr)

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        want = self.want or {}
        have = self.have or {}
        for side, _cli in SIDES:
            wantd = self._index(want.get(side))
            haved = self._index(have.get(side))

            if self.state == "deleted":
                # config names sensors: reset those; no config at all: reset every sensor.
                if want and side not in want:
                    continue
                for target, entry in deleted_targets(wantd, haved, ("name",)):
                    for attr in _ATTRS:
                        if entry.get(attr) is not None and attr not in target:
                            self._reset(side, entry["name"], attr)
                continue

            if self.state == "overridden" and side in want:
                # Only a side the request names is overridden (docs/development-style.md).
                for name, entry in iteritems(haved):
                    if name not in wantd:
                        self._reset_all(side, entry)

            for name, entry in iteritems(wantd):
                current = haved.get(name, {})
                for attr in _ATTRS:
                    value = entry.get(attr)
                    if value is not None:
                        if value != current.get(attr):
                            self._set(side, entry, attr)
                    elif self.state in ("replaced", "overridden") and current.get(attr) is not None:
                        self._reset(side, name, attr)
