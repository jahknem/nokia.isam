#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_inm
short_description: Manages Nokia ISAM xDSL impulse noise monitoring (INM) sensors.
description:
  - Manages C(configure xdsl imp-noise-sensor near-end <line>) and
    C(configure xdsl imp-noise-sensor far-end <line>) on Nokia ISAM devices.
  - The impulse noise sensor itself is switched on per line with I(imp_noise_sensor)
    of M(nokia.isam.isam_xdsl_lines); this module manages the sensor parameters.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - The attribute set is the one the device prints in the detail output of C(info configure xdsl imp-noise-sensor).
    Values are passed through as strings; the accepted ranges are not verified against the device help.
  - A sensor exists for every xDSL line and cannot be removed. C(deleted) and C(overridden)
    reset its attributes to the device defaults (C(no <attribute>)).
options:
  config:
    description: Impulse noise sensor configuration, per direction.
    type: dict
    suboptions:
      near_end:
        description: Near-end (upstream, measured by the ISAM) sensors, one per xDSL line.
        type: list
        elements: dict
        suboptions:
          name:
            type: str
            required: true
            description: xDSL line index, for example C(1/1/3/1).
          inm_mode:
            type: str
            description: INM mode (C(inm-mode)). Unset means the device default.
          inm_eq_inp_mode:
            type: str
            description: Equivalent INP mode used to classify impulses (C(inm-eq-inp-mode)).
          ins_sensitivity:
            type: str
            description: Impulse noise sensor sensitivity (C(ins-sensitivity)).
          inm_cluster_cont:
            type: str
            description: Cluster continuation value (C(inm-cluster-cont)).
          inm_iat_offset:
            type: str
            description: Inter-arrival time histogram offset (C(inm-iat-offset)).
          inm_iat_step:
            type: str
            description: Inter-arrival time histogram step (C(inm-iat-step)).
      far_end:
        description: Far-end (downstream, measured by the CPE) sensors, one per xDSL line.
        type: list
        elements: dict
        suboptions:
          name:
            type: str
            required: true
            description: xDSL line index, for example C(1/1/3/1).
          inm_mode:
            type: str
            description: INM mode (C(inm-mode)). Unset means the device default.
          inm_eq_inp_mode:
            type: str
            description: Equivalent INP mode used to classify impulses (C(inm-eq-inp-mode)).
          ins_sensitivity:
            type: str
            description: Impulse noise sensor sensitivity (C(ins-sensitivity)).
          inm_cluster_cont:
            type: str
            description: Cluster continuation value (C(inm-cluster-cont)).
          inm_iat_offset:
            type: str
            description: Inter-arrival time histogram offset (C(inm-iat-offset)).
          inm_iat_step:
            type: str
            description: Inter-arrival time histogram step (C(inm-iat-step)).
  running_config:
    description:
      - 'Native C(info configure xdsl imp-noise-sensor flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) in I(near_end) and I(far_end) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
      - C(deleted) resets the named sensors (all sensors of a direction given as an empty list, all sensors without I(config)).
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
- name: Configure the near-end sensor of a line
  nokia.isam.isam_xdsl_inm:
    config:
      near_end:
        - name: 1/1/3/1
          inm_eq_inp_mode: "1"
          inm_iat_offset: "5"
    state: merged

# commands:
# - configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-eq-inp-mode 1 inm-iat-offset 5

- name: Read only the named sensors (targeted gathering)
  nokia.isam.isam_xdsl_inm:
    config:
      near_end:
        - name: 1/1/3/1
      far_end:
        - name: 1/1/3/1
    state: gathered

- name: Reset the far-end sensor of a line to the defaults
  nokia.isam.isam_xdsl_inm:
    config:
      far_end:
        - name: 1/1/3/1
    state: deleted

- name: Parse device output
  nokia.isam.isam_xdsl_inm:
    running_config: |
      configure xdsl imp-noise-sensor near-end 1/1/3/1 no inm-mode inm-eq-inp-mode 1 no ins-sensitivity
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
  - With C(deleted) and I(running_config) (offline preview of the removal) they are rendered only, never
    sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
  sample:
  - configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-eq-inp-mode 1 no inm-iat-offset
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_inm.xdsl_inm import (
    Xdsl_inmArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_inm.xdsl_inm import (
    Xdsl_inm,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_inmArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Xdsl_inm(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
