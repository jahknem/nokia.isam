#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_nat
short_description: Manages the NAPT table aging time of Nokia ISAM.
description:
  - Manages C(configure nat) on Nokia ISAM devices (NAPT aging-time configuration).
  - Requires operator xdsl privileges.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure nat).
  - The output without C(detail) omits defaults; an absent attribute is at its device default and is not reported in facts.
options:
  config:
    description: Settings of C(configure nat).
    type: dict
    suboptions:
      aging_time:
        description:
          - Aging time of a NAPT record in seconds (C(aging-time)), range 60-240. Device default C(120).
        type: int
  running_config:
    description:
      - Native C(info configure nat flat) output to parse with I(state=parsed).
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
- name: Configure nat
  nokia.isam.isam_nat:
    config:
      aging_time: 180
    state: merged

# commands:
# - configure nat aging-time 180

- name: Reset to the device defaults
  nokia.isam.isam_nat:
    state: deleted

# commands (only attributes that are not at their default):
# - configure nat no aging-time

- name: Parse device output
  nokia.isam.isam_nat:
    running_config: |
      configure nat aging-time 180
    state: parsed

# parsed:
#   aging_time: 180
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
    - configure nat aging-time 180
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.nat.nat import (
    NatArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.nat.nat import (
    Nat,
)


def main():
    module = AnsibleModule(
        argument_spec=NatArgs.argument_spec,
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
    result = Nat(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
