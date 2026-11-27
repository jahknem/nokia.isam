# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam xdsl_inm fact class.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_inm.xdsl_inm import (
    Xdsl_inmArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_inm import (
    SIDES,
    Xdsl_inmTemplate,
)


class Xdsl_inmFacts(object):
    """The isam_xdsl_inm facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Xdsl_inmArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the sensors named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "xdsl_inm", "info configure xdsl imp-noise-sensor flat", {
            "near_end": "info configure xdsl imp-noise-sensor near-end %s flat",
            "far_end": "info configure xdsl imp-noise-sensor far-end %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate facts for the xdsl_inm network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]
        parser = Xdsl_inmTemplate(lines=str(data or "").splitlines(), module=self._module)
        parsed = parser.parse()
        objs = {}
        for side, _cli in SIDES:
            entries = list(parsed.get(side, {}).values())
            if entries:
                objs[side] = entries

        ansible_facts["ansible_network_resources"].pop("xdsl_inm", None)
        params = {}
        if objs:
            params = utils.remove_empties(
                parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
            ) or {}
        facts["xdsl_inm"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
