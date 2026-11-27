# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure xdsl ont interface <ont>`` (xDSL settings of an ONT)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import (
    parse_attributes,
)

# (option, CLI keyword); value attributes, ``no <keyword>`` resets to the default.
ATTRS = (
    ("dpbo_profile", "dpbo-profile"),
)

_CLI_TO_ATTR = dict((cli, attr) for attr, cli in ATTRS)
_ATTR_TO_CLI = dict(ATTRS)
_LINE = re.compile(r"^(?:configure\s+)?xdsl\s+ont\s+interface\s+(?P<ont_idx>\S+)(?:\s+(?P<rest>.*))?$")


class Xdsl_ontsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_ontsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        """{ont_idx: entry} for the lines given."""
        result = {}
        for raw in self._lines:
            match = _LINE.match(raw.strip())
            if not match:
                continue
            ont_idx = match.group("ont_idx")
            entry = result.setdefault(ont_idx, {"ont_idx": ont_idx})
            parse_attributes(match.group("rest"), entry, _CLI_TO_ATTR)
        return result

    @staticmethod
    def command(ont_idx, suffix=""):
        cmd = "configure xdsl ont interface {0}".format(ont_idx)
        return cmd + (" " + suffix if suffix else "")

    @staticmethod
    def render_attr(entry, attr):
        """Set command for entry[attr], or its ``no`` form when the value is None."""
        cli = _ATTR_TO_CLI[attr]
        value = entry.get(attr)
        if value is None:
            return Xdsl_ontsTemplate.command(entry["ont_idx"], "no " + cli)
        return Xdsl_ontsTemplate.command(entry["ont_idx"], "{0} {1}".format(cli, value))

    PARSERS = [
        {"name": "xdsl_onts", "getval": re.compile(r"^$"), "setval": "", "result": {}},
    ]
