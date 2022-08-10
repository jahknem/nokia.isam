#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_bridge_vlans
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_bridge
short_description: 'Manages vlan attributes of isam bridge.'
description: 'This moduel manages all vlans configured for an existing bridge. Bridge must already exist!'
version_added: 1.0.0
author: Ansible Network Engineer
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: The provided configuration
    type: dict
    elements: dict
    suboptions:
      bridge:
        type: string
        description: 
        - Required Identifier of the bridge to be configured.
        required: True
      vlan:
        type: list
        elements: dict
        suboptions:
          vlan_id:
            type: dict
            elements: dict
            suboptions:
              id: 
                type: str
                description: 
                - 'parameter describing which vlan id to be configured. Required if a vlan is to be created.'
              tag:
                type: str
                description:
                - 'optional parameter with default value: "untagged"'
                - 'tag control for egress port'
                choices:
                - 'untagged'
                - 'single-tagged'
                - 'priority-tagged'
              l2fwder_vlan:
                type: str
                description:
                - 'optional parameter with default value: "stacked 0 : 4097"'
                - 'layer2 forwarder vlan id'
              vlan_scope:
                type: str
                description:
                - 'optional parameter with default value: "l2fwder"'
                - 'the vlan scope'
                choices:
                - 'local'
                - 'l2fwder'
                - 'network'
              qos:
                type: str
                description:
                - 'optional parameter with default value: "none"'
                - 'the qos policy'
                default: none
              qos_profile:
                type: str
                description:
                - 'optional parameter with default value: "none"'
                - 'the qos profile'
                default: none
              prior_best_effort:
                type: boolean
                description:
                - 'optional parameter with default value: "none"'
                - 'enable best effort priority (value: 0)'
                default: none
              prior_background:
                type: boolean
                description:
                - 'optional parameter with default value: "none"'
                - 'enable background priority (value: 1)'
                default: none
              prior_spare:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable spare priority (value: 2)'
              prior_exc_effort:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable excellen effort priority (value: 3)'
              prior_ctrl_load:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable controlled load priority (value: 4)'
              prior_less_100ms:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable less than 100ms latency and jitter priority (value: 5)'
              prior_less_10ms:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable less than 10ms latency and jitter priority (value: 6)'
              prior_nw_ctrl:
                type: boolean
                description:
                - 'optional parameter'
                - 'enable network controlled priority (value: 7)'
              in_qos_prof_name:
                type: str
                description:
                - 'optional parameter with default value: "name: Default_TC0"'
                - 'the input qos profile name'
              max_up_qos_policy:
                type: int
                description:
                - 'optional parameter with default value: "0"'
                - 'the maximum number of qos policy numbers on a VLAn port basis'
              max_ip_antispoof:
                type: int
                description:
                - 'optional parameter with default value: "65335"'
                - 'the maximum number of ip address number in IP antispoofing and/or ARP relay'
              max_unicast_mac:
                type: int
                description:
                - 'optional parameter with default value: "65535"'
                - 'the maximum number of uncommited unicast macs adresses'
              max_ipv6_antispf:
                type: int
                description:
                - 'optional parameter with default value: "65335"'
                - 'the maximum number of ipv6 address number in IP antispoofing and/or ARP relay'
              mac_learn_ctrl:
                type: int
                description:
                - 'optional parameter with default value: "3"'
                - 'MAC address learned control up(1), down(2), inherit from bridgedPort(3)'
              min_cvlan_id:
                type: int
                description:
                - 'optional parameter with default value: "1"'
                - 'This object configures the lower boundary of CVLAN range for protocol awareness for S-VLAN cross-connect(Tunnel)'
              max_cvlan_id:
                type: int
                description:
                - 'optional parameter with default value: "4095"'
                - This object configures the upper boundary of CVLAN range for protocol awareness for S-VLAN cross-connect(Tunnel)
              ds_dedicated_q:
                type: bool
                description: 
                - 'optional parameter with default value: "disable"'
              tpid:
                type: str
                description:
                - 'optional parameter with default value: "8100"'
                - 'This object configures vlan port tpid in hex values'
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
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.bridge_vlans.bridge_vlans import (
    Bridge_vlansArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.bridge_vlans.bridge_vlans import (
    Bridge_vlans,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=Bridge_vlansArgs.argument_spec,
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

    result = Bridge_vlans(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
