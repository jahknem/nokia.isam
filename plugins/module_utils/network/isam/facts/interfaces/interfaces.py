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

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    unwrap_response,
)


class InterfacesFacts(object):
    """ The isam interfaces facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec

    @staticmethod
    def _canonicalize_entry(item):
        entry = dict(item)
        if "id" in entry and "name" not in entry:
            entry["name"] = entry["id"]
        if "admin-up" in entry and "admin_up" not in entry:
            entry["admin_up"] = entry["admin-up"]
        if "link-updown-trap" in entry and "link_updown_trap" not in entry:
            entry["link_updown_trap"] = entry["link-updown-trap"]
        if "port-type" in entry and "port_type" not in entry:
            entry["port_type"] = entry["port-type"]

        entry.pop("id", None)
        entry.pop("admin-up", None)
        entry.pop("link-updown-trap", None)
        entry.pop("port-type", None)
        return entry

    def get_config(self, connection):
        config = self._module.params.get("config") or []
        commands = [
            "info configure interface port %s detail flat" % item["name"]
            for item in config
        ]
        return get_scoped_config(
            self._module,
            connection,
            config,
            "info configure interface port flat",
            commands,
        )

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
            data = self.get_config(connection)
        data = unwrap_response(data)

        # parse native config using the Interfaces template
        # the template 'getval' regexes expect lines starting with 'port ...'
        # but the device output contains 'configure interface port ...'
        # so strip the leading prefix and ignore non-config lines
        raw_lines = []
        for line in str(data or "").splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('configure interface port '):
                raw_lines.append(line.replace('configure interface ', '', 1))

        interfaces_parser = InterfacesTemplate(lines=raw_lines, module=self._module)
        parsed = interfaces_parser.parse()
        valued = parsed.values()
        objs = list(valued)

        objs = [self._canonicalize_entry(item) for item in objs]

        ansible_facts['ansible_network_resources'].pop('interfaces', None)

        params = utils.remove_empties(
            interfaces_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        validated = params.get('config') or []
        facts['interfaces'] = [self._canonicalize_entry(item) for item in validated]
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
