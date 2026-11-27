# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The isam_uni_onts fact class (configure uni ont tc-layer)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.l2uni_onts.l2uni_onts import (
    parse_sections,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.uni_onts.uni_onts import (
    Uni_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.uni_onts import (
    Uni_ontsTemplate,
)


class Uni_ontsFacts(object):
    """The isam_uni_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Uni_ontsArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the UNIs named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "uni_onts", "info configure uni flat", {
            "config": "info configure uni ont tc-layer %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for the uni_onts network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        parser, sections = parse_sections(Uni_ontsTemplate, self._module, data)

        ansible_facts["ansible_network_resources"].pop("uni_onts", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": sections.get("config", [])}, redact=True)
        ) or {}
        facts["uni_onts"] = params.get("config") or []
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
