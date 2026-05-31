# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The facts class for isam
this file validates each subset of facts and selectively
calls the appropriate facts gathering function
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts import (
    FactsBase,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interfaces.interfaces import InterfacesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.bridges.bridges import BridgesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_line.ethernet_line import Ethernet_lineFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.pon_interfaces.pon_interfaces import Pon_interfacesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ethernet_onts.ethernet_onts import Ethernet_ontsFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts import Equipment_ontsFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_interfaces.qos_interfaces import Qos_interfacesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.isam_equipment.isam_equipment import Isam_equipmentFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlans.vlans import VlansFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_profiles.qos_profiles import Qos_profilesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_lines.xdsl_lines import Xdsl_linesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_profiles.xdsl_profiles import Xdsl_profilesFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.link_agg.link_agg import Link_aggFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ani_onts.ani_onts import Ani_ontsFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xstp.xstp import XstpFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.alarm.alarm import AlarmFacts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.traps.traps import Isam_trapsFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_cages.interface_cages import InterfaceCagesFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ntp_onts.ntp_onts import Ntp_ontsFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_maps.qos_maps import Qos_mapsFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.system.system import Isam_systemFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlan_global.vlan_global import Isam_vlan_globalFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.voice_sip.voice_sip import Isam_voice_sipFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_bonding.xdsl_bonding import Xdsl_bondingFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.dhcp_server.dhcp_server import Isam_dhcp_serverFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.generic_pon.generic_pon import Generic_ponFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.iphost.iphost import IphostFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.li_vlan.li_vlan import Li_vlanFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.multicast.multicast import MulticastFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.mcast_general.mcast_general import Mcast_generalFactsfrom ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.software_mngt.software_mngt import Software_mngtFacts

FACT_LEGACY_SUBSETS = {}
FACT_RESOURCE_SUBSETS = dict(
    interfaces=InterfacesFacts,
    bridges=BridgesFacts,
    ethernet_line=Ethernet_lineFacts,
    pon_interfaces=Pon_interfacesFacts,
    ethernet_onts=Ethernet_ontsFacts,
    equipment_onts=Equipment_ontsFacts,
    qos_interfaces=Qos_interfacesFacts,
    isam_equipment=Isam_equipmentFacts,
    vlans=VlansFacts,
    qos_profiles=Qos_profilesFacts,
    xdsl_lines=Xdsl_linesFacts,
    xdsl_profiles=Xdsl_profilesFacts,
    link_agg=Link_aggFacts,
    ani_onts=Ani_ontsFacts,
    xstp=XstpFacts,
    alarm=AlarmFacts,
    isam_traps=Isam_trapsFacts,    interface_cages=InterfaceCagesFacts,)    ntp_onts=Ntp_ontsFacts,    qos_maps=Qos_mapsFacts,)    system=Isam_systemFacts,    isam_vlan_global=Isam_vlan_globalFacts,)    voice_sip=Isam_voice_sipFacts,    xdsl_bonding=Xdsl_bondingFacts,)    isam_dhcp_server=Isam_dhcp_serverFacts,    generic_pon=Generic_ponFacts,)    iphost=IphostFacts,    li_vlan=Li_vlanFacts,)    multicast=MulticastFacts,    mcast_general=Mcast_generalFacts,)    software_mngt=Software_mngtFacts,
)

class Facts(FactsBase):
    """ The fact class for isam
    """

    VALID_LEGACY_GATHER_SUBSETS = frozenset(FACT_LEGACY_SUBSETS.keys())
    VALID_RESOURCE_SUBSETS = frozenset(FACT_RESOURCE_SUBSETS.keys())

    def __init__(self, module):
        super(Facts, self).__init__(module)

    def get_facts(self, legacy_facts_type=None, resource_facts_type=None, data=None):
        """ Collect the facts for isam

        :param legacy_facts_type: List of legacy facts types
        :param resource_facts_type: List of resource fact types
        :param data: previously collected conf
        :rtype: dict
        :return: the facts gathered
        """
        if self.VALID_RESOURCE_SUBSETS:
            self.get_network_resources_facts(FACT_RESOURCE_SUBSETS, resource_facts_type, data)

        if self.VALID_LEGACY_GATHER_SUBSETS:
            self.get_network_legacy_facts(FACT_LEGACY_SUBSETS, legacy_facts_type)

        return self.ansible_facts, self._warnings
