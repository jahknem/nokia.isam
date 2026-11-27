# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_trouble_shooting_pon config file.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    settings_commands,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.trouble_shooting_pon import (
    INTERVAL_ATTRS,
    THRESHOLD_ATTRS,
    Trouble_shooting_ponTemplate,
)


def _by_name(entries):
    result = {}
    for entry in entries or []:
        result[entry["name"]] = dict((key, value) for key, value in entry.items() if value is not None)
    return result


class Trouble_shooting_pon(IsamResourceModule):
    """The isam_trouble_shooting_pon config class.

    ``interfaces`` (extensive counters) are created and removed (``[no] interface``).
    Thresholds exist for every PON port; they are set or reset in place, so
    ``deleted`` and ``overridden`` reset them instead of removing anything.
    """

    # Both thresholds of one PON port in one command (detail output packs them).
    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure trouble-shooting pon statistics threshold interface \S+) (?P<suffix>.+)$",
    )

    def __init__(self, module):
        super(Trouble_shooting_pon, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="trouble_shooting_pon",
            tmplt=Trouble_shooting_ponTemplate(),
        )

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        want = self.want or {}
        have = self.have or {}
        state = self.state
        tmplt = Trouble_shooting_ponTemplate
        whole = state == "overridden" or (state == "deleted" and not want)

        # ---- statistics interfaces (create / remove)
        want_ifs = _by_name(want.get("interfaces"))
        have_ifs = _by_name(have.get("interfaces"))
        if state == "deleted":
            for name in have_ifs:
                if whole or name in want_ifs:
                    self.commands.append(tmplt.render_interface(name, False))
        else:
            if whole or (state == "replaced" and "interfaces" in want):
                for name in have_ifs:
                    if name not in want_ifs:
                        self.commands.append(tmplt.render_interface(name, False))
            for name in want_ifs:
                if name not in have_ifs:
                    self.commands.append(tmplt.render_interface(name))

        # ---- threshold interval (settings attribute)
        wthr = want.get("threshold") or {}
        hthr = have.get("threshold") or {}
        if state == "deleted":
            if whole or wthr.get("interval") is not None:
                self.commands.extend(settings_commands("deleted", {}, hthr, INTERVAL_ATTRS, lambda o, v: tmplt.render_interval(v)))
        elif state == "merged" or (state == "replaced" and "threshold" not in want):
            self.commands.extend(settings_commands("merged", wthr, hthr, INTERVAL_ATTRS, lambda o, v: tmplt.render_interval(v)))
        else:
            self.commands.extend(settings_commands("replaced", wthr, hthr, INTERVAL_ATTRS, lambda o, v: tmplt.render_interval(v)))

        # ---- per-port thresholds (set / reset in place)
        want_th = _by_name(wthr.get("interfaces"))
        have_th = _by_name(hthr.get("interfaces"))
        names = list(want_th) + [name for name in have_th if name not in want_th]
        for name in names:
            wentry = want_th.get(name)
            hentry = have_th.get(name, {})

            def render(option, value, name=name):
                return tmplt.render_threshold(name, option, value)

            if state == "deleted":
                if whole or wentry is not None:
                    self.commands.extend(settings_commands("deleted", {}, hentry, THRESHOLD_ATTRS, render))
            elif wentry is not None:
                mode = "merged" if state == "merged" else "replaced"
                self.commands.extend(settings_commands(mode, wentry, hentry, THRESHOLD_ATTRS, render))
            elif whole:
                self.commands.extend(settings_commands("deleted", {}, hentry, THRESHOLD_ATTRS, render))
