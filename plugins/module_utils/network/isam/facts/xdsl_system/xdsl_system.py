# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam xdsl_system fact class.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_system.xdsl_system import (
    Xdsl_systemArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_system import (
    Xdsl_systemTemplate,
)


class Xdsl_systemFacts(object):
    """The isam_xdsl_system facts class (a settings block, always read completely)."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_systemArgs.argument_spec

    def get_config(self, connection):
        return connection.get("info configure xdsl system flat")

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate facts for the xdsl_system network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]
        parser = Xdsl_systemTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = parser.parse()

        ansible_facts["ansible_network_resources"].pop("xdsl_system", None)
        params = {}
        if objs:
            params = utils.remove_empties(
                parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
            ) or {}
        facts["xdsl_system"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
