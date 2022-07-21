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
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
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
            data = connection.get("info configure interface port detail")

        # parse native config using the Interfaces template
        #if not debugpy.is_client_connected():
        #    debugpy.listen(("localhost",3000))
        #    debugpy.wait_for_client()
        #    debugpy.breakpoint()
        lines = data.splitlines()
        interfaces_parser = InterfacesTemplate(lines=lines, module=self._module)
        parsed = interfaces_parser.parse()
        valued = parsed.values()
        objs = list(valued)

        ansible_facts['ansible_network_resources'].pop('interfaces', None)

        params = utils.remove_empties(
            interfaces_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['interfaces'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
