# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_profiles.xdsl_profiles import (
    Xdsl_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    Xdsl_profilesTemplate,
)


class Xdsl_profilesFacts(object):
    """The isam xdsl_profiles facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_profilesArgs.argument_spec
        self.template = Xdsl_profilesTemplate()

    def get_config(self, connection):
        commands = [
            "info configure xdsl service-profile",
            "info configure xdsl spectrum-profile",
            "info configure xdsl dpbo-profile",
            "info configure xdsl vect-profile",
            "info configure xdsl vce-profile",
        ]
        output = []
        for command in commands:
            data = connection.get(command)
            output.append(data[0] if type(data) == tuple else data)
        return "\n".join(output)

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        if type(data) == tuple:
            data = data[0]

        params = self.template.normalize(self.template.parse(data))
        ansible_facts["ansible_network_resources"].pop("xdsl_profiles", None)
        facts["xdsl_profiles"] = params
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
