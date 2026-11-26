#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_qos_maps
version_added: 1.0.0
short_description: Manage QoS maps on Nokia ISAM devices
description:
- Manage QoS mapping tables on Nokia ISAM devices.
- Supports C(tc-map-dot1p), C(dscp-map-dot1p), C(up-ctrl-pkt), and C(dn-ctrl-pkt) sub-families.
author: Jan Kühnemund (@jahknem)
notes:
- Tested against read-only output from Nokia ISAM 6.2.04ng.
options:
  config:
    type: dict
    description: QoS maps configuration.
    suboptions:
      tc_map_dot1p:
        type: list
        elements: dict
        description: List of 802.1p to traffic-class mappings.
        suboptions:
          dot1p:
            type: int
            description: 802.1p priority value (0-7).
            required: true
          tc:
            type: int
            description: Traffic class index.
          dpcolor:
            type: str
            description:
            - Output discard precedence on the queue (C(dpcolor)).
            - Device values are C(green) or C(yellow).
          policer_color:
            type: str
            description:
            - Frame colour for trTCM (C(policer-color)).
            - Device values are C(green), C(yellow) or C(red).
      dscp_map_dot1p:
        type: list
        elements: dict
        description: List of DSCP to 802.1p mappings.
        suboptions:
          dscp:
            type: str
            description: DSCP value (numeric or name like C(CS0), C(EF), etc.).
            required: true
          dot1p:
            type: int
            description: 802.1p priority value.
      up_ctrl_pkt:
        type: list
        elements: dict
        description: List of upstream control-packet classifications.
        suboptions:
          protocol:
            type: str
            description: Protocol name (e.g. C(arp), C(dhcp), C(pppoe)).
            required: true
          dscp:
            type: int
            description: DSCP value.
          pbit:
            type: int
            description: Priority bit (802.1p).
          tc:
            type: int
            description: Traffic class.
      dn_ctrl_pkt:
        type: list
        elements: dict
        description: List of downstream control-packet classifications.
        suboptions:
          protocol:
            type: str
            description: Protocol name.
            required: true
          dscp:
            type: int
            description: DSCP value.
          pbit:
            type: int
            description: Priority bit (802.1p).
          tc:
            type: int
            description: Traffic class.
  running_config:
    description:
      - 'Output from C(info configure qos), used with state C(parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - Desired resource state.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(tc_map_dot1p[].dot1p) and C(dscp_map_dot1p[].dscp) and C(up_ctrl_pkt[].protocol) and C(dn_ctrl_pkt[].protocol) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(deleted) and I(config), only the sections and instances named in I(config) are deleted or reset; other sections are left alone. Without I(config) everything is deleted. Naming an entry by its identity alone is enough.
    type: str
    default: merged
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
"""

EXAMPLES = """
- name: Gather QoS maps
  nokia.isam.isam_qos_maps:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_qos_maps:
    state: gathered
    config:
      tc_map_dot1p:
        - dot1p: 5
      up_ctrl_pkt:
        - protocol: dhcp

- name: Render tc-map-dot1p entries
  nokia.isam.isam_qos_maps:
    state: rendered
    config:
      tc_map_dot1p:
        - dot1p: 0
          tc: 0
        - dot1p: 7
          tc: 7

- name: Render dscp-map-dot1p entries
  nokia.isam.isam_qos_maps:
    state: rendered
    config:
      dscp_map_dot1p:
        - dscp: CS0
          dot1p: 0
        - dscp: EF
          dot1p: 5

- name: Render control-packet entries
  nokia.isam.isam_qos_maps:
    state: rendered
    config:
      up_ctrl_pkt:
        - protocol: dhcp
          dscp: 46
          tc: 7
      dn_ctrl_pkt:
        - protocol: dhcp
          tc: 3
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
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: Configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured QoS maps data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured QoS maps data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_maps.qos_maps import (
    Qos_mapsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_maps.qos_maps import (
    Qos_maps,
)


def main():
    module = AnsibleModule(
        argument_spec=Qos_mapsArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Qos_maps(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
