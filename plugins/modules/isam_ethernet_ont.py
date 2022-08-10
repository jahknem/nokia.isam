#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ethernet_ont
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ethernet_ont
short_description: 'Manages provisioning attributes of isam ONT Ethernet ports.'
description: 'Manages provisioning attributes of isam ONT Ethernet ports.'
version_added: 1.0.0
author: Ansible Network Engineer
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: The provided configuration
    type: list
    elements: dict
    suboptions:
      uni_idx:
        type: str
        description: identification of the uni interface index
      port:
        type: dict
        suboptions:
          pm-collect:
            type: bool
            description: 
            - ethernet port physical layer performance monitoring
            - "default = disable"
      phy:
        type: dict
        suboptions:
          pm:
            type: bool
            description: 
            - physical layer pm collection
            - "default = disable"
      l2:
        type: dict
        suboptions:
          pm-collect-ext:
            type: dict
            suboptions:
              pm-collect:
                type: bool
                description: 
                - indicates whether enable this pm collect for this Ethernet Port
                - "default = disable"
              p-bits:
                type: int
                description: 
                - indicates the number of p-bits to be collected
                - "default = 255"
              vlan-id:
                description: indicates the vlan-id bits of the TCI field are used to filter the PM data collected
                type: int
          pm:
            type: bool
            description: 
            - l2 pm collection
            - "default = disable"
          tca:
            type: bool
            description: 
            - l2 threshold crossing alerts
            - "default = disable"
          dropped-frames-up:
            type: bool
            description: 
            - incoming (upstream) dropped frames threshold
            - "default = disable"
          dropped-frames-dn:
            type: bool
            description: 
            - outgoing (downstream) drooped frames threshold
            - "default = disable"
      cfm:
        type: dict
        suboptions:
          portshut-ais:
            type: bool
            description: 
            - shutdown the corresponding Ethernet port on ONT when receiving DS Y.1731 AIS PDU.
      cust_info:
        type: str
        description:
        - customizable port information
      auto_detect:
        type: str
        description:
        - auto detection configuration
        choices:
        - 10_100baset-auto
        - 10baset-fd
        - 100baset-fd
        - 1000baset-fd
        - auto-basetfd
        - 10gig-fd
        - 2.5gig-fd
        - 5gig-fd
        - 10baset-auto
        - 10baset-hd
        - 100baset-hd
        - 1000baset-hd
        - autobaset-hd
        - 10_100_1000baset-auto
        - 100baset-auto
        - auto
        - 1000baset-auto
      power_control:
        description:
        - power control configuration
        type: bool
      pse-class:
        type: int
        description:
        - power class configuration
        - 'Possible values:'
        - '- 0 : Default output power'
        - '- 1 : Class 0, the output power is 15.4w'
        - '- 2 : Class 1, the output power is 4.0w'
        - '- 3 : Class 2, the output power is 7.0w'
        - '- 4 : Class 3, the output power is 15.4w'
        - '- 5 : Class 4, the output power is 30.0w'
      pse_pw_priority:
        type: str
        description:
        - power supply priority
        - 'Possible values:'
        - '- critical : Prevents overcurrent situations by last disconnecting the ports with critical priority'
        - '- high : Prevents overcurrent situations by disconnecting the ports with high priority'
        - '- low : Prevents overcurrent situations by first disconnecting the ports with lower priority(Default)'
        choices:
        - critical
        - high
        - low
      pwr_override:
        description:
        - configure power shedding
        - 'default: disable'
        type: bool
      lpt_mode:
        description:
        - LinkPassThrough(LPT) mode configuration
        - "- not-supported : ignore and don't send the configuration to ONT"
        - "- enabled : enable the LPT mode on this port"
        - "- disabled : disable the LPT mode on this port"
      admin-state:
        type: bool
        description:
        - 'optional parameter with default value: "disable"'
        - admin state of the port

  state:
    description:
    - The state the configuration should be left in
    type: str
    choices:
    - gathered
    - merged
    - replaced
    - overridden
    - deleted
    default: merged
"""

EXAMPLES = """

"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ethernet_ont.ethernet_ont import (
    Ethernet_ontArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.ethernet_ont.ethernet_ont import (
    Ethernet_ont,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Ethernet_ontArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Ethernet_ont(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
