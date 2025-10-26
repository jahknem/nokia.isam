# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam interfaces fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy
import debugpy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
    InterfacesArgs,
)

class InterfacesFacts(object):
    """ The isam interfaces facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Interfaces network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []
           
        if not data:
            data = connection.get("info configure interface port flat")
            self._module.warn(f"LINES={len(data.splitlines())}")
            self._module.warn(data[:1000])

        # parse native config using the Interfaces template
        # the template 'getval' regexes expect lines starting with 'port ...'
        # but the device output contains 'configure interface port ...'
        # so strip the leading prefix and ignore non-config lines
        raw_lines = []
        for line in data.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('configure interface '):
                raw_lines.append(line.replace('configure interface ', '', 1))

        interfaces_parser = InterfacesTemplate(lines=raw_lines, module=self._module)
        parsed = interfaces_parser.parse()
        valued = parsed.values()
        objs = list(valued)


        ansible_facts['ansible_network_resources'].pop('interfaces', None)

        params = utils.remove_empties(
            interfaces_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts['interfaces'] = params.get('config') or []
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
