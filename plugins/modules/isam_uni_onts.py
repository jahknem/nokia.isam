#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_uni_onts
short_description: Manages Nokia ISAM ONT UNI TC-layer performance monitoring.
description:
  - Manages C(configure uni ont tc-layer <uni>) (TC-layer performance monitor collection per ONT UNI) on Nokia ISAM.
  - The node exists with its ONT UNI; the module sets C(pm-collect) and resets it to the CLI default with
    C(no pm-collect). It does not create or remove UNIs (see M(nokia.isam.isam_ethernet_onts)).
  - The device default (C(disable), shown as C(no pm-collect)) is not reported, like an unset attribute.
    Configuring C(pm_collect=disable) is the same as resetting it.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against the C(info configure uni detail flat) output of Nokia ISAM 6.2.04.
  - TC-layer TCA thresholds of the same UNI are managed by M(nokia.isam.isam_l2uni_onts) (C(tc_layer_threshold)).
options:
  config:
    description: The provided UNI ONT TC-layer configuration.
    type: list
    elements: dict
    suboptions:
      uni_idx:
        type: str
        required: true
        description: ONT UNI index (e.g. C(1/1/2/1/1/1/1)).
      pm_collect:
        type: str
        choices: [enable, disable]
        description: Collection of TC-layer performance monitors (C(pm-collect)); device default C(disable).
  running_config:
    description:
      - 'Device configuration to parse with I(state=parsed), as returned by C(info configure uni flat) (with or without C(detail)).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - C(merged) sets the given attributes; C(replaced) also resets the unspecified attributes of the given UNIs;
      C(overridden) additionally resets every UNI that is not in I(config).
    - C(deleted) resets C(pm-collect) of the named UNIs (all UNIs without I(config)) to the device default.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
      C(uni_idx) (targeted gathering, one C(info configure uni ont tc-layer <uni> flat) read per UNI). Other fields
      are ignored and absent instances are not returned; an instance with only default values is read with
      C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or
      confirmed absent where the device allows it. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Enable TC-layer PM collection on a UNI
  nokia.isam.isam_uni_onts:
    config:
      - uni_idx: 1/1/2/1/1/1/1
        pm_collect: enable
    state: merged

# commands:
# - configure uni ont tc-layer 1/1/2/1/1/1/1 pm-collect enable

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_uni_onts:
    config:
      - uni_idx: 1/1/2/1/1/1/1
    state: gathered

- name: Reset TC-layer PM collection of a UNI
  nokia.isam.isam_uni_onts:
    config:
      - uni_idx: 1/1/2/1/1/1/1
    state: deleted

# commands:
# - configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect
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
  - With C(deleted) and I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: list
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With C(deleted) and I(running_config) (offline preview of the removal) they are rendered only, never
    sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
  sample:
  - configure uni ont tc-layer 1/1/2/1/1/1/1 pm-collect enable
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.uni_onts.uni_onts import (
    Uni_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.uni_onts.uni_onts import (
    Uni_onts,
)


def main():
    module = AnsibleModule(
        argument_spec=Uni_ontsArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Uni_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
