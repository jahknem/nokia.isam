# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.mcast_general.mcast_general import (
    Mcast_generalArgs,
)


class Mcast_generalFacts(object):
    """The isam mcast_general facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Mcast_generalArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure mcast general")

        mcast_general_config = self._parse_mcast_general_config(data)

        ansible_facts["ansible_network_resources"].pop("mcast_general", None)
        params = utils.remove_empties(
            mcast_general_config
        ) or {}
        facts["mcast_general"] = params
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    def _parse_mcast_general_config(self, config):
        mcast_general = {}
        section = None

        for raw_line in config.splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("echo "):
                continue

            if line == "general":
                section = "general"
                continue
            if line == "exit":
                section = None
                continue

            if section == "general":
                self._parse_general_option(line, mcast_general)

        return mcast_general

    def _parse_general_option(self, line, config):
        if line == "admin-state":
            config["admin_state"] = True
        elif line == "no admin-state":
            config["admin_state"] = False
        elif line.startswith("forward-method "):
            config["forward_method"] = line.split(None, 1)[1]
