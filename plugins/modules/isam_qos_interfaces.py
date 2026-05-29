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
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      scheduler_node:
        type: str
      ingress_profile:
        type: str
      cac_profile:
        type: str
      ext_cac:
        type: str
      ds_queue_sharing:
        type: bool
      us_queue_sharing:
        type: bool
      ds_num_queue:
        type: str
      ds_num_rem_queue:
        type: str
      us_num_queue:
        type: str
      queue_stats_on:
        type: bool
      autoschedule:
        type: bool
      oper_weight:
        type: int
      oper_rate:
        type: int
      us_vlanport_queue:
        type: bool
      dsfld_shaper_prof:
        type: str
      bandwidth_profile:
        type: str
      bandwidth_sharing:
        type: str
      aggr_usq_profile:
        type: str
      aggr_dsq_profile:
        type: str
      gem_sharing:
        type: str
      scheduler_mode:
        type: str
      mc_scheduler_node:
        type: str
      bc_scheduler_node:
        type: str
      ds_schedule_tag:
        type: str
      queue:
        type: list
        elements: dict
        suboptions:
          id:
            type: int
            required: true
          priority:
            type: int
          weight:
            type: int
          oper_weight:
            type: int
          queue_profile:
            type: str
          shaper_profile:
            type: str
      upstream_queue:
        type: list
        elements: dict
        suboptions:
          id:
            type: int
            required: true
          priority:
            type: int
          weight:
            type: int
          bandwidth_profile:
            type: str
          ext_bw:
            type: str
          bandwidth_sharing:
            type: str
          queue_profile:
            type: str
          shaper_profile:
            type: str
      ds_rem_queue:
        type: list
        elements: dict
        suboptions:
          id:
            type: int
            required: true
          priority:
            type: int
          weight:
            type: int
  running_config:
    type: str
  state:
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
  returned: when state is merged, replaced, overridden, deleted
  type: list
after:
  returned: when changed
  type: list
commands:
  returned: always, except when state is gathered
  type: list
gathered:
  returned: when state is gathered
  type: list
rendered:
  returned: when state is rendered
  type: list
parsed:
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
