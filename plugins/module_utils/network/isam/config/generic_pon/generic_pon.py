# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    GENERIC_PON_NODES,
    Generic_ponTemplate,
    parser_name,
    section,
    without_defaults,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import requested_sections


class Generic_pon(IsamResourceModule):
    """The isam_generic_pon config class (global settings: nothing is created or removed)."""

    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure generic-pon utilization threshold) (?P<suffix>.+)$",
        r"^(?P<scope>configure generic-pon utilization) (?P<suffix>(?!threshold(?:\s|$)).+)$",
        r"^(?P<scope>configure generic-pon (?:ont|alarmflag)) (?P<suffix>.+)$",
    )

    def __init__(self, module):
        super(Generic_pon, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="generic_pon",
            tmplt=Generic_ponTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        # want stays raw: an explicit default value means "reset to default". compare()
        # resets an attribute absent from want but present in have, so a default is
        # dropped from want (reset when have is non-default, no-op when have is absent).
        want = self.want or {}
        have = without_defaults(self.have)
        # deleted with config touches only the named sections, and in a section only the
        # named attributes (a section named without attributes is reset as a whole)
        requested = requested_sections(self._module) if self.state == "deleted" else set()
        given = remove_empties(self._module.params.get("config") or {})

        if self.state != "deleted" and want.get("dpinteg_threshold") is not None:
            # mandatory value without removal form: only set when given
            self.compare(parsers=["dpinteg_threshold"], want=want, have=have)
        for path, _node, attrs in GENERIC_PON_NODES:
            if requested and (path[0] not in requested or not _named(path, given)):
                continue
            wanted, current = section(want, path), section(have, path)
            values = dict((k, v) for k, v in wanted.items() if not isinstance(v, dict))
            current = dict((k, v) for k, v in current.items() if not isinstance(v, dict))
            if self.state == "merged":
                values = self._merged_values(attrs, values, current)
            elif self.state == "deleted":
                values = dict((k, v) for k, v in current.items() if values and k not in values)
            elif self.state != "rendered":
                values = self._drop_defaults(attrs, values)
            self.compare(parsers=[parser_name(path, option) for option, _cli, _kind, _default in attrs],
                         want=values, have=current)

    @staticmethod
    def _drop_defaults(attrs, values):
        """A value equal to its device default counts as unset (dropped from want)."""
        values = dict(values)
        for option, _cli, _kind, default in attrs:
            if values.get(option) == default:
                values.pop(option, None)
        return values

    def _merged_values(self, attrs, values, current):
        """merged keeps omitted attributes; a given default resets, a given value sets."""
        merged = dict(current)
        for option, _cli, _kind, default in attrs:
            if option not in values:
                continue
            if values[option] == default:
                merged.pop(option, None)
            else:
                merged[option] = values[option]
        return merged


def _named(path, given):
    """deleted: whether a section is named -- itself, or through its top section given
    without any content ('utilization: {}' resets utilization and its threshold). The
    caller has already checked that path[0] is among the requested sections."""
    if not given.get(path[0]):
        return True
    return len(path) == 1 or bool(section(given, path))
