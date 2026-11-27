#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_epon_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_epon_interfaces
short_description: Manages Nokia ISAM EPON interfaces.
description:
  - Manages C(configure epon interface) on Nokia ISAM.
  - Platforms without EPON support (C(invalid token)) have no instances.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: EPON interfaces.
    type: list
    elements: dict
    suboptions:
      name:
        description: EPON interface (e.g. 1/1/6/3).
        type: str
        required: true
      polling_period:
        description: Polling period.
        type: int
      dba_polling0:
        description: DBA polling value 0.
        type: int
      dba_polling1:
        description: DBA polling value 1.
        type: int
      dba_polling2:
        description: DBA polling value 2.
        type: int
      dba_polling3:
        description: DBA polling value 3.
        type: int
      dba_polling4:
        description: DBA polling value 4.
        type: int
      admin_state:
        description: Administrative state.
        type: str
        choices: [up, down]
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
- name: Gather the whole resource
  nokia.isam.isam_epon_interfaces:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_epon_interfaces:
    config:
      - name: 1/1/6/3
    state: gathered
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.epon_interfaces.epon_interfaces import Epon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Epon_interfaces


def main():
    module = AnsibleModule(argument_spec=Epon_interfacesArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Epon_interfaces(module).execute_module())

if __name__ == "__main__": main()
