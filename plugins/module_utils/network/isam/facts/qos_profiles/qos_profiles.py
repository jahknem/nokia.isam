# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
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

    @staticmethod
    def _profile_command(identity):
        profile_type, name = identity
        path = Qos_profilesTemplate._profile_path({"profile_type": profile_type, "name": name})
        return ["info configure qos profiles %s flat" % path]

    def get_config(self, connection):
        """The whole resource, or only the profiles named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "qos_profiles", "info configure qos profiles flat", {
            "config": self._profile_command,
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)

        if isinstance(data, tuple):
            data = data[0]
        parser = Qos_profilesTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = list(parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("qos_profiles", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}

        facts["qos_profiles"] = params.get("config") or []
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts
