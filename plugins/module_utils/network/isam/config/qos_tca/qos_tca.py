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
# Device defaults: every queue exists and prints 'no tca-enable no load-thresh ...'
# when unset (live captures r6.2.04m-card6-*), so a value equal to its default is
# the same as unset when comparing.
_DEFAULTS = {"tca_enable": False}


def _non_default(entry):
    """The entry's attributes that differ from the device default."""
    return dict((attr, entry.get(attr)) for attr in _ATTRS
                if entry.get(attr) is not None and entry.get(attr) != _DEFAULTS.get(attr))


class Qos_tca(IsamResourceModule):
    """The isam_qos_tca config class.

    A queue's TCA attributes are set/reset in place; queues are not individually
    removable on the device, so deleted/overridden reset their attributes.
    deleted with only a queue's identity resets every non-default attribute; named
    attributes reset only themselves.
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

    def _reset_all(self, entry, attrs=_ATTRS):
        current = _non_default(entry)
        for attr in attrs:
            if attr in current:
                self._reset(entry, attr)

    def generate_commands(self):
        wantd = self._index(self.want)
        haved = self._index(self.have)

        if self.state == "deleted":
            for key, have in iteritems(haved):
                if wantd and key not in wantd:
                    continue
                named = [attr for attr in _ATTRS if (wantd.get(key) or {}).get(attr) is not None]
                self._reset_all(have, named or _ATTRS)
            return

        if self.state == "overridden":
            for key, have in iteritems(haved):
                if key not in wantd:
                    self._reset_all(have)

        for key, want in iteritems(wantd):
            have = _non_default(haved.get(key, {}))
            for attr in _ATTRS:
                wv = want.get(attr)
                hv = have.get(attr)
                if wv is not None:
                    # rendered has no device: an explicit default is rendered as given
                    if wv != hv and (self.state == "rendered" or wv != _DEFAULTS.get(attr) or hv is not None):
                        self._set(want, attr)
                elif self.state in ("replaced", "overridden") and hv is not None:
                    self._reset(want, attr)
