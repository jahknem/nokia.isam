#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_cwmp_plt
short_description: Manages the CWMP platform (NAT function) of Nokia ISAM.
description:
  - Manages C(configure cwmp plt) on Nokia ISAM devices (CWMP platform configuration).
  - Requires operator xdsl privileges.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure cwmp plt).
  - The output without C(detail) omits defaults; an absent attribute is at its device default and is not reported in facts.
options:
  config:
    description: Settings of C(configure cwmp plt).
    type: dict
    suboptions:
      admin_state:
        description:
          - Administrative state of the CWMP platform (C(adminstate)). Device default C(locked).
        type: str
        choices: [unlocked, locked]
  running_config:
    description:
      - 'Native C(info configure cwmp plt flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
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
- name: Configure cwmp plt
  nokia.isam.isam_cwmp_plt:
    config:
      admin_state: unlocked
    state: merged

# commands:
# - configure cwmp plt adminstate unlocked

- name: Reset to the device defaults
  nokia.isam.isam_cwmp_plt:
    state: deleted

# commands (only attributes that are not at their default):
# - configure cwmp plt no adminstate

- name: Parse device output
  nokia.isam.isam_cwmp_plt:
    running_config: |
      configure cwmp plt adminstate unlocked
    state: parsed

# parsed:
#   admin_state: unlocked
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
    - configure cwmp plt adminstate unlocked
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.cwmp_plt.cwmp_plt import (
    Cwmp_pltArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.cwmp_plt.cwmp_plt import (
    Cwmp_plt,
)


def main():
    module = AnsibleModule(
        argument_spec=Cwmp_pltArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Cwmp_plt(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
