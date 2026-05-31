# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_maps.qos_maps import (
    Qos_mapsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_maps import (
    Qos_mapsTemplate,
)


class Qos_mapsFacts(object):
    """The isam qos_maps facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Qos_mapsArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure qos tc-map-dot1p flat") + "\n" + \
                   connection.get("info configure qos dscp-map-dot1p flat") + "\n" + \
                   connection.get("info configure qos up-ctrl-pkt flat") + "\n" + \
                   connection.get("info configure qos dn-ctrl-pkt flat")

        parser = Qos_mapsTemplate(lines=data.splitlines(), module=self._module)
        objs = parser.parse()

        ansible_facts["ansible_network_resources"].pop("qos_maps", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}

        facts["qos_maps"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
