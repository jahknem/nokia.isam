# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam nat fact class.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.nat.nat import (
    NatArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.nat import (
    NatTemplate,
)


class NatFacts(object):
    """The isam_nat facts class (a settings block, always read completely)."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = NatArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure nat flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate facts for the nat network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]
        parser = NatTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = parser.parse()

        ansible_facts["ansible_network_resources"].pop("nat", None)
        params = {}
        if objs:
            params = utils.remove_empties(
                parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
            ) or {}
        facts["nat"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
