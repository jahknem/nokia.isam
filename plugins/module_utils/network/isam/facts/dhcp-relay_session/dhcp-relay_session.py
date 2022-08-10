# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam dhcp-relay_session fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.dhcp-relay_session import (
    Dhcp-relay_sessionTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.dhcp-relay_session.dhcp-relay_session import (
    Dhcp-relay_sessionArgs,
)

class Dhcp-relay_sessionFacts(object):
    """ The isam dhcp-relay_session facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Dhcp-relay_sessionArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Dhcp-relay_session network resource

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

        # parse native config using the Dhcp-relay_session template
        dhcp-relay_session_parser = Dhcp-relay_sessionTemplate(lines=data.splitlines(), module=self._module)
        objs = list(dhcp-relay_session_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('dhcp-relay_session', None)

        params = utils.remove_empties(
            dhcp-relay_session_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['dhcp-relay_session'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
