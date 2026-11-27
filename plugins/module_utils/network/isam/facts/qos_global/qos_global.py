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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_global.qos_global import (
    Qos_globalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_global import (
    LIST_NODES,
    SECTIONS,
    SETTINGS_NODES,
    Qos_globalTemplate,
    normalize_line_card,
    strip_defaults,
)

# One read per CLI node. The bare "configure qos" settings (general) have no node of
# their own: ISAM "info" has no depth limit, so they can only be read with
# "info configure qos flat", which also returns every qos interface/profile/tca/map
# line (thousands on a loaded node). That read is issued only when general is in
# scope, and then it replaces the per-node reads (it contains them all).
_FULL = "info configure qos flat"
_NODE_COMMANDS = dict(
    [(section, "info configure qos %s flat" % node) for section, node in SETTINGS_NODES.items()]
    + [(section, "info configure qos %s flat" % node) for section, (node, _key) in LIST_NODES.items()]
)
# Releases without a node answer like this; the node then simply has no settings.
_ABSENT = ("invalid token", "instance does not exist", "specified instance does not exist")


def _absent(text):
    text = str(text).lower()
    return any(marker in text for marker in _ABSENT)


class Qos_globalFacts(object):
    """The isam_qos_global facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Qos_globalArgs.argument_spec

    def sections_in_scope(self):
        """Sections the module needs: the named ones for merged/replaced/overridden/deleted/
        gathered with config, otherwise all (deleted/gathered without config, isam_facts)."""
        params = getattr(self._module, "params", None) or {}
        config = params.get("config")
        state = params.get("state", "merged")
        if self._module is None or not isinstance(config, dict) or state not in ("merged", "replaced", "overridden", "deleted", "gathered"):
            return list(SECTIONS)
        named = [section for section in SECTIONS if config.get(section) is not None]
        return named or list(SECTIONS)

    @staticmethod
    def _line_card_command(name):
        return ["info configure qos global %s flat" % normalize_line_card(name)]

    def _get_full_config(self, connection):
        sections = self.sections_in_scope()
        if "general" in sections:
            return unwrap_response(connection.get(_FULL)) or ""
        replies = []
        for section in sections:
            try:
                reply = unwrap_response(connection.get(_NODE_COMMANDS[section])) or ""
            except Exception as exc:  # connection plugins surface device errors here
                if _absent(exc):
                    continue
                raise
            if not _absent(reply):
                replies.append(reply)
        return "\n".join(replies)

    def get_config(self, connection):
        """The resource sections in scope, or only the line cards named in config (gathered)."""
        return get_targeted_config(self._module, connection, "qos_global", self._get_full_config, {
            "line_cards": self._line_card_command,
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        parser = Qos_globalTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = strip_defaults(parser.parse())

        ansible_facts["ansible_network_resources"].pop("qos_global", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        facts["qos_global"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
