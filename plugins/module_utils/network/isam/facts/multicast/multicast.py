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
            data = connection.get("info configure igmp mcast-svc-context")
            mcast_control_data = connection.get("info configure mcast-control")
            data = data + "\n" + mcast_control_data

        multicast_config = self._parse_multicast_config(data)

        ansible_facts["ansible_network_resources"].pop("multicast", None)
        params = utils.remove_empties(
            multicast_config
        ) or {}
        facts["multicast"] = params
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _parse_multicast_config(self, config):
        multicast = {"igmp": {}, "mcast_control": {}}
        section = None

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo "):
                continue

            if line == "igmp":
                section = "igmp"
                continue
            if line == "mcast-control":
                section = "mcast_control"
                continue
            if line == "exit":
                section = None
                continue

            if section == "igmp":
                self._parse_igmp_option(line, multicast["igmp"])
            elif section == "mcast_control":
                self._parse_mcast_control_option(line, multicast["mcast_control"])

        return multicast

    def _parse_igmp_option(self, line, igmp):
        if line == "mld-snooping":
            igmp["mld_snooping"] = True
        elif line == "no mld-snooping":
            igmp["mld_snooping"] = False
        elif line == "mld-querier":
            igmp["mld_querier"] = True
        elif line == "no mld-querier":
            igmp["mld_querier"] = False
        elif line == "igmp-snooping":
            igmp["igmp_snooping"] = True
        elif line == "no igmp-snooping":
            igmp["igmp_snooping"] = False
        elif line == "igmp-querier":
            igmp["igmp_querier"] = True
        elif line == "no igmp-querier":
            igmp["igmp_querier"] = False
        elif line.startswith("query-interval "):
            val = line.split(None, 1)[1]
            try:
                igmp["query_interval"] = int(val)
            except ValueError:
                pass
        elif line.startswith("query-response-interval "):
            val = line.split(None, 1)[1]
            try:
                igmp["query_response_interval"] = int(val)
            except ValueError:
                pass
        elif line.startswith("robustness-count "):
            val = line.split(None, 1)[1]
            try:
                igmp["robustness_count"] = int(val)
            except ValueError:
                pass

    def _parse_mcast_control_option(self, line, mcast_control):
        if line == "admin-state":
            mcast_control["admin_state"] = True
        elif line == "no admin-state":
            mcast_control["admin_state"] = False
        elif line.startswith("max-groups "):
            val = line.split(None, 1)[1]
            try:
                mcast_control["max_groups"] = int(val)
            except ValueError:
                pass
        elif line.startswith("max-sources "):
            val = line.split(None, 1)[1]
            try:
                mcast_control["max_sources"] = int(val)
            except ValueError:
                pass
