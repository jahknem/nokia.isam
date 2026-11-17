#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_pon_global
short_description: Manages the system-wide GPON settings of Nokia ISAM.
description:
  - Manages C(configure pon) on Nokia ISAM devices (system-wide GPON settings that apply to all GPON interfaces).
  - Requires operator equipment privileges.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure pon).
  - The output without C(detail) omits defaults; an absent attribute is at its device default and is not reported in facts.
  - Per-interface settings (C(configure pon interface)) belong to M(nokia.isam.isam_pon_interfaces); the read command C(info configure pon flat) also returns those lines, they are ignored here.
options:
  config:
    description: Settings of C(configure pon).
    type: dict
    suboptions:
      pwrbrst_mode:
        description:
          - Power burst detection mode for GPON (C(pwrbrst-mode)). Device default C(disable).
        type: str
        choices: [disable, enable]
      range_mode:
        description:
          - Range mode of all GPON interfaces (C(range-mode)); C(alientolerant) lets ONTs range in the presence of alien ONUs. Device default C(normal).
        type: str
        choices: [normal, alientolerant]
  running_config:
    description:
      - Native C(info configure pon flat) output to parse with I(state=parsed).
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
- name: Configure pon
  nokia.isam.isam_pon_global:
    config:
      range_mode: alientolerant
    state: merged

# commands:
# - configure pon range-mode alientolerant

- name: Reset to the device defaults
  nokia.isam.isam_pon_global:
    state: deleted

# commands (only attributes that are not at their default):
# - configure pon no range-mode

- name: Parse device output
  nokia.isam.isam_pon_global:
    running_config: |
      configure pon no pwrbrst-mode range-mode alientolerant
    state: parsed

# parsed:
#   range_mode: alientolerant
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
    - configure pon range-mode alientolerant
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pon_global.pon_global import (
    Pon_globalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_global.pon_global import (
    Pon_global,
)


def main():
    module = AnsibleModule(
        argument_spec=Pon_globalArgs.argument_spec,
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
    result = Pon_global(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
