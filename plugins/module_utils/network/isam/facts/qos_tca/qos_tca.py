# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_tca.qos_tca import (
    Qos_tcaArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_tca import (
    Qos_tcaTemplate,
)


class Qos_tcaFacts(object):
    """The isam_qos_tca facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Qos_tcaArgs.argument_spec

    @staticmethod
    def _tca_command(identity):
        name, queue = identity
        return ["info configure qos tca %s queue %s flat" % (name, queue)]

    def get_config(self, connection):
        """The whole resource, or only the port/queue instances named in config."""
        return get_targeted_config(self._module, connection, "qos_tca", "info configure qos tca flat", {
            "config": self._tca_command,
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]
        parser = Qos_tcaTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = list(parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("qos_tca", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["qos_tca"] = params.get("config") or []
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
