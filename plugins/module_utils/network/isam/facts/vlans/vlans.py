# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam vlans fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VlansTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import (
    VlansArgs,
)

class VlansFacts(object):
    """ The isam vlans facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = VlansArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Vlans network resource

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

        # parse native config using the Vlans template
        vlans_parser = VlansTemplate(lines=data.splitlines(), module=self._module)
        objs = list(vlans_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('vlans', None)

        params = utils.remove_empties(
            vlans_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['vlans'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
