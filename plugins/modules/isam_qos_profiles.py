#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_qos_profiles
version_added: 1.0.0
short_description: Manage QoS profiles on Nokia ISAM devices
description:
- Manage initial support for C(configure qos profiles) on Nokia ISAM devices.
- The module supports live-observed profile identities and common scalar fields.
- Complex nested profile data can be supplied as raw strings in C(attributes).
author: Jan Kuehnemund
notes:
- Tested against read-only output from Nokia ISAM 6.2.04ng.
options:
  config:
    type: list
    elements: dict
    description: QoS profile entries.
    suboptions:
      profile_type:
        type: str
        required: true
        choices: [queue, scheduler-node, cac, marker-d1p, policer, session, aggrqueuesconfig, shaper, bandwidth, ingress-qos, rate-limit]
      name:
        type: str
        required: true
      attributes:
        type: list
        elements: str
        description: Raw profile subcommands for complex or not-yet-modeled nested values.
  running_config:
    type: str
    description: Output from C(info configure qos profiles), used with state C(parsed).
  state:
    type: str
    default: merged
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
"""

EXAMPLES = """
- name: Gather QoS profiles
  nokia.isam.isam_qos_profiles:
    state: gathered

- name: Render a queue profile
  nokia.isam.isam_qos_profiles:
    state: rendered
    config:
      - profile_type: queue
        name: FD_BEQ
        queue-type: red:24:48:80
"""

RETURN = """
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
after:
  description: Configuration after module execution.
  returned: when changed
  type: list
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured QoS profile data.
  returned: when state is gathered
  type: list
parsed:
  description: Parsed structured QoS profile data.
  returned: when state is parsed
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_profiles.qos_profiles import (
    Qos_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_profiles.qos_profiles import (
    Qos_profiles,
)


def main():
    module = AnsibleModule(
        argument_spec=Qos_profilesArgs.argument_spec,
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
    result = Qos_profiles(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
