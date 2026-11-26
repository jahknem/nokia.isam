#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_system
short_description: Manages system-wide xDSL settings of Nokia ISAM.
description:
  - Manages C(configure xdsl system) on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure xdsl system).
options:
  config:
    description: System-wide xDSL settings.
    type: dict
    suboptions:
      auto_port_reset:
        description: Automatic xDSL port reset (C(configure xdsl system auto-port-reset)).
        type: dict
        suboptions:
          enable:
            type: bool
            description: Enable automatic port reset (C(enable) / C(no enable)). The device default is disabled.
  running_config:
    description:
      - 'Native C(info configure xdsl system flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - This is a single settings block without instance lists; C(gathered) always reads it completely.
      - Nothing can be removed. C(deleted) resets the settings to the device defaults
        (only the nodes named in I(config), all without I(config)); C(overridden) behaves like C(replaced).
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
- name: Enable automatic port reset
  nokia.isam.isam_xdsl_system:
    config:
      auto_port_reset:
        enable: true
    state: merged

# commands:
# - configure xdsl system auto-port-reset enable

- name: Reset to the device defaults
  nokia.isam.isam_xdsl_system:
    state: deleted

# commands:
# - configure xdsl system auto-port-reset no enable
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
    - configure xdsl system auto-port-reset enable
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_system.xdsl_system import (
    Xdsl_systemArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_system.xdsl_system import (
    Xdsl_system,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_systemArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Xdsl_system(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
