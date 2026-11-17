# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure xdsl system`` (system-wide xDSL settings)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import (
    parse_attributes,
)

# node option -> (CLI node, ((option, CLI keyword, kind), ...)); kind "flag" or "value".
NODES = (
    ("auto_port_reset", "auto-port-reset", (("enable", "enable", "flag"),)),
)

_LINE = re.compile(r"^(?:configure\s+)?xdsl\s+system\s+(?P<node>\S+)(?:\s+(?P<rest>.*))?$")
_BY_CLI = dict((cli, (option, attrs)) for option, cli, attrs in NODES)
_BY_OPTION = dict((option, (cli, attrs)) for option, cli, attrs in NODES)


class Xdsl_systemTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_systemTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        """{node option: {attribute: value}} for the lines given."""
        result = {}
        for raw in self._lines:
            match = _LINE.match(raw.strip())
            if not match or match.group("node") not in _BY_CLI:
                continue
            option, attrs = _BY_CLI[match.group("node")]
            cli_to_attr = dict((cli, attr) for attr, cli, _kind in attrs)
            flags = tuple(cli for _attr, cli, kind in attrs if kind == "flag")
            entry = result.setdefault(option, {})
            parse_attributes(match.group("rest"), entry, cli_to_attr, flags)
        return result

    @staticmethod
    def render_attr(node, attr, value):
        """Set command for one attribute; value None renders the reset (``no``) form."""
        cli_node, attrs = _BY_OPTION[node]
        cli, kind = [(c, k) for a, c, k in attrs if a == attr][0]
        if kind == "flag":
            suffix = cli if value else "no " + cli
        elif value is None:
            suffix = "no " + cli
        else:
            suffix = "{0} {1}".format(cli, value)
        return "configure xdsl system {0} {1}".format(cli_node, suffix)

    PARSERS = [
        {"name": "xdsl_system", "getval": re.compile(r"^$"), "setval": "", "result": {}},
    ]
