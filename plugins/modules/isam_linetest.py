#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.linetest.linetest import LinetestArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.linetest.linetest import Linetest


DOCUMENTATION = r'''
---
module: isam_linetest
short_description: Manage Nokia ISAM LineTest configuration
description:
  - Supports declarative single LineTest session and parameter configuration
    (C(configure linetest single ltsession) and C(configure linetest single ltparm)).
  - Sends only configuration commands; it does not execute LineTest actions.
  - Omitted options are not rendered or reset with C(merged). With C(replaced) or
    C(overridden), omitted configured C(group_opt), C(busy_overwrite) and C(force_measure)
    are reset using their trailing C(no) form. Unchanged parameters emit no commands.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    type: dict
    description: Declarative LineTest configuration.
    suboptions:
      sessions:
        type: list
        elements: dict
        description: LineTest sessions (C(configure linetest single ltsession)).
        suboptions:
          session_id:
            type: str
            required: true
            description: Session identifier.
          ownerid:
            type: str
            description: Owner identifier of the session.
          timeout_period:
            type: str
            description: Session timeout period.
          line_num:
            type: str
            description: Number of lines in the session.
          type_high:
            type: str
            description: High part of the test type bitmap.
          type_low:
            type: str
            description: Low part of the test type bitmap.
          test_parm_num:
            type: str
            description: Number of test parameters.
          test_mode:
            type: str
            description: Test mode.
            choices: [single, interactive, cablepair]
          inactive_timer:
            type: str
            description: Inactivity timer.
          type_extend:
            type: str
            description: Extended test type bitmap.
          group_opt:
            type: str
            description: Group option.
            choices: [none, extended, pots-collective, melt-collective]
          busy_overwrite:
            type: str
            description: Overwrite busy lines.
            choices: [true, false]
          force_measure:
            type: str
            description: Force the measurement.
            choices: [true, false]
      parameters:
        type: list
        elements: dict
        description: LineTest test parameters (C(configure linetest single ltparm)).
        suboptions:
          session_id:
            type: str
            required: true
            description: Session identifier.
          test_name:
            type: str
            required: true
            description: Test name.
          value1:
            type: str
            description: Test parameter value 1.
          value2:
            type: str
            description: Test parameter value 2.
          value3:
            type: str
            description: Test parameter value 3.
          value4:
            type: str
            description: Test parameter value 4.
          value5:
            type: str
            description: Test parameter value 5.
          min_threshold:
            type: str
            description: Minimum threshold.
          max_threshold:
            type: str
            description: Maximum threshold.
          min_threshold2:
            type: str
            description: Second minimum threshold.
          max_threshold2:
            type: str
            description: Second maximum threshold.
          ltstrvalue1:
            type: str
            description: String test parameter value.
  running_config:
    type: str
    description: Output from C(info configure linetest) for parsed state.
  state:
    description:
      - Desired resource state.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(parameters[].session_id) and C(parameters[].test_name) and C(sessions[].session_id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
'''

EXAMPLES = r'''
- name: Configure a LineTest session
  nokia.isam.isam_linetest:
    config:
      sessions:
        - session_id: "1"
          ownerid: "3"
          timeout_period: "100"
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_linetest:
    config:
      sessions:
        - session_id: "1"
      parameters:
        - session_id: "1"
          test_name: ac-voltage-ab
    state: gathered
'''

RETURN = r'''
extends_documentation_fragment: nokia.isam.read_outcomes
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
  type: dict
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
'''


def main():
    module = AnsibleModule(
        argument_spec=LinetestArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", state, ["config"]]
            for state in ("merged", "replaced", "overridden", "rendered")
        ] + [["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**Linetest(module).execute_module())


if __name__ == "__main__":
    main()
