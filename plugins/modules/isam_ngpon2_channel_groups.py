#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ngpon2_channel_groups
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ngpon2_channel_groups
short_description: Manages Nokia ISAM NG-PON2 channel groups.
description:
  - Manages C(configure channel-group id) and its subchannel groups on Nokia ISAM.
  - Platforms without NG-PON2 support (C(invalid token)) have no instances.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Channel groups.
    type: list
    elements: dict
    suboptions:
      id:
        description: Channel group identifier.
        type: int
        required: true
      name:
        description: Channel group name.
        type: str
      polling_period:
        description: Polling period.
        type: int
      raman_reduct:
        description: Raman reduction.
        type: str
      ng2sys_id:
        description: NG-PON2 system identifier.
        type: str
      admin_state:
        description: Administrative state.
        type: str
        choices: [up, down]
      channel_pairs:
        description: Channel pairs of the group.
        type: list
        elements: str
      subchannel_groups:
        description: Subchannel groups (read together with their channel group).
        type: list
        elements: dict
        suboptions:
          id:
            description: Subchannel group identifier.
            type: int
            required: true
          name:
            description: Subchannel group name.
            type: str
          auth_method:
            description: Authentication method.
            type: str
          mcast_encrypt:
            description: Multicast encryption.
            type: str
          fec_dn:
            description: Downstream FEC.
            type: str
          closest_ont:
            description: Distance of the closest ONT.
            type: int
          diff_reach:
            description: Differential reach.
            type: int
          admin_state:
            description: Administrative state.
            type: str
            choices: [up, down]
          cpi:
            description: Channel partition index.
            type: str
          channel_pairs:
            description: Channel pairs of the subchannel group.
            type: list
            elements: str
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
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
  nokia.isam.isam_ngpon2_channel_groups:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_ngpon2_channel_groups:
    config:
      - id: 1
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ngpon2_channel_groups.ngpon2_channel_groups import Ngpon2_channel_groupsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Ngpon2_channel_groups


def main():
    module = AnsibleModule(argument_spec=Ngpon2_channel_groupsArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Ngpon2_channel_groups(module).execute_module())

if __name__ == "__main__": main()
