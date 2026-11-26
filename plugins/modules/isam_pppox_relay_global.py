#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_pppox_relay_global
short_description: Manages the system-wide PPPoX cross-connect session settings of Nokia ISAM.
description:
  - Manages C(configure pppox-relay cross-connect global-session) on Nokia ISAM devices (system-wide parameters that apply to all PPP sessions).
  - Requires operator pppoe privileges.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure pppox-relay cross-connect global-session).
  - The output without C(detail) omits defaults; an absent attribute is at its device default and is not reported in facts.
  - Cross-connect engines and client ports (C(configure pppox-relay cross-connect engine|client-port)) are not managed by this module.
options:
  config:
    description: Settings of C(configure pppox-relay cross-connect global-session).
    type: dict
    suboptions:
      pado_timeout:
        description:
          - Timeout for the PADO message in seconds (C(pado-timeout)), range 1-60. Device default C(3).
        type: int
      pads_timeout:
        description:
          - Timeout for the PADS message in seconds (C(pads-timeout)), range 1-60. Device default C(3).
        type: int
      max_pad_attempts:
        description:
          - Maximum number of PADR messages (C(max-pad-attempts)), range 1-16. Device default C(10).
        type: int
      trans_max_age:
        description:
          - Maximum age of a PPP transaction in seconds (C(trans-max-age)), range 1-300. Device default C(300).
        type: int
      cc_max_age:
        description:
          - Maximum age of a PPP cross-connection in seconds (C(cc-max-age)), range 10-3000. Device default C(300).
        type: int
  running_config:
    description:
      - 'Native C(info configure pppox-relay cross-connect global-session flat) output to parse with I(state=parsed).'
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
- name: Configure pppox-relay cross-connect global-session
  nokia.isam.isam_pppox_relay_global:
    config:
      pado_timeout: 5
      max_pad_attempts: 4
    state: merged

# commands:
# - configure pppox-relay cross-connect global-session pado-timeout 5 max-pad-attempts 4

- name: Reset to the device defaults
  nokia.isam.isam_pppox_relay_global:
    state: deleted

# commands (only attributes that are not at their default):
# - configure pppox-relay cross-connect global-session no pado-timeout no max-pad-attempts

- name: Parse device output
  nokia.isam.isam_pppox_relay_global:
    running_config: |
      configure pppox-relay cross-connect global-session pado-timeout 5 no pads-timeout max-pad-attempts 4 no trans-max-age no cc-max-age
    state: parsed

# parsed:
#   pado_timeout: 5
#   max_pad_attempts: 4
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
    - configure pppox-relay cross-connect global-session pado-timeout 5 max-pad-attempts 4
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pppox_relay_global.pppox_relay_global import (
    Pppox_relay_globalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pppox_relay_global.pppox_relay_global import (
    Pppox_relay_global,
)


def main():
    module = AnsibleModule(
        argument_spec=Pppox_relay_globalArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Pppox_relay_global(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
