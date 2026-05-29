#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_lines
short_description: Manages XDSL line attributes of Nokia ISAM.
description:
  - Manages C(configure xdsl line) settings on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Initial implementation covers fields observed on live C(info configure xdsl line).
options:
  config:
    description: List of XDSL lines to configure.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        aliases: [if_index]
        description: XDSL line interface index, for example C(1/1/3/1).
      service_profile:
        type: str
        aliases: [service-profile]
        description: Service profile reference.
      spectrum_profile:
        type: str
        aliases: [spectrum-profile]
        description: Spectrum profile reference.
      dpbo_profile:
        type: str
        aliases: [dpbo-profile]
        description: DPBO profile reference.
      vect_profile:
        type: str
        aliases: [vect-profile]
        description: Vectoring profile reference.
      admin_up:
        type: bool
        aliases: [admin-up]
        description: Administrative state of the XDSL line.
  running_config:
    description:
      - Native C(info configure xdsl line) output to parse.
    type: str
  state:
    description: The state of the configuration after module completion.
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
- name: Configure an XDSL line
  nokia.isam.isam_xdsl_lines:
    config:
      - name: 1/1/3/1
        service_profile: "13"
        spectrum_profile: "2"
        dpbo_profile: "1"
        vect_profile: "10"
        admin_up: true
    state: merged

- name: Gather XDSL line facts
  nokia.isam.isam_xdsl_lines:
    state: gathered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_lines.xdsl_lines import (
    Xdsl_linesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_lines.xdsl_lines import (
    Xdsl_lines,
)


def main():
    """Main entry point for module execution."""
    module = AnsibleModule(
        argument_spec=Xdsl_linesArgs.argument_spec,
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

    result = Xdsl_lines(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
