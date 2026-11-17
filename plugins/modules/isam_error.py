#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_error
short_description: Manages the error log settings of Nokia ISAM.
description:
  - Manages C(configure error) on Nokia ISAM devices (error log configuration).
  - Requires operator alarm privileges.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure error).
  - The output without C(detail) omits defaults; an absent attribute is at its device default and is not reported in facts.
options:
  config:
    description: Settings of C(configure error).
    type: dict
    suboptions:
      log_full_action:
        description:
          - Action when the error log buffer is full (C(log-full-action)); C(wrap) overwrites older records, C(halt) stops logging until the buffer is reset. Device default C(wrap).
        type: str
        choices: [wrap, halt]
  running_config:
    description:
      - Native C(info configure error flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - This is a single settings block without instance lists; C(gathered) always reads it completely.
      - Nothing can be removed. C(deleted) resets all attributes to the device defaults (C(no <attribute>));
        C(replaced) and C(overridden) reset the attributes omitted from I(config).
    type: str
    choices:
      - merged
      - replaced
      - overridden
      - deleted
      - gathered
      - rendered
      - parsed
    default: merged
"""

EXAMPLES = """
- name: Configure error
  nokia.isam.isam_error:
    config:
      log_full_action: halt
    state: merged

# commands:
# - configure error log-full-action halt

- name: Reset to the device defaults
  nokia.isam.isam_error:
    state: deleted

# commands (only attributes that are not at their default):
# - configure error no log-full-action

- name: Parse device output
  nokia.isam.isam_error:
    running_config: |
      configure error log-full-action halt
    state: parsed

# parsed:
#   log_full_action: halt
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - configure error log-full-action halt
rendered:
  description: The provided configuration in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.error.error import (
    ErrorArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.error.error import (
    Error,
)


def main():
    module = AnsibleModule(
        argument_spec=ErrorArgs.argument_spec,
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
    result = Error(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
