#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_interface_cages
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_interface_cages
version_added: 1.0.0
short_description: 'Manage interface cage attributes on Nokia ISAM MSAN devices.'
description: 'This module manages interface cage configuration and facts on Nokia ISAM MSAN devices.'
author: Jan Kühnemund (@jahknem)
notes:
- 'Tested against Nokia ISAM with OS Version R6.2.04m'
- R6.2.04m only knows C(operational-mode) for a cage; it refuses C(description) and C(apply-qos) (C(invalid token)).
options:
  config:
    description: A dictionary of options for interface cages
    type: list
    elements: dict
    suboptions:
      id:
        type: str
        description:
        - Configure a specific interface cage identifier.
        required: true
      description:
        type: str
        description:
        - Description of the interface cage.
      apply_qos:
        type: bool
        description:
        - Apply QoS to the interface cage.
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - C(operational_mode) has no CLI removal form (cages are fixed positions). With C(deleted), C(replaced) or C(overridden) a mode that would be removed is kept on the device and a warning is returned.
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
- name: Merge interface cage configuration
  nokia.isam.isam_interface_cages:
    config:
      - id: "1"
        description: "Main distribution cage"
        apply_qos: true
    state: merged

- name: Delete interface cage configuration
  nokia.isam.isam_interface_cages:
    config:
      - id: "1"
    state: deleted

- name: Render interface cage commands
  nokia.isam.isam_interface_cages:
    config:
      - id: "2"
        description: "Secondary cage"
        apply_qos: false
    state: rendered

- name: Gather interface cage facts
  nokia.isam.isam_interface_cages:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_interface_cages:
    config:
      - id: "1"
    state: gathered

- name: Parse interface cage configuration
  nokia.isam.isam_interface_cages:
    running_config: |
      configure interface cage 1 description "Main cage"
      configure interface cage 1 apply-qos
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
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - configure interface cage 1
    - configure interface cage 1 description Main cage
    - configure interface cage 1 apply-qos
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - configure interface cage 1
    - configure interface cage 1 description Main cage
    - configure interface cage 1 apply-qos
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interface_cages.interface_cages import (
    InterfaceCagesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.interface_cages.interface_cages import (
    InterfaceCages,
)


def main():
    """
    Main entry point for module execution

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=InterfaceCagesArgs.argument_spec,
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

    result = InterfaceCages(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
