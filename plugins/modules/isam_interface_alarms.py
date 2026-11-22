#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_interface_alarms
short_description: Resource module to configure interface alarm default severity
description:
  - Manages C(configure interface alarm) default severity settings on Nokia ISAM devices.
version_added: 0.3.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Interface alarm configurations.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description:
          - Resource identifier (index of the IANA ifType).
      default_severity:
        type: str
        choices: [indeterminate, warning, minor, major, critical]
        description:
          - Default severity to be reported with default value "major".
          - Alarms below this threshold will not be reported.
  running_config:
    description: Device-native configuration to parse when state is parsed.
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), the device exposes no single-instance read for interface
        alarms, so the whole node is read once and each named alarm is reported in C(read_outcomes)
        as C(present) when the parsed catalog lists it and C(unknown) when it does not
        (C(confirmed_absent) only when the device says the node itself does not exist);
        I(gathered) stays the full catalog. Without I(config) the whole resource is read, as before.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather interface alarms
  nokia.isam.isam_interface_alarms:
    state: gathered


- name: Read only the named alarms (targeted gathering)
  nokia.isam.isam_interface_alarms:
    state: gathered
    config:
      - name: "6"


- name: Set default severity for Ethernet interface alarm
  nokia.isam.isam_interface_alarms:
    config:
      - name: "6"
        default_severity: major
    state: merged
"""

RETURN = """
extends_documentation_fragment: nokia.isam.read_outcomes
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
  returned: when state is rendered
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when state is gathered
  type: list
parsed:
  description: Device-native config parsed into structured data.
  returned: when state is parsed
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interface_alarms.interface_alarms import (
    Interface_alarmsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.interface_alarms.interface_alarms import (
    Interface_alarms,
)


def main():
    module = AnsibleModule(
        argument_spec=Interface_alarmsArgs.argument_spec,
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

    result = Interface_alarms(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
