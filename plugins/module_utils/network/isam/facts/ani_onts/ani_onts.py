# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    strip_noise_lines,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ani_onts.ani_onts import (
    Ani_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ani_onts import (
    Ani_ontsTemplate,
)


class Ani_ontsFacts(object):
    """The isam ani_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Ani_ontsArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure ani ont flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]

        data = strip_noise_lines(data, "configure ani ont ")
        ani_onts_parser = Ani_ontsTemplate(lines=data, module=self._module)
        objs = list(ani_onts_parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("ani_onts", None)
        params = utils.remove_empties(
            ani_onts_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["ani_onts"] = list(params.get("config") or [])
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
