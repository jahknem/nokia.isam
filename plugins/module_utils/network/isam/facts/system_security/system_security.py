# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import (
    Isam_system_securityArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    Isam_system_securityTemplate,
)

# section -> single-instance read command (identity is the entry name)
_TARGETED = {
    "operators": "info configure system security operator %s flat",
    "profiles": "info configure system security profile %s flat",
    "snmp_communities": "info configure system security snmp community %s flat",
    "snmp_views": "info configure system security snmp view %s flat",
    "snmp_managers": "info configure system security snmp manager %s flat",
    "snmp_notify_profiles": "info configure system security snmp notify-profile %s flat",
    "radius_auth_servers": "info configure system security radius auth-server %s flat",
    "radius_policies": "info configure system security radius policy %s flat",
    "radius_dyn_auth_clients": "info configure system security radius dyn-auth-client %s flat",
}


class Isam_system_securityFacts(object):
    """The isam_system_security facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_system_securityArgs.argument_spec

    def get_config(self, connection):
        return get_targeted_config(self._module, connection, "isam_system_security",
                                   "info configure system security flat", _TARGETED)

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        parser = Isam_system_securityTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = parser.parse()

        ansible_facts["ansible_network_resources"].pop("isam_system_security", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["isam_system_security"] = params.get("config", {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
