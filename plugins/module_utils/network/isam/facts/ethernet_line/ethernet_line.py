# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

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
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    Ethernet_lineTemplate,
)
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
        """Wrapper method for `connection.get()`
        This method exists solely to allow the unit test framework to mock device connection calls.
        """
        return connection.get("info configure ethernet line")

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
        data = flatten_indented_tree(data)

        # parse native config using the Ethernet_line template
        ethernet_line_parser = Ethernet_lineTemplate(lines=data, module=self._module)

        objs = list(ethernet_line_parser.parse().values())

        for item in objs:
            item["mau"] = list(item["mau"].values())

        ansible_facts['ansible_network_resources'].pop('ethernet_line', None)

        params = utils.remove_empties(
            ethernet_line_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['ethernet_line'] = params.get("config", [])
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
