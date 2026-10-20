"""Controller-side filters for focused ISAM monitoring tables."""
from __future__ import absolute_import, division, print_function

from ansible.errors import AnsibleFilterError
from ansible_collections.nokia.isam.plugins.module_utils.monitoring import (
    parse_unprovisioned_onts,
    parse_xdsl_operational_lines,
)


def checked(parser, value):
    try:
        return parser(value)
    except (ValueError, TypeError, KeyError) as exc:
        # Never return an error string as if it were a successful parsed table.
        raise AnsibleFilterError(str(exc)) from exc


class FilterModule(object):
    def filters(self):
        return {
            "parse_unprovisioned_onts": lambda value: checked(parse_unprovisioned_onts, value),
            "parse_xdsl_operational_lines": lambda value: checked(parse_xdsl_operational_lines, value),
        }
