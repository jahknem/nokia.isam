#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_generic_pon
short_description: Manage generic PON data path integrity threshold.
description:
  - Manages C(configure generic-pon dpinteg-threshold) configuration.
version_added: 1.0.0
author: Ansible Network Engineer
options:
  config:
    description: The provided generic PON configuration.
    type: dict
    suboptions:
      dpinteg_threshold:
        description: Data path integrity threshold value (0-100).
        type: str
  running_config:
    description: Device native configuration to parse.
    type: str
  state:
    description: The state of the configuration after module completion.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather generic PON configuration
  nokia.isam.isam_generic_pon:
    state: gathered

- name: Configure dpinteg-threshold
  nokia.isam.isam_generic_pon:
    config:
      dpinteg_threshold: "50"
    state: merged
"""

RETURN = """
before:
  description: The configuration as structured data before module invocation.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when state is gathered
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.generic_pon.generic_pon import (
    Generic_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.generic_pon.generic_pon import (
    Generic_pon,
)


def main():
    module = AnsibleModule(
        argument_spec=Generic_ponArgs.argument_spec,
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

    result = Generic_pon(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
