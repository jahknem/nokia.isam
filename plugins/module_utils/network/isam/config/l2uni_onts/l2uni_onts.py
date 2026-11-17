# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The isam_l2uni_onts config class.

``UniPmConfigMixin`` holds the state logic shared with isam_uni_onts: per UNI and
CLI scope (node or sub-node) the changed fields are packed into one command, as
the CLI syntax allows (``configure l2uni ont performance-monitor <uni> [ no
pm-collect | pm-collect <v> ] [ no pm-collect-64bit | ... ]``) and the device
shows. The nodes exist with their UNI, so nothing is created or removed:
removal resets fields to their CLI default with ``no <attr>``.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2uni_onts import (
    IDENTITY,
    L2uni_ontsTemplate,
)

# field name -> (allowed ranges); values outside are rejected before rendering.
_INT_RANGES = {
    "p_bits": ((0, 7), (255, 255)),
    "vlan_id": ((0, 4092),),
    "dropped_frames_up": ((0, 4294967295),),
    "dropped_frames_dn": ((0, 4294967295),),
}


class UniPmConfigMixin(object):
    """State logic for UniPmTemplate resources. Subclasses set TEMPLATE and _sections()."""

    TEMPLATE = None

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def _sections(self, data):
        raise NotImplementedError

    @staticmethod
    def _index(entries):
        return dict((e[IDENTITY], e) for e in entries or [] if isinstance(e, dict) and e.get(IDENTITY))

    def _check_ranges(self, node, entry):
        for sub, dummy, fields in node.scopes():
            values = (entry.get(sub) or {}) if sub else entry
            for field in fields:
                value = values.get(field.name)
                ranges = _INT_RANGES.get(field.name)
                if value is None or not ranges:
                    continue
                if not any(low <= value <= high for low, high in ranges):
                    self._module.fail_json(msg="%s %s: %s=%s is out of range %s" % (
                        node.section, entry[IDENTITY], field.name, value,
                        ", ".join("%d-%d" % r if r[0] != r[1] else "%d" % r[0] for r in ranges)))

    def _emit(self, node, uni, cli, parts):
        if parts:
            self.commands.append(node.scope_command(uni, cli) + " " + " ".join(parts))

    def _reset(self, node, have, want=None):
        """Reset the present fields of an entry; with want naming fields, only those."""
        want = want or {}
        named = any(
            (want.get(sub) is not None) if sub else
            any(want.get(f.name) is not None for f in fields)
            for sub, dummy, fields in node.scopes()
        )
        for sub, cli, fields in node.scopes():
            hvals = (have.get(sub) or {}) if sub else have
            if sub:
                wsub = want.get(sub)
                wvals = wsub or {}
                whole = not named or wsub == {} or (wsub is not None and not any(v is not None for v in wsub.values()))
            else:
                wvals, whole = want, not named
            parts = [f.render(None) for f in fields
                     if hvals.get(f.name) is not None and (whole or wvals.get(f.name) is not None)]
            self._emit(node, have[IDENTITY], cli, parts)

    def _update(self, node, want, have):
        render_all = self.state == "rendered"
        replace = self.state in ("replaced", "overridden")
        for sub, cli, fields in node.scopes():
            wvals = (want.get(sub) or {}) if sub else want
            hvals = (have.get(sub) or {}) if sub else have
            parts = []
            for field in fields:
                wv, hv = wvals.get(field.name), hvals.get(field.name)
                if wv is not None:
                    current = hv if hv is not None else field.default
                    if render_all or wv != current:
                        parts.append(field.render(wv))
                elif replace and hv is not None:
                    parts.append(field.render(None))
            self._emit(node, want[IDENTITY], cli, parts)

    def generate_commands(self):
        wants = self._sections(self.want)
        haves = self._sections(self.have) if self.state != "rendered" else {}
        for node in self.TEMPLATE.NODES:
            wantd = self._index(wants.get(node.section))
            haved = self._index(haves.get(node.section))
            for want in wantd.values():
                self._check_ranges(node, want)

            if self.state == "deleted":
                for uni, have in haved.items():
                    if wantd and uni not in wantd:
                        continue
                    if not wantd and wants and self._named_any(wants):
                        # config names instances only in other sections
                        continue
                    self._reset(node, have, wantd.get(uni))
                continue

            if self.state == "overridden":
                for uni, have in haved.items():
                    if uni not in wantd:
                        self._reset(node, have)

            for uni, want in wantd.items():
                self._update(node, want, haved.get(uni, {}))

    @staticmethod
    def _named_any(sections):
        return any(entries for entries in sections.values())


class L2uni_onts(UniPmConfigMixin, ResourceModule):
    """The isam_l2uni_onts config class."""

    TEMPLATE = L2uni_ontsTemplate

    def __init__(self, module):
        super(L2uni_onts, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="l2uni_onts",
            tmplt=L2uni_ontsTemplate(),
        )

    def _sections(self, data):
        return dict(data or {})
