# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from queue import Empty
import re

__metaclass__ = type

"""
The isam bridges fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy
#import debugpy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.bridges import (
    BridgesTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.bridges.bridges import (
    BridgesArgs,
)

class BridgesFacts(object):
    """ The isam bridges facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = BridgesArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Bridges network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        # if not debugpy.is_client_connected():
        #     debugpy.listen(("localhost",3000))
        #     debugpy.wait_for_client()
        if not data:
            data = connection.get("info configure bridge flat")
        
        data = self._flatten_config(data)

        # debugpy.breakpoint()

        # parse native config using the Bridges template
        bridges_parser = BridgesTemplate(lines=data, module=self._module)
        parsed = bridges_parser.parse()
        values = parsed.values()
        list_parsed = list(parsed)
        list_valued = list(values)
        objs = list(bridges_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('bridges', None)

        # debugpy.breakpoint()

        params = utils.remove_empties(bridges_parser.validate_config(self.argument_spec, {"config": list_valued}, redact=True))

        facts['bridges'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    def _divide_chunks(self, l, n):
        for i in range(0, len(l), n):
            yield l[i:i + n]

    def _flatten_config(self, config):

        parser = re.compile(
                r"""
                configure\sbridge\s(port\s(?P<id>\S+)\s)?(vlan-id(?P<vlan_id>\d+)\s)?(?P<rest>.*)
                """
            )
        
        flattened_config = []
        bridge_string = None        
        vlan_string = None
        lines = config.splitlines()
        for line in lines:  
        # if line contains bridge port id, store it in bridge_id
            match = parser.match(line)
            if match:
                regDict = match.groupdict()
                if 'id' in regDict:
                    bridge_string = "port" + regDict['id']
                if 'vlan_id' in regDict:
                    vlan_string = "vlan-id" + regDict['vlan_id']
                if 'rest' in regDict:
                    values = match.group("rest").split()
                    for item,item2 in self._divide_chunks(values,2):
                        flattened_config.append("configure bridge ".join([bridge_string, vlan_string, item, item2]))
        return flattened_config
