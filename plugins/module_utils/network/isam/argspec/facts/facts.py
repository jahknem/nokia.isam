# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The arg spec for the isam facts module.
"""


class FactsArgs(object):  # pylint: disable=R0903
    """ The arg spec for the isam facts module
    """

    def __init__(self, **kwargs):
        pass

    choices = [
        'all',
        'alarm',
        'active_alarms',
        'ani_onts',
        'bridges',
        'dhcp_server',
        'equipment_onts',
        'equipment_replan',
        'equipment_status',
        'ethernet_line',
        'ethernet_onts',
        'generic_pon',
        'interface_alarms',
        'interface_cages',
        'interfaces',
        'interface_status',
        'iphost',
        'isam_equipment',
        'isam_dhcp_server',
        'isam_traps',
        'isam_vlan_global',
        'li_vlan',
        'link_agg',
        'mcast_general',
        'igmp',
        'mcast_control',
        'multicast',
        'ntp_onts',
        'ont_status',
        'ont_ranging_status',
        'ont_software_status',
        'pon_interfaces',
        'pon_status',
        'pon_pm_status',
        'qos_interfaces',
        'qos_maps',
        'qos_profiles',
        'software_mngt',
        'software_status',
        'system',
        'vlans',
        'voice_sip',
        'xdsl_boards',
        'xdsl_bonding',
        'xdsl_lines',
        'xdsl_profiles',
        'xstp',
    ]

    argument_spec = {
        'gather_subset': dict(default=['!config'], type='list'),
        'gather_network_resources': dict(choices=choices,
                                          type='list'),
        'gather_configuration': dict(default=False, type='bool'),
        'provider': dict(type='dict', no_log=True),
    }
