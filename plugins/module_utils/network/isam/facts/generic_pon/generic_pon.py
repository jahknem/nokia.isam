# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import (
    Generic_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import iter_cli_fields
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    GENERIC_PON_NODES,
    Generic_ponTemplate,
    without_defaults,
)


class Generic_ponFacts(object):
    """The isam generic_pon facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Generic_ponArgs.argument_spec

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}
        if data is None:
            data = connection.get("info configure generic-pon flat")
        parser = Generic_ponTemplate(lines=self._split_packed_lines(unwrap_response(data)), module=self._module)
        params = utils.remove_empties(parser.validate_config(self.argument_spec, {"config": parser.parse()},
                                                             redact=self._module is not None)) or {}
        ansible_facts["ansible_network_resources"].pop("generic_pon", None)
        facts["generic_pon"] = without_defaults(params.get("config") or {})
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    @staticmethod
    def _split_packed_lines(data):
        """One line per attribute, 'configure generic-pon <node> [no] <kw> [<value>]'."""
        nodes = sorted(((node, attrs) for _path, node, attrs in GENERIC_PON_NODES), key=lambda n: -len(n[0]))
        result = []
        for raw_line in str(data or "").splitlines():
            line = raw_line.strip()
            if line.startswith("configure generic-pon dpinteg-threshold "):
                result.append(line)
                continue
            for node, attrs in nodes:
                prefix = "configure generic-pon %s " % node
                if line.startswith(prefix):
                    keywords = [cli for _option, cli, _kind, _default in attrs]
                    for negate, key, value in iter_cli_fields(line[len(prefix):].split(), value_fields=keywords):
                        result.append(" ".join(w for w in (prefix.strip(), "no" if negate else "", key, value or "") if w))
                    break
        return result

