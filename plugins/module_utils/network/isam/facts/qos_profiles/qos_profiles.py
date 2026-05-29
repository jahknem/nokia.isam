# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_profiles.qos_profiles import (
    Qos_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)


class Qos_profilesFacts(object):
    """The isam qos_profiles facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Qos_profilesArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = connection.get("info configure qos profiles")

        parser = Qos_profilesTemplate(lines=data.splitlines(), module=self._module)
        objs = list(parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("qos_profiles", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}

        facts["qos_profiles"] = params.get("config") or []
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
