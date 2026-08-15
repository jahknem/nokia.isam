# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_xdsl_lines config file.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    normalize_resource_keys,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_lines import (
    Xdsl_linesTemplate,
)


class Xdsl_lines(ResourceModule):
    """The isam_xdsl_lines config class."""

    def __init__(self, module):
        super(Xdsl_lines, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="xdsl_lines",
            tmplt=Xdsl_linesTemplate(),
        )
        self.parsers = [
            "service_profile",
            "spectrum_profile",
            "dpbo_profile",
            "vect_profile",
            "rtx_profile",
            "sos_profile",
            "admin_up",
        ]
        self.parsers.extend(
            [
                "carrier_data_mode",
                "transfer_mode",
                "vect_qln_mode",
                "vect_fallback",
                "ansi_t1413",
                "etsi_dts",
                "g992_1_a",
                "g992_1_b",
                "g992_2_a",
                "g992_3_a",
                "g992_3_b",
                "g992_3_aj",
                "g992_3_l1",
                "g992_3_l2",
                "g992_3_am",
                "g992_5_a",
                "g992_5_b",
                "ansi_t1_424",
                "etsi_ts",
                "itu_g993_1",
                "ieee_802_3ah",
                "g992_5_aj",
                "g992_5_am",
                "g993_2_8a",
                "g993_2_8b",
                "g993_2_8c",
                "g993_2_8d",
                "g993_2_12a",
                "g993_2_12b",
                "g993_2_17a",
                "g993_2_30a",
                "g993_2_35b",
                "imp_noise_sensor",
                "auto_switch",
            ]
        )

    def execute_module(self):
        """Execute the module."""
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """Generate configuration commands from want, have and state."""
        wantd = self._index_by_id(self.want)
        haved = self._index_by_id(self.have)

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        self.compare(parsers=self.parsers, want=want, have=have)

    @staticmethod
    def _index_by_id(data):
        indexed = {}
        for entry in data or []:
            normalized = normalize_resource_keys(entry, aliases=(("if_index", "name"),))

            key = normalized.get("name") or normalized.get("if_index")
            if key:
                indexed[key] = normalized
        return indexed
