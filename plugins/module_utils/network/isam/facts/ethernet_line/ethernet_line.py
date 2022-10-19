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

from copy import deepcopy
from anytree import Node, PreOrderIter
import debugpy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    Ethernet_lineTemplate,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ethernet_line.ethernet_line import (
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

        # if not debugpy.is_client_connected():
        #     debugpy.listen(("localhost",3000))
        #     debugpy.wait_for_client()
        

        if not data:
            data = self.get_config(connection)
        data = self._flatten_config(data)

        # parse native config using the Ethernet_line template
        ethernet_line_parser = Ethernet_lineTemplate(lines=data, module=self._module)
        # debugpy.breakpoint()
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

    # Counts the number of spaces at the beginning of a string
    def _count_spaces(self, line):
        spaces = 0
        for char in line:
            if char == ' ':
                spaces += 1
            else:
                break
        return spaces

    # Parses the config into a tree structure and cleans up the config so that only relevant data is returned
    # The tree structure is determined by the number of spaces at the beginning of each line
    def _parse_config_to_tree(self, config):
        if not config:
            return None
        chapter = 0
        last_spaces = 0
        root = None
        parent_node = None
        for line in config.splitlines():

            # Check if line is valid
            if line.startswith('echo') or line.startswith('#'):
                continue

            # Only here the actual content begins
            # Check if parent node exists. Otherwise create it using first line
            if parent_node is None:
                root = Node(line.split('#',1)[0].strip())
                parent_node = root
                prev_node = root
                
            # The "exit" string is not relevant for us but we need to keep track of the indentation. If the indent is smaller than the previous line, we need to go up the tree
            elif "exit" in line:
                if self._count_spaces(line) < last_spaces:
                    parent_node = parent_node.parent   
                else: 
                    continue

            # Check if line is a child of the previous line as a greater indent means the line has to be a child of the previous line
            elif self._count_spaces(line) > last_spaces:
                parent_node = prev_node
                prev_node = Node(line.split('#',1)[0].strip(), parent=prev_node)


            
            # In all other cases the current line is a sibling of the previous line
            else:
                prev_node = Node(line.split('#',1)[0].strip(), parent=parent_node)
            
            # In any case, the indentation spaces of the current line become the last spaces to be used for the next line
            last_spaces = self._count_spaces(line)
        return root


    def _flatten_config(self, config):
        if not config:
            return None
        flat_config = []
        root = self._parse_config_to_tree(config)
        for leave in root.leaves:
            line = []
            for node in leave.path:
                line.append(node.name)
            flat_config.append(" ".join(line))
        return flat_config

    
