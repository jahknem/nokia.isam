# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam interface_cages fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interface_cages import (
    InterfaceCagesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interface_cages.interface_cages import (
    InterfaceCagesArgs,
)


class InterfaceCagesFacts(object):
    """ The isam interface_cages facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = InterfaceCagesArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure interface cage")

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for InterfaceCages network resource

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

        # parse native config using the InterfaceCages template
        interface_cages_parser = InterfaceCagesTemplate(
            lines=self._flatten_config(data), module=self._module
        )
        objs = list(interface_cages_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('interface_cages', None)

        params = utils.remove_empties(
            interface_cages_parser.validate_config(
                self.argument_spec, {"config": objs}, redact=True
            )
        ) or {}

        facts['interface_cages'] = params.get('config') or []
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def _flatten_config(self, data):
        lines = []
        current_id = None
        for line in (data or "").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("echo"):
                continue
            if stripped in ("configure", "configure interface", "exit"):
                continue

            if stripped.startswith("cage "):
                parts = stripped.split()
                if len(parts) > 1:
                    current_id = parts[1]
                lines.append("configure interface " + stripped)
            elif current_id and line[:1].isspace():
                lines.append("configure interface cage {0} {1}".format(current_id, stripped))
            else:
                lines.append("configure interface " + stripped)
        return lines
