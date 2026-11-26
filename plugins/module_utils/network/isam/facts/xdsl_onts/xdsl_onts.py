# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam xdsl_onts fact class.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_onts.xdsl_onts import (
    Xdsl_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_onts import (
    Xdsl_ontsTemplate,
)


class Xdsl_ontsFacts(object):
    """The isam_xdsl_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_ontsArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the ONTs named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "xdsl_onts", "info configure xdsl ont flat", {
            "config": "info configure xdsl ont interface %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate facts for the xdsl_onts network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]
        parser = Xdsl_ontsTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = list(parser.parse().values())

        ansible_facts["ansible_network_resources"].pop("xdsl_onts", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["xdsl_onts"] = params.get("config") or []
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
