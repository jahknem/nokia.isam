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

from copy import deepcopy
import debugpy

from ansible.module_utils.six import iteritems
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
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
            "port_type",
            "admin_up",
            "tca_line_threshold_enable",
            "tca_line_threshold_los",
            "tca_line_threshold_fcs",
            "tca_line_threshold_rx_octets",
            "tca_line_threshold_tx_octets",
            "tca_line_threshold_los_day",
            "tca_line_threshold_fcs_day",
            "tca_line_threshold_rx_octets_day",
            "tca_line_threshold_tx_octets_day",
            "mau_type",
            "mau_power",
            "mau_speed_auto_sense",
            "mau_autonegotiate",
            "mau_cap100base_tfd",
            "mau_cap1000base_xfd",
            "mau_cap1000base_tfd",
        ]

        
    def edit_config(self, commands):
        """Wrapper method for `_connection.edit_config()`
        This exists solely to allow the unit test framework to mock device connection calls.
        """
        return self._connection.edit_config(commands)

    def execute_module(self):
        """ Execute the module

        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        wantd = {entry['if_index']: entry for entry in self.want}
        haved = {entry['if_index']: entry for entry in self.have}

        # if not debugpy.is_client_connected():
        #     debugpy.listen(("localhost",3000))
        #     debugpy.wait_for_client()
        # debugpy.breakpoint()

        # if state is merged, merge want onto have and then compare
        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        # if state is deleted, empty out wantd and set haved to wantd
        if self.state == "deleted":
            haved = {
                k: v for k, v in iteritems(haved) if k in wantd or not wantd
            }
            wantd = {}

        # remove superfluous config for overridden and deleted
        if self.state in ["overridden", "deleted"]:
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
        self.compare(parsers=self.parsers, want=want, have=have)
