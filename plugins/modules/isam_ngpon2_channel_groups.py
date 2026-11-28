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
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)
read_outcomes:
  description:
    - Sanitized per-instance read outcomes for a targeted read (I(state) is C(gathered)
      and I(config) names instances).
    - Each outcome names the config section that addressed the instance (for example
      C(config)) and the selector -- the instance identity, a composite identity
      recorded joined by C(/). Instances in different sections that share an identity
      value are different instances and are reported separately.
    - Each outcome records the command axis (C(ok), C(rejected) or C(failed)) and the
      instance-existence axis (C(present), C(confirmed_absent) or C(unknown)).
    - Only C(confirmed_absent) is evidence the instance is gone -- the device's explicit
      "instance does not exist" about that instance, or a header-only reply to its
      C(flat detail) read (which prints every existing instance, also one with defaults
      only). C(unknown) (an invalid-token rejection, a missing dependency, another
      instance's line, a setting whose reads never show it, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(failed) or C(unverified)) is reported at resource level under
      C(parse); C(failed) means the family parser could not process the reply,
      C(unverified) that no parser records its coverage of the reply (a read never claims
      a complete parse).
    - A named instance the device rejected (C(invalid token)) is missing from C(gathered)
      exactly like an absent one; the module also warns, naming the rejected selectors.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
  type: list
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: list
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ngpon2_channel_groups.ngpon2_channel_groups import Ngpon2_channel_groupsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Ngpon2_channel_groups


def main():
    module = AnsibleModule(argument_spec=Ngpon2_channel_groupsArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Ngpon2_channel_groups(module).execute_module())

if __name__ == "__main__": main()
