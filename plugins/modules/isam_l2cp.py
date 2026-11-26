#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_l2cp
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_l2cp
short_description: Manages the Nokia ISAM global L2CP partition type.
description:
  - Manages C(configure l2cp partition-type) on Nokia ISAM.
  - A single settings block (one entry named C(l2cp)); C(gathered) always reads it completely.
  - The write states read C(info configure l2cp flat) and compare against it (an empty read means C(no-partition)); a device error fails the module.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The global L2CP settings (one entry).
    type: list
    elements: dict
    suboptions:
      name:
        description: Always C(l2cp).
        type: str
        required: true
      partition_type:
        description: Partition type.
        type: str
        choices: [no-partition, fixed-assigned]
  running_config:
    description:
      - 'Native C(info configure ... flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state the configuration should be left in.
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
  nokia.isam.isam_l2cp:
    state: gathered

- name: Set the partition type
  nokia.isam.isam_l2cp:
    config:
      - name: l2cp
        partition_type: fixed-assigned
    state: merged
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2cp.l2cp import L2cpArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp.l2cp import L2cp


def main():
    module = AnsibleModule(argument_spec=L2cpArgs.argument_spec, required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**L2cp(module).execute_module())


if __name__ == "__main__":
    main()
