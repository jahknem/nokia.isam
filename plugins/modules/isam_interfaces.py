#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_interfaces
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_interfaces
version_added: 1.0.0
short_description: 'Manages interface attributes of Nokia ISAM MSAN devices.'
description: 'This module manages interface attributes of Nokia ISAM MSAN devices'
author: Jan Kühnemund (@jahknem)
notes:
- 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  config:
    description: A dictionary of options for interface ports
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        aliases: [id]
        description:
        - configure a specific interface port
      admin_up:
        type: bool
        aliases: [admin-up]
        description:
        - If the interface has been activated administratevly
      link_updown_trap:
        type: bool
        aliases: [link-updown-trap]
        description:
        - If up/down state changes of the interface should be trapped
      user:
        type: str
        description:
          - description of the user connected to this interface. (only supported for physical interfaces)
      severity:
        type: str
        description:
        - set minimum severity for alarm to be reported,If ima is the only interface for which this parameter is not supported
        - 'Possible values:'
        - '- indeterminate : not a definite known severity'
        - '- warning : just to inform as a warning'
        - '- minor : not service affecting'
        - '- major : service affecting'
        - '- critical : service breaking'
        - '- no-alarms : do not report alarm'
        - '- default : take default as specified via Interface Alarm Configuration command'
        - '- no-value : no entry in the table'
        choices:
        - indeterminate
        - warning
        - minor
        - major
        - critical
        - no-alarms
        - default
        - no-value
        default: no-value
      port_type:
        aliases: [port-type]
        description:
        - The whole network service model based on this interface
        type: str
        choices:
        - uni
        - nni
        - hc-uni
        - uplink
        default: uni
  running_config:
    description:
    - With state C(parsed), the configuration to parse; the value should be the output of C(info configure interface port flat).
    - With state C(deleted) and no I(config), the current configuration for an offline preview of the removal of
      everything in it (CLI text or the canonical resource JSON); nothing is read from or sent to the device.
    type: str

  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    - C(deleted) never brings an interface up. An ONT or VLAN-port interface the device creates with C(admin-up) stays down when it was set down; name I(admin_up) with C(merged) to bring it up.
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
- name: Gather interface facts
  nokia.isam.isam_interfaces:
    state: gathered

- name: Enable interface and set alarm behavior
  nokia.isam.isam_interfaces:
    state: merged
    config:
      - name: "ethernet-line:1/1/8/1"
        admin_up: true
        link_updown_trap: true
        severity: warning
        port_type: nni

- name: Legacy aliases are still accepted
  nokia.isam.isam_interfaces:
    state: merged
    config:
      - id: "ethernet-line:1/1/8/2"
        admin-up: true
        link-updown-trap: false
        port-type: uni

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_interfaces:
    config:
      - name: uni:1/1/5/1/3/1/1
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.interfaces.interfaces import (
    Interfaces,
)


def main():
    """
    Main entry point for module execution

    :returns: the result from module invocation
    """
    module = AnsibleModule(
        argument_spec=InterfacesArgs.argument_spec,
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

    result = Interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
