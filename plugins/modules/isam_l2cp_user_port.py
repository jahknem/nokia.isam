#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_l2cp_user_port
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_l2cp_user_port
short_description: Manages Nokia ISAM L2CP user ports.
description:
  - Manages C(configure l2cp user-port <port> partition-id) on Nokia ISAM.
  - The write states read C(info configure l2cp user-port flat) and compare against it; a device error fails the module.
  - The removal form C(no user-port <port> partition-id <id>) needs the assigned id, which is taken from the device.
    With I(state=replaced) or C(overridden) a different assigned partition is removed before the new one is set.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: L2CP user ports.
    type: list
    elements: dict
    suboptions:
      name:
        description: User port (e.g. 1/1/7/3).
        type: str
        required: true
      partition_id:
        description: Partition identifier (unset deletes it).
        type: str
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
  nokia.isam.isam_l2cp_user_port:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_l2cp_user_port:
    config:
      - name: 1/1/7/3
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp_user_port.l2cp_user_port import L2cpUserPortArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp_user_port.l2cp_user_port import L2cpUserPort


def main():
    module = AnsibleModule(argument_spec=L2cpUserPortArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**L2cpUserPort(module).execute_module())


if __name__ == "__main__":
    main()
