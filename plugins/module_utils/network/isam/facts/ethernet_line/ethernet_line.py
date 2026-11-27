# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import re


__metaclass__ = type

"""
The isam ethernet_line fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    flatten_indented_tree,
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    LINE_FLAGS,
    LINE_VALUES,
    MAU_FLAGS,
    MAU_VALUES,
    TCA_FLAGS,
    TCA_THRESHOLDS,
    Ethernet_lineTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import iter_cli_fields
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ethernet_line.ethernet_line import (
    Ethernet_lineArgs,
)


class Ethernet_lineFacts(object):
    """ The isam ethernet_line facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Ethernet_lineArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the lines named in config (targeted gathering).

        Their MAUs are read with them.
        """
        return get_targeted_config(self._module, connection, "ethernet_line", "info configure ethernet line flat", {
            "config": "info configure ethernet line %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Ethernet_line network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        lines = str(data or "").splitlines()
        if not any(line.strip().startswith("configure ethernet line ") for line in lines):
            lines = flatten_indented_tree(data) or []
        data = self._split_attributes(lines, "configure ethernet line ")

        # parse native config using the Ethernet_line template
        ethernet_line_parser = Ethernet_lineTemplate(lines=data, module=self._module)

        objs = list(ethernet_line_parser.parse().values())

        for item in objs:
            if "mau" in item:
                item["mau"] = list(item["mau"].values())
        # A bare line (only defaults: what the detail probe returns for a default-only
        # line) names an existing line: keep it as its identity (read contract).
        known = set(item.get("if_index") for item in objs)
        for line in lines:  # before _split_attributes, which drops a line without attributes
            match = re.match(r"^configure ethernet line (\S+)$", str(line).strip())
            if match and match.group(1) not in known:
                objs.append({"if_index": match.group(1)})
                known.add(match.group(1))

        ansible_facts['ansible_network_resources'].pop('ethernet_line', None)

        params = utils.remove_empties(
            ethernet_line_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['ethernet_line'] = params.get("config", [])
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    @staticmethod
    def _split_attributes(lines, prefix):
        """Split each device line into one line per attribute (the template parses one
        attribute per line): 'configure ethernet line <id> mau 1 type X power down' becomes
        '... mau 1 type X' and '... mau 1 power down'."""
        result = []
        for raw in lines:
            line = raw.strip()
            if not line.startswith(prefix):
                continue
            tokens = line[len(prefix):].split()
            if len(tokens) < 2:
                continue
            scope, rest = prefix + tokens[0], tokens[1:]
            if rest[0] == "tca-line-threshold":
                scope, rest, flags, values = scope + " tca-line-threshold", rest[1:], TCA_FLAGS, TCA_THRESHOLDS
            elif rest[0] == "mau" and len(rest) > 1:
                scope, rest, flags, values = "%s mau %s" % (scope, rest[1]), rest[2:], MAU_FLAGS, MAU_VALUES
            else:
                flags, values = LINE_FLAGS, LINE_VALUES
            for negate, key, value in iter_cli_fields(rest, bool_fields=flags, value_fields=values):
                result.append(" ".join(word for word in (scope, "no" if negate else "", key, value or "") if word))
        return result
