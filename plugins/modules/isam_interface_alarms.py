#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_interface_alarms
short_description: Resource module to configure interface alarm default severity
description:
  - Manages C(configure interface alarm) default severity settings on Nokia ISAM devices.
version_added: 0.3.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Interface alarm configurations.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description:
          - Resource identifier (index of the IANA ifType).
      default_severity:
        type: str
        choices: [indeterminate, warning, minor, major, critical]
        description:
          - Default severity to be reported with default value "major".
          - Alarms below this threshold will not be reported.
  running_config:
    description: Device-native configuration to parse when state is parsed.
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), the device exposes no single-instance read for interface
        alarms, so the whole node is read once and each named alarm is reported in C(read_outcomes)
        as C(present) when the parsed catalog lists it and C(unknown) when it does not
        (C(confirmed_absent) only when the device says the node itself does not exist);
        I(gathered) stays the full catalog. Without I(config) the whole resource is read, as before.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather interface alarms
  nokia.isam.isam_interface_alarms:
    state: gathered


- name: Read only the named alarms (targeted gathering)
  nokia.isam.isam_interface_alarms:
    state: gathered
    config:
      - name: "6"


- name: Set default severity for Ethernet interface alarm
  nokia.isam.isam_interface_alarms:
    config:
      - name: "6"
        default_severity: major
    state: merged
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
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
  returned: when state is rendered
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when state is gathered
  type: list
parsed:
  description: Device-native config parsed into structured data.
  returned: when state is parsed
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interface_alarms.interface_alarms import (
    Interface_alarmsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.interface_alarms.interface_alarms import (
    Interface_alarms,
)


def main():
    module = AnsibleModule(
        argument_spec=Interface_alarmsArgs.argument_spec,
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

    result = Interface_alarms(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
