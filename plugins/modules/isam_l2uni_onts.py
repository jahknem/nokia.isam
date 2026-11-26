#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_l2uni_onts
short_description: Manages Nokia ISAM ONT L2 UNI performance monitoring and TC-layer thresholds.
description:
  - Manages C(configure l2uni ont performance-monitor <uni>) (including its C(pm-collect-ext) sub-node)
    and C(configure l2uni ont tc-layer-threshold <uni>) on Nokia ISAM.
  - These nodes exist with their ONT UNI; the module sets attributes and resets them to the CLI default
    with C(no <attribute>). It does not create or remove UNIs (see M(nokia.isam.isam_ethernet_onts)).
  - An attribute at its CLI default (shown by the device as C(no <attribute>)) is not reported, like an unset attribute.
    Configuring an attribute with its default value is the same as resetting it.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against the C(info configure l2uni detail flat) output of Nokia ISAM 6.2.04.
  - Attributes changed in one CLI scope (the UNI node, or its C(pm-collect-ext) sub-node) are sent as one command.
options:
  config:
    description: The provided L2 UNI ONT configuration.
    type: dict
    suboptions:
      performance_monitor:
        description: C(configure l2uni ont performance-monitor <uni>) entries.
        type: list
        elements: dict
        suboptions:
          uni_idx:
            type: str
            required: true
            description: ONT UNI index (e.g. C(1/1/2/1/1/1/1)).
          pm_collect:
            type: str
            choices: [none, pm-enable, tca-enable]
            description:
              - Collection of Ethernet traffic performance monitors (C(pm-collect)); device default C(none).
          pm_collect_64bit:
            type: str
            choices: [none, pm-enable]
            description:
              - Collection of 64-bit Ethernet traffic performance monitors (C(pm-collect-64bit)); device default C(none).
          pm_collect_ext:
            type: dict
            description: Extended 32-bit PM collection (C(performance-monitor <uni> pm-collect-ext)).
            suboptions:
              pm_collect:
                type: str
                choices: [enable, disable]
                description: Extended PM collection for this port (C(pm-collect)); device default C(disable).
              p_bits:
                type: int
                description:
                  - P-bits of the TCI used to filter the collected PM data (C(p-bits)), C(0)-C(7);
                    C(255) (0xFF, device default) means not used.
              vlan_id:
                type: int
                description:
                  - VLAN id of the TCI used to filter the collected PM data (C(vlan-id)), C(1)-C(4092);
                    C(0) (device default) means not used.
      tc_layer_threshold:
        description: C(configure l2uni ont tc-layer-threshold <uni>) entries (TC-layer TCA thresholds).
        type: list
        elements: dict
        suboptions:
          uni_idx:
            type: str
            required: true
            description: ONT UNI index (e.g. C(1/1/2/1/1/1/1)).
          dropped_frames_up:
            type: int
            description:
              - TCA threshold for upstream dropped frames (C(dropped-frames-up)), C(0)-C(4294967294);
                C(4294967295) (C(disabled), device default) disables the threshold.
          dropped_frames_dn:
            type: int
            description:
              - TCA threshold for downstream dropped frames (C(dropped-frames-dn)), C(0)-C(4294967294);
                C(4294967295) (C(disabled), device default) disables the threshold.
  running_config:
    description:
      - 'Device configuration to parse with I(state=parsed), as returned by C(info configure l2uni flat) (with or without C(detail)).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - C(merged) sets the given attributes; C(replaced) also resets the unspecified attributes of the given UNIs;
      C(overridden) additionally resets every UNI of the given lists that is not in I(config) (a list missing from
      I(config) is reset completely).
    - C(deleted) resets attributes to the device default. A UNI named with identity only is reset completely, otherwise
      only the named attributes are reset; lists not named in I(config) are left alone. Without I(config) every UNI
      of both lists is reset.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
      C(uni_idx) in C(performance_monitor) and C(tc_layer_threshold) (targeted gathering, one
      C(info configure l2uni ont performance-monitor <uni> flat) or C(info configure l2uni ont tc-layer-threshold <uni> flat)
      read per UNI). Other fields are ignored and absent instances are not returned; an instance with nothing configured
      answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Enable PM collection with TCA and a dropped-frames threshold on one UNI
  nokia.isam.isam_l2uni_onts:
    config:
      performance_monitor:
        - uni_idx: 1/1/2/1/1/1/1
          pm_collect: tca-enable
          pm_collect_64bit: pm-enable
          pm_collect_ext:
            pm_collect: enable
            vlan_id: 100
      tc_layer_threshold:
        - uni_idx: 1/1/2/1/1/1/1
          dropped_frames_up: 1000
    state: merged

# commands:
# - configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect tca-enable pm-collect-64bit pm-enable
# - configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext pm-collect enable vlan-id 100
# - configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 dropped-frames-up 1000

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_l2uni_onts:
    config:
      performance_monitor:
        - uni_idx: 1/1/2/1/1/1/1
    state: gathered

- name: Reset the PM settings of a UNI to the device defaults
  nokia.isam.isam_l2uni_onts:
    config:
      performance_monitor:
        - uni_idx: 1/1/2/1/1/1/1
    state: deleted

# commands:
# - configure l2uni ont performance-monitor 1/1/2/1/1/1/1 no pm-collect no pm-collect-64bit
# - configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect-ext no pm-collect no vlan-id

- name: Parse device output
  nokia.isam.isam_l2uni_onts:
    running_config: |
      configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect pm-enable no pm-collect-64bit
      configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 dropped-frames-up 500 no dropped-frames-dn
    state: parsed
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
    - Only C(confirmed_absent) -- the device's explicit "instance does not exist" signal
      about that instance -- is evidence the instance is gone. C(unknown) (a header-only
      reply, an invalid-token rejection, a missing dependency, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(complete), C(partial), C(failed) or C(unverified)) is reported at
      resource level under C(parse); C(unverified) means the parser did not record its
      coverage of the reply.
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
  - With I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With I(running_config) (offline preview) they are rendered only, never sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
  sample:
  - configure l2uni ont performance-monitor 1/1/2/1/1/1/1 pm-collect pm-enable
  - configure l2uni ont tc-layer-threshold 1/1/2/1/1/1/1 no dropped-frames-up
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
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.l2uni_onts.l2uni_onts import (
    L2uni_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2uni_onts.l2uni_onts import (
    L2uni_onts,
)


def main():
    module = AnsibleModule(
        argument_spec=L2uni_ontsArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = L2uni_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
