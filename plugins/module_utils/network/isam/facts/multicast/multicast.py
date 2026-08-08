# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.multicast.multicast import (
    MulticastArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import (
    MulticastTemplate,
)


class MulticastFacts(object):
    """The isam multicast facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = MulticastArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            igmp_data = connection.get("info configure igmp flat")
            mcast_data = connection.get("info configure mcast-control flat")
            data = igmp_data + "\n" + mcast_data

        data = self._flatten_config(data)
        parser = MulticastTemplate(lines=data, module=self._module)
        parsed = parser.parse()

        ansible_facts["ansible_network_resources"].pop("multicast", None)
        params = utils.remove_empties(
            parsed
        ) or {}
        facts["multicast"] = params
        facts["igmp"] = params.get("igmp", {})
        facts["mcast_control"] = params.get("mcast_control", {})
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    @staticmethod
    def _flatten_config(config):
        flat_config = []
        if not config:
            return flat_config

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("echo") or line.startswith("#"):
                continue
            if line.startswith("configure igmp ") or line.startswith("configure mcast-control "):
                flat_config.append(line)

        return flat_config
