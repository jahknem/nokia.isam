#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""
The module file for isam_facts
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: isam_facts
short_description: Get facts about isam devices.
version_added: "1.0.0"
author: Jan Kühnemund (@jahknem)
description:
  - Collects facts from network devices running the isam operating
    system. This module places the facts gathered in the fact tree keyed by the
    respective resource name. Operational subsets and configuration resources
    are opt-in so a default invocation does not contact the device.
options:
  gather_subset:
    description:
      - Selects read-only operational facts to gather. Use C(!all) followed
        by one or more operational subsets for a focused query. C(all)
        gathers every operational subset. Values can be excluded with an
        initial C(!).
      - 'Operational subsets: C(active_alarms), C(config_tree), C(dhcp_relay),
        C(equipment_status), C(interface_status), C(ont_ranging_status), C(ont_serials),
        C(ont_software_status), C(ont_status), C(pon_pm_status), C(pon_status),
        C(software_status).'
      - C(ont_serials) returns an MSAN-wide ONT serial index under
        C(ansible_net_ont_serials). It issues C(show equipment ont interface),
        which is markedly cheaper than expanding the whole
        C(info configure equipment ont flat) tree, so prefer it when only
        C(ont-idx) to C(sernum) bindings are needed. A device that does not
        implement the command reports a warning; callers that depend on the
        index for a safety decision must treat a missing index as a failure
        rather than as "no ONTs configured".
    type: list
    elements: str
    default: ['!all']
  gather_network_resources:
    description:
      - Selects configuration/resource facts such as interfaces and vlans.
        Operational status, counters, alarms, and sessions belong in
        I(gather_subset) instead.
      - C(all) selects every resource. A value with an initial C(!) excludes that
        resource; a list of exclusions only (for example C(!interfaces)) selects every
        other resource, like C([all, "!interfaces"]).
      - 'Resources: C(alarm), C(ani_onts), C(bridges), C(dhcp_server), C(equipment_onts), C(equipment_replan), C(ethernet_line), C(ethernet_onts), C(generic_pon), C(interface_alarms), C(interface_cages), C(interfaces), C(iphost), C(isam_equipment), C(isam_dhcp_server), C(isam_dhcp_relay), C(isam_arp_relay), C(isam_cfm), C(efm_oam_interface), C(isam_ipv6_antispoofing_slot), C(isam_dist_service), C(l2cp), C(l2cp_session), C(l2cp_user_port), C(linetest), C(ngpon2_channel_groups), C(epon_interfaces), C(channel_pair_pm), C(isam_traps), C(isam_vlan_global), C(li_vlan), C(link_agg), C(mcast_general), C(igmp), C(mcast_control), C(multicast), C(ntp_onts), C(pon_interfaces), C(qos_global), C(cwmp_plt), C(error), C(nat), C(pon_global), C(pppox_relay_global), C(trouble_shooting_pon), C(qos_interfaces), C(qos_maps), C(qos_profiles), C(qos_tca), C(xdsl_inm), C(xdsl_onts), C(xdsl_system), C(l2uni_onts), C(uni_onts), C(software_mngt), C(system), C(isam_system_security), C(vlans), C(voice_sip), C(xdsl_boards), C(xdsl_bonding), C(xdsl_lines), C(xdsl_profiles), C(xstp).'
      - Unknown names fail the module (validated by the facts class, so that exclusions
        are accepted).
    type: list
    elements: str
  gather_configuration:
    description:
      - Read the access-side flat configuration once and pass it to each selected
        resource parser. This avoids one device request per resource.
      - On evidenced firmware this source omits IHUB port, LAG and service configuration.
        The explicit read-only IHUB family modules use separate hierarchical sources.
    default: false
    type: bool
  config_tree_detail:
    description:
      - With the C(config_tree) subset, read C(info configure detail flat) instead of
        C(info configure flat). Detail also prints unset defaults and is several
        times larger. This expands the raw snapshot, not proven modeled coverage.
        The default (non-detail) is the configured content.
      - The root tree masks secret values and strips C(encrypted:) credentials from
        paths, attributes and stored CLI lines. Only device-masked placeholders such
        as C(plain:******) are retained. Leaves contain C(attrs), C(lines), C(node)
        and C(source); this view is lossless except for credential redaction.
        C(source) is C(grammar), C(resource) (resource-backed CLI metadata), or
        C(unclassified). Unknown paths are retained under C(__unclassified__)
        without guessed nesting. Unknown attribute tails are preserved in
        C(unparsed); they are never inferred as fields or child nodes.
      - C(ansible_net_config_tree_source) records the flat source and its known IHUB
        omissions. Lossless input parsing is not a whole-device completeness claim.
    default: false
    type: bool
    version_added: "1.0.0"
"""

EXAMPLES = """
- name: Gather all resource facts
  nokia.isam.isam_facts:
    gather_network_resources: all

- name: Collect only the interfaces facts
  nokia.isam.isam_facts:
    gather_network_resources:
      - interfaces

- name: Gather operational DHCP relay information
  nokia.isam.isam_facts:
    gather_subset:
      - "!all"
      - dhcp_relay

- name: Collect every resource except interfaces
  nokia.isam.isam_facts:
    gather_network_resources:
      - all
      - "!interfaces"

- name: Read one complete configuration and reuse it for several resource parsers
  nokia.isam.isam_facts:
    gather_configuration: true
    gather_network_resources:
      - interfaces
      - pon_interfaces
      - equipment_onts

# Schema-less: every line is kept, including parts no resource family models yet.
- name: Read the whole configuration as a nested, lossless tree (ansible_net_config_tree)
  nokia.isam.isam_facts:
    gather_subset:
      - "!all"
      - config_tree

- name: The same, including unset defaults (full configurable surface; much larger)
  nokia.isam.isam_facts:
    gather_subset:
      - "!all"
      - config_tree
    config_tree_detail: true
"""

RETURN = """
ansible_facts:
  description: Facts collected from the device.
  returned: always
  type: dict
warnings:
  description: Warnings emitted while collecting facts.
  returned: when warnings are present
  type: list
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.facts.facts import FactsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts


def main():
    """
    Main entry point for module execution

    :returns: ansible_facts
    """
    argument_spec = FactsArgs.argument_spec
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    warnings = []

    result = Facts(module).get_facts()

    ansible_facts, additional_warnings = result
    warnings.extend(additional_warnings)

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()
