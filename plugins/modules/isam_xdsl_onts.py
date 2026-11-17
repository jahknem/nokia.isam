#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_onts
short_description: Manages xDSL settings of Nokia ISAM ONTs.
description:
  - Manages C(configure xdsl ont interface <ont>) on Nokia ISAM devices, the xDSL
    settings of an ONT (for example its downstream power back-off profile).
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure xdsl ont).
  - The xDSL interface node exists with its ONT (see M(nokia.isam.isam_equipment_onts)) and is not
    created or removed by this module. C(deleted) and C(overridden) reset its attributes to the
    device defaults (C(no <attribute>)).
options:
  config:
    description: List of ONTs with their xDSL settings.
    type: list
    elements: dict
    suboptions:
      ont_idx:
        type: str
        required: true
        description: ONT index, for example C(1/1/2/1/1).
      dpbo_profile:
        type: str
        description:
          - Downstream power back-off profile (C(dpbo-profile)), an index of
            M(nokia.isam.isam_xdsl_profiles) I(dpbo_profiles). Unset means no profile.
  running_config:
    description:
      - Native C(info configure xdsl ont flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(ont_idx) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
      - C(deleted) resets the named ONTs (all ONTs without I(config)).
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
- name: Assign a DPBO profile to an ONT
  nokia.isam.isam_xdsl_onts:
    config:
      - ont_idx: 1/1/2/1/1
        dpbo_profile: "1"
    state: merged

# commands:
# - configure xdsl ont interface 1/1/2/1/1 dpbo-profile 1

- name: Read only the named ONTs (targeted gathering)
  nokia.isam.isam_xdsl_onts:
    config:
      - ont_idx: 1/1/2/1/1
    state: gathered

- name: Remove the DPBO profile of an ONT
  nokia.isam.isam_xdsl_onts:
    config:
      - ont_idx: 1/1/2/1/1
    state: deleted

# commands:
# - configure xdsl ont interface 1/1/2/1/1 no dpbo-profile
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - configure xdsl ont interface 1/1/2/1/1 dpbo-profile 1
rendered:
  description: The provided configuration in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_onts.xdsl_onts import (
    Xdsl_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_onts.xdsl_onts import (
    Xdsl_onts,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_ontsArgs.argument_spec,
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
    result = Xdsl_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
