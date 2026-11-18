#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_mcast_general
short_description: Manage Nokia ISAM multicast general configuration.
description:
  - Manages C(configure mcast general) and C(configure mcast capacity) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided multicast general configuration.
    type: dict
    suboptions:
      admin_state:
        description: Enable or disable multicast general admin state.
        type: bool
      forward_method:
        description: Multicast forward method.
        type: str
      fast_change:
        description:
          - Enable or disable multicast fast channel change (C(fast-change)).
          - When enabled on the device, C(replaced) and C(overridden) without it, and C(deleted), reset it
            with C(configure mcast general no fast-change).
        type: bool
      pkg_memb_bitmap:
        description:
          - Fast channel change package membership bitmap (C(configure mcast general pkg-memb-bitmap <value>)),
            value as printed by the device.
          - The device default (C(no pkg-memb-bitmap)) is not reported. I(state=replaced), I(state=overridden)
            and I(state=deleted) reset it with C(configure mcast general no pkg-memb-bitmap).
          - Set and reset forms follow the C(info configure detail flat) output and are not yet verified on a device.
        type: str
      max_bitrate:
        description:
          - Fast channel change maximum bit rate (C(configure mcast general max-bitrate <value>)).
          - The device default (C(no max-bitrate)) is not reported; reset with C(configure mcast general no max-bitrate)
            (not yet verified on a device).
        type: int
      mean_bit_rate:
        description:
          - Fast channel change mean bit rate (C(configure mcast general mean-bit-rate <value>)).
          - The device default (C(no mean-bit-rate)) is not reported; reset with C(configure mcast general no mean-bit-rate)
            (not yet verified on a device).
        type: int
      package_member:
        description: Multicast package membership as printed by the device (C(package-member)).
        type: str
      capacity:
        description:
          - Multicast capacity (C(configure mcast capacity)), set and reset (C(no <attribute>)) in place.
          - Values at the device default are not reported in facts.
          - C(merged) sets the given values, C(replaced) and C(overridden) also reset the omitted capacity
            attributes, C(deleted) resets all capacity attributes.
        type: dict
        suboptions:
          max_num_group:
            description:
              - Maximum number of groups the system (per LT) supports in enough bandwidth (C(max-num-group)),
                range 0-2048. Device default C(1024).
            type: int
          max_num_uncfg:
            description:
              - Maximum number of unconfigured groups the system (per LT) supports in enough bandwidth
                (C(max-num-uncfg)), range 0-2048. Device default C(64).
            type: int
          cfg_res_time:
            description:
              - Time in seconds to reserve the unused guaranteed configured groups (C(cfg-res-time)).
                Device default C(125).
            type: int
          uncfg_res_time:
            description:
              - Time in seconds to reserve the unused unconfigured groups (C(uncfg-res-time)).
                Device default C(0).
            type: int
  running_config:
    description:
      - Device native configuration to parse (C(info configure mcast general flat) and
        C(info configure mcast capacity flat) output).
    type: str
  state:
    description: The state of the configuration after module completion.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather multicast general configuration
  nokia.isam.isam_mcast_general:
    state: gathered

- name: Configure multicast general
  nokia.isam.isam_mcast_general:
    config:
      admin_state: true
      forward_method: proxy
    state: merged

- name: Configure multicast capacity
  nokia.isam.isam_mcast_general:
    config:
      capacity:
        max_num_group: 512
        cfg_res_time: 60
    state: merged

# commands:
# - configure mcast capacity max-num-group 512 cfg-res-time 60
"""

RETURN = """
before:
  description: The configuration as structured data before module invocation.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.mcast_general.mcast_general import (
    Mcast_generalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.mcast_general.mcast_general import (
    Mcast_general,
)


def main():
    module = AnsibleModule(
        argument_spec=Mcast_generalArgs.argument_spec,
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

    result = Mcast_general(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
