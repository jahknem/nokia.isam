# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import warn_retained_on_delete
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import TableResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    TABLE,
    Software_mngtTemplate,
)


class Software_mngt(TableResourceModule):
    """The isam_software_mngt config class (global settings; OSWP records are a list)."""

    TABLE = TABLE

    def __init__(self, module):
        super(Software_mngt, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="software_mngt",
            tmplt=Software_mngtTemplate(),
        )

    def generate_commands(self):
        super(Software_mngt, self).generate_commands()
        warn_retained_on_delete(self)

    # An OSWP is a fixed slot (index 1 or 2) and has no removal command: the CLI guide
    # (software-mngt, section 20.3) has no 'no oswp' form. deleted (identity alone or
    # without config) and overridden (an OSWP not given) reset its removable attributes
    # instead: 'no activate' / 'no auto-verify' / 'no on-schedule-time' return to
    # 'manually' / 'disabled' / unset, so nothing ever activates or verifies a software
    # package unless a request names it. admin-state is not reset implicitly (an
    # operational switch); it changes only when named.
    _IMPLICIT_RESET_SKIP = ("admin_state",)

    def _compare_instances(self, node, want, have):
        if node.key != "oswp" or self.state not in ("deleted", "overridden"):
            return super(Software_mngt, self)._compare_instances(node, want, have)
        ident = node.identity
        wantd = dict((str(entry[ident]), entry) for entry in want)
        haved = dict((str(entry[ident]), entry) for entry in have)
        if self.state == "overridden":
            for name, have_entry in haved.items():
                if name not in wantd:
                    self._reset_oswp(node, name, set(), have_entry)
            for name, want_entry in wantd.items():
                self.commands.extend(self.TABLE.diff_commands(
                    node, name, want_entry, haved.get(name, {}), "overridden"))
            return
        for name, have_entry in haved.items():
            if wantd and name not in wantd:
                continue
            want_entry = wantd.get(name) or {}
            named = set(key for key, value in want_entry.items() if key != ident and value is not None)
            self._reset_oswp(node, name, named, have_entry)

    def _reset_oswp(self, node, name, named, have_entry):
        """Reset the named attributes of OSWP name (all resettable ones when none is named)."""
        if named:
            keep = dict((key, value) for key, value in have_entry.items() if key not in named)
        else:
            keep = dict((key, value) for key, value in have_entry.items()
                        if key in self._IMPLICIT_RESET_SKIP or key == node.identity)
            fixed = [attr.cli for attr in node.attrs
                     if not attr.removable and have_entry.get(attr.option) is not None]
            if fixed:
                self._module.warn("oswp %s has no removal form in ISAM CLI (fixed slot); its resettable "
                                  "attributes are reset, %s retained" % (name, ", ".join(fixed)))
        self.commands.extend(self.TABLE.diff_commands(node, name, keep, have_entry, "replaced"))
