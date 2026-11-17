# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The isam_l2uni_onts fact class (configure l2uni ont performance-monitor / tc-layer-threshold)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    flatten_indented_tree,
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2uni_onts.l2uni_onts import (
    L2uni_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2uni_onts import (
    L2uni_ontsTemplate,
)


def config_lines(data):
    """Flat configure lines of a reply; indented output is flattened first."""
    text = str(unwrap_response(data) or "")
    stripped = [raw.strip() for raw in text.splitlines()]
    if "exit" in stripped:
        # Indented (non-flat) output closes every level with "exit".
        indented = "\n".join(raw for raw in text.splitlines() if raw.strip() and not raw.strip().startswith("#"))
        return [line for line in (flatten_indented_tree(indented) or []) if line.startswith("configure ")]
    return [line for line in stripped if line.startswith("configure ")]


def parse_sections(template_cls, module, data):
    """{section: [entry, ...]} parsed with a UniPmTemplate subclass."""
    parser = template_cls(lines=config_lines(data), module=module)
    return parser, dict((section, list(entries.values())) for section, entries in parser.parse().items())


class L2uni_ontsFacts(object):
    """The isam_l2uni_onts facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = L2uni_ontsArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the UNIs named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "l2uni_onts", "info configure l2uni flat", {
            "performance_monitor": "info configure l2uni ont performance-monitor %s flat",
            "tc_layer_threshold": "info configure l2uni ont tc-layer-threshold %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate the facts for the l2uni_onts network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        parser, sections = parse_sections(L2uni_ontsTemplate, self._module, data)

        ansible_facts["ansible_network_resources"].pop("l2uni_onts", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": sections}, redact=True)
        ) or {}
        facts["l2uni_onts"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
