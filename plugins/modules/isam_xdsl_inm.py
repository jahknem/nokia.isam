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
      - Native C(info configure xdsl imp-noise-sensor flat) output to parse with I(state=parsed).
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
    - configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-eq-inp-mode 1 no inm-iat-offset
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_inm.xdsl_inm import (
    Xdsl_inmArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_inm.xdsl_inm import (
    Xdsl_inm,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_inmArgs.argument_spec,
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
    result = Xdsl_inm(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
