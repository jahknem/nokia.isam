# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

import shlex

__metaclass__ = type

"""
The isam vlans fact class
It is in this file the configuration is collected from the device
for a given resource, parsed, and the facts tree is populated
based on the configuration.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
    VLAN_DEFAULTS,
    VLAN_FLAG_KEYWORDS,
    VLAN_VALUE_KEYWORDS,
    VlansTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import (
    VlansArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    iter_cli_fields,
)


class VlansFacts(object):
    """ The isam vlans facts class
    """

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = VlansArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the VLANs named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "vlans", "info configure vlan id flat", {
            "config": "info configure vlan id %s flat",
        })

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
            data = self.get_config(connection)

        # parse native config using the Vlans template
        vlans_parser = VlansTemplate(lines=self._flatten_config(data), module=self._module)
        objs = list(vlans_parser.parse().values())

        ansible_facts['ansible_network_resources'].pop('vlans', None)

        params = utils.remove_empties(
            vlans_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}

        # device defaults (flags off included) are not reported
        facts['vlans'] = [dict((key, value) for key, value in entry.items()
                               if value is not False and VLAN_DEFAULTS.get(key) != value)
                          for entry in params.get('config') or []]
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts

    @staticmethod
    def _flatten_config(data):
        """One line per attribute, 'configure vlan id <id> [no] <kw> [<value>]', from the
        packed flat lines or the hierarchical form ('id <id> ...' with indented attributes)."""
        flat = []
        current_id = None
        for raw in (data or "").splitlines():
            line = raw.strip()
            if not line or line.startswith(("#", "echo")) or line in ("configure", "configure vlan", "exit"):
                continue
            if line.startswith("configure vlan id "):
                flat.append(line)
            elif line.startswith("id "):
                current_id = line.split()[1]
                flat.append("configure vlan " + line)
            elif current_id and raw[:1].isspace():
                flat.append("configure vlan id %s %s" % (current_id, line))
        result = []
        for line in flat:
            parts = line.split(None, 4)  # configure vlan id <id> [<attributes>]
            vlan_id, body = parts[3], parts[4] if len(parts) > 4 else ""
            result.append("configure vlan id %s" % vlan_id)
            for negate, key, value in iter_cli_fields(shlex.split(body), bool_fields=VLAN_FLAG_KEYWORDS,
                                                      value_fields=VLAN_VALUE_KEYWORDS):
                if value is not None and " " in value:
                    value = '"%s"' % value
                result.append(" ".join(w for w in ("configure vlan id", vlan_id, "no" if negate else "", key, value or "") if w))
        return result
