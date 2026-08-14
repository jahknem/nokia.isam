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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    Generic_ponTemplate,
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
        data = unwrap_response(data)

        parser = Generic_ponTemplate(lines=self._split_packed_lines(data))
        parsed = parser.parse()

        ansible_facts["ansible_network_resources"].pop("generic_pon", None)
        facts["generic_pon"] = utils.remove_empties(parsed) or {}
        ansible_facts["ansible_network_resources"].update(facts)

        return ansible_facts

    _PACKED_WORDS = {
        "pon-pmcollect", "ont-pmcollect", "ontbulk-pmcollect",
        "slid-mode", "sn-bundle-timer", "sw-ver-mis-block", "sn-autounlock",
        "ponlos-alarm-ctrl", "threshold", "txmcutilhi", "txmcutilmd",
        "txmcutillo", "txtotutilhi", "txtotutilmd", "txtotutillo",
        "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi",
        "dbacongperiodmd", "dbacongperiodlo", "txucdropfrmhi",
        "txucdropfrmmd", "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd",
        "txmcdropfrmlo", "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo",
        "rxtotdropfrmhi", "rxtotdropfrmmd", "rxtotdropfrmlo", "numtcint",
        "numtcintdba", "dbacongthresh",
    }

    def _split_packed_lines(self, data):
        result = []
        for raw_line in str(data or "").splitlines():
            line = raw_line.strip()
            if not line or not line.startswith("configure generic-pon "):
                if line:
                    result.append(line)
                continue
            tokens = line.split()
            starts = [
                index for index, token in enumerate(tokens[3:], 3)
                if (token in self._PACKED_WORDS and (index == 3 or tokens[index - 1] != "no"))
                or (token == "no" and index + 1 < len(tokens) and tokens[index + 1] in self._PACKED_WORDS)
            ]
            if not starts:
                result.append(line)
                continue
            prefix = " ".join(tokens[:3])
            result.extend(
                prefix + " " + " ".join(tokens[start:end])
                for start, end in zip(starts, starts[1:] + [len(tokens)])
            )
        return result
