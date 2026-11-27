# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ani_onts import (
    Ani_ontsTemplate,
)


class Ani_onts(IsamResourceModule):
    """The isam_ani_onts config class."""

    def __init__(self, module):
        super(Ani_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="ani_onts",
            tmplt=Ani_ontsTemplate(),
        )
        self.parsers = [
            "tca_thresh",
        ]

    def generate_commands(self):
        wantd = {entry["ont_idx"]: entry for entry in self.want or []}
        haved = {entry["ont_idx"]: entry for entry in self.have or []}

        if self.state == "merged":
            for key, have in iteritems(haved):
                if key not in wantd:
                    wantd[key] = have
                else:
                    wantd[key] = dict(have, **wantd[key])

        if self.state == "deleted":
            # The entry belongs to the ONT: it exists from the ONT's creation to its
            # removal, and "no tca-thresh" only resets it (lab DS-LIN-TEST-01
            # 2026-11-27: present before any write, still present after
            # "no tca-thresh" with every threshold at its default). Deleting resets
            # the named thresholds (all of them for an identity-only entry).
            for key, have in iteritems(haved):
                if key in wantd or not wantd:
                    want = wantd.get(key) or {}
                    named = [field for field, _cli in self.THRESHOLDS if want.get(field) is not None]
                    self._reset(have, named or [field for field, _cli in self.THRESHOLDS])
            return

        if self.state == "overridden":
            for key, have in iteritems(haved):
                if key not in wantd:
                    self._reset(have, [field for field, _cli in self.THRESHOLDS])

        for key, want in iteritems(wantd):
            self._compare_entry(want, haved.get(key, {}))

    def _reset(self, have, fields):
        """'no <attr>' for every listed threshold the entry has set; nothing if none is."""
        parts = ["no %s" % cli for field, cli in self.THRESHOLDS if field in fields and have.get(field) is not None]
        if parts:
            self.commands.append(" ".join(["configure ani ont tca-thresh %s" % have["ont_idx"]] + parts))

    # The thresholds of one tca-thresh entry (the parser covers the whole line, so
    # the base compare, keyed on tca_thresh, never saw a changed threshold: lab
    # DS-LIN-TEST-01 2026-11-27, merged lower_optical_th on an existing entry sent
    # nothing). "no <attr>" is the device's own form for the default (detail read).
    THRESHOLDS = (("lower_optical_th", "lower-optical-th"), ("upper_optical_th", "upper-optical-th"),
                  ("rssi_profile", "rssi-profile"))

    @staticmethod
    def _same(want, have):
        try:
            return float(want) == float(have)
        except (TypeError, ValueError):
            return str(want) == str(have)

    def _compare_entry(self, want, have):
        ont = want["ont_idx"]
        if want.get("tca_thresh") is False:
            # The entry cannot be removed apart from its ONT: false resets it.
            if have:
                self._reset(have, [field for field, _cli in self.THRESHOLDS])
            return
        parts = []
        for field, cli in self.THRESHOLDS:
            wanted, current = want.get(field), have.get(field)
            if wanted is not None and (current is None or not self._same(wanted, current)):
                parts.append("%s %s" % (cli, wanted))
            elif wanted is None and current is not None and self.state in ("replaced", "overridden"):
                parts.append("no %s" % cli)
        if parts or not have:
            self.commands.append(" ".join(["configure ani ont tca-thresh %s" % ont] + parts))
