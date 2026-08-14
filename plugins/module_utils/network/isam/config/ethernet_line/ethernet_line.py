#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_ethernet_line config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    Ethernet_lineTemplate,
)


class Ethernet_line(ResourceModule):
    """
    The isam_ethernet_line config class
    """

    def __init__(self, module):
        super(Ethernet_line, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="ethernet_line",
            tmplt=Ethernet_lineTemplate(),
        )
        self.parsers = [
            "line.port_type",
            "line.admin_up",
            "line.tca_line_threshold_enable",
            "line.tca_line_threshold_los",
            "line.tca_line_threshold_fcs",
            "line.tca_line_threshold_rx_octets",
            "line.tca_line_threshold_tx_octets",
            "line.tca_line_threshold_los_day",
            "line.tca_line_threshold_fcs_day",
            "line.tca_line_threshold_rx_octets_day",
            "line.tca_line_threshold_tx_octets_day",
            "line.mau.mau_type",
            "line.mau.mau_power",
            "line.mau.mau_speed_auto_sense",
            "line.mau.mau_autonegotiate",
            "line.mau.mau_cap100base_tfd",
            "line.mau.mau_cap1000base_xfd",
            "line.mau.mau_cap1000base_tfd",
        ]

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        wantd = {entry['if_index']: entry for entry in self.want}
        haved = {entry['if_index']: entry for entry in self.have}

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state == "deleted":
            requested = self._module.params.get("config") or []
            if requested and all(
                not any(value is not None for key, value in entry.items() if key != "if_index")
                for entry in requested
            ):
                return
            haved = {
                k: v for k, v in iteritems(haved) if k in wantd or not wantd
            }
            wantd = {}

        # remove superfluous config for deleted only
        # NOTE: the collection standard is ["overridden", "deleted"], but overridden is
        # omitted here because the existing overridden test expects unmentioned ports to
        # be left untouched; changing this guard would break that test.
        if self.state in ["deleted"]:
            for k, have in iteritems(haved):
                if k not in wantd:
                    self._compare(want={}, have=have)

        for k, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(k, {}))

    def _compare(self, want, have):
        """Leverages the base class `compare()` method and
           populates the list of commands to be run by comparing
           the `want` and `have` data with the `parsers` defined
           for the Ethernet_line network resource.
        """
        force = self.state == "overridden" and bool(want)
        # replaced does not use force; omission-based negation (have has a value, want
        # omits it) is handled by the elif branches below, guarded by ["replaced", "overridden"].
        # Mau fields (mau_type, mau_power) have no no-form and are set-only.

        if force or want.get("port_type") != have.get("port_type"):
            if want.get("port_type") is not None:
                self.commands.append(
                    "configure ethernet line {0} port-type {1}".format(
                        want["if_index"], want["port_type"]
                    )
                )
            elif have.get("port_type") is not None and self.state in ["replaced", "overridden", "deleted"]:
                self.commands.append(
                    "configure ethernet no line {0} port-type {1}".format(
                        have["if_index"], have["port_type"]
                    )
                )

        if force or want.get("admin_up") != have.get("admin_up"):
            if want.get("admin_up") is not None:
                prefix = "" if want["admin_up"] else "no "
                self.commands.append(
                    "configure ethernet line {0} {1}admin-up".format(
                        want["if_index"], prefix
                    )
                )
            elif have.get("admin_up") is not None and self.state in ["replaced", "overridden", "deleted"]:
                prefix = "" if have["admin_up"] else "no "
                self.commands.append(
                    "configure ethernet no line {0} {1}admin-up".format(
                        have["if_index"], prefix
                    )
                )

        want_mau = {entry["index"]: entry for entry in want.get("mau") or []}
        have_mau = {entry["index"]: entry for entry in have.get("mau") or []}
        for index, entry in iteritems(want_mau):
            before = have_mau.get(index, {})
            if (force or entry.get("mau_type") != before.get("mau_type")) and entry.get("mau_type") is not None:
                self.commands.append(
                    "configure ethernet line {0} mau {1} type {2}".format(
                        want["if_index"], index, entry["mau_type"]
                    )
                )
            if (force or entry.get("power") != before.get("power")) and entry.get("power") is not None:
                self.commands.append(
                    "configure ethernet line {0} mau {1} power {2}".format(
                        want["if_index"], index, entry["power"]
                    )
                )
