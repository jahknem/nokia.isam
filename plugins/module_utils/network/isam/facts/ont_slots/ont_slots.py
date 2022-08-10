# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam ont_slots fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.ont_slots import (
    Ont_slotsTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ont_slots.ont_slots import (
    Ont_slotsArgs,
)

class Ont_slotsFacts(object):
    """ The isam ont_slots facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = Ont_slotsArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Ont_slots network resource

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

        # parse native config using the Ont_slots template
        ont_slots_parser = Ont_slotsTemplate(lines=data.splitlines(), module=self._module)
        objs = list(ont_slots_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('ont_slots', None)

        params = utils.remove_empties(
            ont_slots_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )

        facts['ont_slots'] = params['config']
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
