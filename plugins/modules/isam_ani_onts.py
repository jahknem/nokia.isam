#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_ani_onts
short_description: Resource module to configure ani ont TCA thresholds
description:
  - Manages C(configure ani ont) TCA threshold entries on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against Nokia ISAM 6.2.04ng
  - This module works with connection C(network_cli)
  - Implements CLI command: C(configure ani ont ())
options:
  config:
    description: A list of ani ont TCA threshold configurations.
    type: list
    elements: dict
    suboptions:
      ont_idx:
        type: str
        required: true
        description: The ONT interface index.
      tca_profile:
        type: str
        description: TCA profile name.
      admin_state:
        type: str
        choices: [up, down]
        description: Administrative state of the ANI ONT entry.
  running_config:
    description:
      - This option is used only with state I(parsed).
      - The value of this option should be the output received from the device
        by executing the command C(info configure ani ont).
      - For state I(parsed) active connection to remote host is not required.
    type: str
  state:
    description: The state the configuration should be left in.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather ani ont TCA thresholds
  nokia.isam.isam_ani_onts:
    state: gathered

- name: Merge an ani ont entry
  nokia.isam.isam_ani_onts:
    config:
      - ont_idx: 1/1/1/1/1
        tca_profile: "default"
        admin_state: up
    state: merged
"""

RETURN = """
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ani_onts.ani_onts import (
    Ani_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ani_onts.ani_onts import (
    Ani_onts,
)


def main():
    module = AnsibleModule(
        argument_spec=Ani_ontsArgs.argument_spec,
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

    result = Ani_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
