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
        initial C(M(!)).
    required: false
    default: ['!all']
    version_added: "2.2"
  gather_network_resources:
    description:
      - Selects configuration/resource facts such as interfaces and vlans.
        Operational status, counters, alarms, and sessions belong in
        C(gather_subset) instead.
        Can specify a list of values to include a larger subset. Values
        can also be used with an initial C(M(!)) to specify that a
        specific subset should not be collected.
    required: false
    version_added: "2.9"
  gather_configuration:
    description:
      - Read the complete flat configuration once and pass it to each selected
        resource parser. This avoids one device request per resource.
    required: false
    default: false
    type: bool
    version_added: "1.1.0"
"""

EXAMPLES = """
# Gather all facts
- isam_facts:
    gather_network_resources: all

# Collect only the interfaces facts
- isam_facts:
    gather_network_resources:
      - interfaces

# Gather operational DHCP relay information
- isam_facts:
    gather_subset:
      - "!all"
      - dhcp_relay

# Do not collect interfaces facts
- isam_facts:
    gather_network_resources:
      - "!interfaces"

# Collect interfaces and minimal default facts
- isam_facts:
    gather_network_resources: interfaces

# Read one complete configuration and reuse it for multiple resource parsers
- isam_facts:
    gather_configuration: true
    gather_network_resources:
      - interfaces
      - pon_interfaces
      - equipment_onts
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
