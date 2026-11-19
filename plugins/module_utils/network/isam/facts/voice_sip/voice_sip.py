# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.voice_sip.voice_sip import (
    Isam_voice_sipArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    parse_lines,
    without_defaults,
)


class Isam_voice_sipFacts(object):
    """The isam voice sip facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Isam_voice_sipArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the instances named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "voice_sip", "info configure voice sip flat", {
            "cas_nsm_prof": "info configure voice sip cas-nsm-prof %s flat",
            "lineid_syn_prof": "info configure voice sip lineid-syn-prof %s flat",
            "redundancy": "info configure voice sip redundancy %s flat",
            "redundancy_cmd": "info configure voice sip redundancy-cmd %s flat",
            "register": "info configure voice sip register %s flat",
            "vsp": "info configure voice sip vsp %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        if not data:
            data = self.get_config(connection)
        data = self._flatten_config(unwrap_response(data))
        params = without_defaults(parse_lines("\n".join(data)))
        ansible_facts["ansible_network_resources"].pop("voice_sip", None)
        ansible_facts["ansible_network_resources"]["voice_sip"] = params
        return ansible_facts

    @staticmethod
    def _flatten_config(config):
        flat_config = []
        for raw_line in str(config or "").splitlines():
            line = raw_line.rstrip()
            # Strip comments (# preceded by space, not inside quoted values)
            if " #" in line:
                before = line[:line.index(" #")]
                if before.count('"') % 2 == 0:
                    line = before
            stripped = line.strip()
            if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
                continue
            if line.startswith("configure voice sip "):
                flat_config.append(line)
        return flat_config
