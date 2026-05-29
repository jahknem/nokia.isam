#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_qos_interfaces
short_description: Manages Nokia ISAM QoS interface attributes.
description:
  - Manages an initial safe subset of C(configure qos interface).
  - Covers live-observed interface profile bindings, queue profile bindings,
    upstream bandwidth profile/sharing bindings, and simple queue priority and weight fields.
  - The full Nokia QoS interface grammar is large; unsupported fields are intentionally not rendered.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: QoS interface configuration entries.
    type: list
    elements: dict
    suboptions:
      name:
        description: QoS interface identifier.
        type: str
        required: true
      scheduler_node:
        description: Scheduler node profile reference.
        type: str
      ingress_profile:
        description: Ingress QoS profile reference.
        type: str
      cac_profile:
        description: CAC profile reference.
        type: str
      ext_cac:
        description: Extended CAC setting.
        type: str
      ds_queue_sharing:
        description: Downstream queue sharing setting.
        type: bool
      us_queue_sharing:
        description: Upstream queue sharing setting.
        type: bool
      ds_num_queue:
        description: Downstream queue count.
        type: str
      ds_num_rem_queue:
        description: Downstream remote queue count.
        type: str
      us_num_queue:
        description: Upstream queue count.
        type: str
      queue_stats_on:
        description: Queue statistics collection setting.
        type: bool
      autoschedule:
        description: Autoschedule setting.
        type: bool
      oper_weight:
        description: Operational weight.
        type: int
      oper_rate:
        description: Operational rate.
        type: int
      us_vlanport_queue:
        description: Upstream VLAN port queue setting.
        type: bool
      dsfld_shaper_prof:
        description: DS field shaper profile reference.
        type: str
      bandwidth_profile:
        description: Bandwidth profile reference.
        type: str
      bandwidth_sharing:
        description: Bandwidth sharing setting.
        type: str
      aggr_usq_profile:
        description: Aggregate upstream queue profile reference.
        type: str
      aggr_dsq_profile:
        description: Aggregate downstream queue profile reference.
        type: str
      gem_sharing:
        description: GEM sharing setting.
        type: str
      scheduler_mode:
        description: Scheduler mode.
        type: str
      mc_scheduler_node:
        description: Multicast scheduler node reference.
        type: str
      bc_scheduler_node:
        description: Broadcast scheduler node reference.
        type: str
      ds_schedule_tag:
        description: Downstream schedule tag.
        type: str
      queue:
        description: Downstream queue entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Queue identifier.
            type: int
            required: true
          priority:
            description: Queue priority.
            type: int
          weight:
            description: Queue weight.
            type: int
          oper_weight:
            description: Queue operational weight.
            type: int
          queue_profile:
            description: Queue profile reference.
            type: str
          shaper_profile:
            description: Shaper profile reference.
            type: str
      upstream_queue:
        description: Upstream queue entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Queue identifier.
            type: int
            required: true
          priority:
            description: Queue priority.
            type: int
          weight:
            description: Queue weight.
            type: int
          bandwidth_profile:
            description: Bandwidth profile reference.
            type: str
          ext_bw:
            description: Extended bandwidth setting.
            type: str
          bandwidth_sharing:
            description: Bandwidth sharing setting.
            type: str
          queue_profile:
            description: Queue profile reference.
            type: str
          shaper_profile:
            description: Shaper profile reference.
            type: str
      ds_rem_queue:
        description: Downstream remote queue entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Queue identifier.
            type: int
            required: true
          priority:
            description: Queue priority.
            type: int
          weight:
            description: Queue weight.
            type: int
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description: Desired resource state.
    type: str
    default: merged
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
"""

EXAMPLES = """
- nokia.isam.isam_qos_interfaces:
    config:
      - name: 1/1/8/28
        cac_profile: name:FD_Default
        queue:
          - id: 0
            shaper_profile: name:qssShaperDN920Mbps
    state: merged
"""

RETURN = """
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, deleted
  type: list
after:
  description: Configuration after module execution.
  returned: when changed
  type: list
commands:
  description: Commands sent to the device or produced in check mode.
  returned: always, except when state is gathered
  type: list
gathered:
  description: Gathered structured QoS interface data.
  returned: when state is gathered
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
parsed:
  description: Parsed structured QoS interface data.
  returned: when state is parsed
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_interfaces.qos_interfaces import Qos_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_interfaces.qos_interfaces import Qos_interfaces


def main():
    module = AnsibleModule(
        argument_spec=Qos_interfacesArgs.argument_spec,
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

    result = Qos_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
