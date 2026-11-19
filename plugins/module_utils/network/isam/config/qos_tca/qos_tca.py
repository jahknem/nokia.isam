# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_tca import (
    Qos_tcaTemplate,
)

_ATTRS = ("tca_enable", "load_thresh", "dis_frame_th", "qpeak_usage_th")


class Qos_tca(IsamResourceModule):
    """The isam_qos_tca config class.

    A queue's TCA attributes are set/reset in place; queues are not individually
    removable on the device, so deleted/overridden reset their attributes.
    """

    def __init__(self, module):
        super(Qos_tca, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="qos_tca",
            tmplt=Qos_tcaTemplate(),
        )

    def _index(self, data):
        return {(e["name"], e["queue"]): e for e in data or [] if e.get("name") is not None and e.get("queue") is not None}

    def _set(self, entry, attr):
        cmd = Qos_tcaTemplate.render_attr(entry, attr)
        if cmd:
            self.commands.append(cmd)

    def _reset(self, entry, attr):
        blank = {"name": entry["name"], "queue": entry["queue"], attr: (False if attr == "tca_enable" else None)}
        cmd = Qos_tcaTemplate.render_attr(blank, attr)
        if cmd:
            self.commands.append(cmd)

    def generate_commands(self):
        wantd = self._index(self.want)
        haved = self._index(self.have)

        if self.state == "deleted":
            for key, have in iteritems(haved):
                if wantd and key not in wantd:
                    continue
                for attr in _ATTRS:
                    if have.get(attr) is not None:
                        self._reset(have, attr)
            return

        if self.state == "overridden":
            for key, have in iteritems(haved):
                if key not in wantd:
                    for attr in _ATTRS:
                        if have.get(attr) is not None:
                            self._reset(have, attr)

        for key, want in iteritems(wantd):
            have = haved.get(key, {})
            for attr in _ATTRS:
                wv = want.get(attr)
                hv = have.get(attr)
                if wv is not None:
                    if wv != hv:
                        self._set(want, attr)
                elif self.state in ("replaced", "overridden") and hv is not None:
                    self._reset(want, attr)
