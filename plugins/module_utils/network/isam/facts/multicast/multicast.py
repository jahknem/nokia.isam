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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)

IGMP_PACKAGE = "info configure igmp package %s flat"
MCAST_CONTROL_PACKAGE = "info configure mcast-control package %s flat"

# facts resource -> {instance list: single-instance read}
TARGETED_FORMATS = {
    "igmp": {"packages": IGMP_PACKAGE},
    "mcast_control": {"packages": MCAST_CONTROL_PACKAGE},
    "multicast": {"igmp.packages": IGMP_PACKAGE, "mcast_control.packages": MCAST_CONTROL_PACKAGE},
}


def _whole(connection):
    igmp_data = connection.get("info configure igmp flat")
    mcast_data = connection.get("info configure mcast-control flat")
    return igmp_data + "\n" + mcast_data


def module_resource(module):
    """Which of the three public resources the module is (they share this facts class)."""
    spec = getattr(module, "argument_spec", None) or {}
    options = (spec.get("config") or {}).get("options") or {}
    if "igmp" in options:
        return "multicast"
    if "admin_state" in options:
        return "mcast_control"
    if "mld_snooping" in options:
        return "igmp"
    return None


class MulticastFacts(object):
    """The isam multicast facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = MulticastArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            resource = module_resource(self._module)
            if resource:
                data = get_targeted_config(self._module, connection, resource, _whole, TARGETED_FORMATS[resource])
            else:
                data = _whole(connection)

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
