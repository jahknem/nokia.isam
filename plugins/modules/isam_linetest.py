#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function


DOCUMENTATION = r'''
---
module: isam_linetest
short_description: Manage Nokia ISAM LineTest configuration
description:
  - Supports declarative single LineTest session and parameter configuration
    (C(configure linetest single ltsession) and C(configure linetest single ltparm)).
  - A session exists only after C(session-cmd create) and is removed with C(session-cmd destroy).
    C(merged), C(replaced) and C(overridden) send C(session-cmd create) for a requested session that
    does not exist, before its attributes; C(deleted) and C(overridden) send C(session-cmd destroy)
    only for existing sessions. No other LineTest action (such as C(starttest)) is sent, and
    C(rendered) renders the declarative attributes only.
  - Parameters of a session that neither exists nor is requested in I(config) are rejected.
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
            description: 'Test mode of the session (C(test-mode)): C(single) (ends after one run), C(interactive) or C(cablepair).'
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
            choices: ['true', 'false']
          force_measure:
            type: str
            description: Force the measurement.
            choices: ['true', 'false']
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
            description: 'Line test to run with this parameter entry (C(ltparm <session> test-name <name>)), for example C(ac-voltage-ab).'
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
    description:
      - 'Output from C(info configure linetest) for parsed state.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - Desired resource state.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(parameters[].session_id) and C(parameters[].test_name) and C(sessions[].session_id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
  version_added: 1.0.0
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
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.linetest.linetest import LinetestArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.linetest.linetest import Linetest


def main():
    module = AnsibleModule(
        argument_spec=LinetestArgs.argument_spec,
        required_if=[
            ["state", state, ["config"]]
            for state in ("merged", "replaced", "overridden", "rendered")
        ] + [["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**Linetest(module).execute_module())


if __name__ == "__main__":
    main()
