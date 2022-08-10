# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam bridge_vlans fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.bridge_vlans import (
    Bridge_vlansTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.bridge_vlans.bridge_vlans import (
    Bridge_vlansArgs,
)

class Bridge_vlansFacts(object):
    """ The isam bridge_vlans facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Bridge_vlansArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Bridge_vlans network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = connection.get()

        # parse native config using the Bridge_vlans template
        bridge_vlans_parser = Bridge_vlansTemplate(lines=data.splitlines(), module=self._module)
        objs = list(bridge_vlans_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('bridge_vlans', None)

        params = utils.remove_empties(
            bridge_vlans_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['bridge_vlans'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
