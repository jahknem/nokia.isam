#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_link_agg
version_added: 1.0.0
short_description: Manages Nokia ISAM link aggregation configuration
description:
- Manages C(configure link-agg port) and C(configure link-agg group) configuration.
author: Jan Kühnemund (@jahknem)
notes:
- Tested against Nokia ISAM with OS Version R6.2.04ng.
options:
  config:
    description: Link aggregation configuration.
    type: dict
    suboptions:
      ports:
        description: LACP port configuration entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Port identifier.
            type: str
            required: true
            aliases: [name]
          lacp_mode:
            description: Convenience view of passive-lacp state.
            type: str
            choices: [active, passive]
            aliases: [mode]
          passive_lacp:
            description: Set LACP inactive for the actor.
            type: bool
          timeout:
            description: Convenience view of short-timeout state.
            type: str
            choices: [long, short]
          short_timeout:
            description: Use short timeout for the LACP protocol.
            type: bool
          actor_port_prio:
            description: Actor port priority.
            type: str
      groups:
        description: LACP group configuration entries.
        type: list
        elements: dict
        suboptions:
          id:
            description: Link aggregation group identifier.
            type: str
            required: true
            aliases: [name]
          load_sharing_policy:
            description: Link aggregation load sharing policy.
            type: str
            choices: [mac-src, mac-dst, mac-src-dst, ip-src, ip-dst, ip-src-dst, l2-l3-hybrid-model]
          max_active_port:
            description: Maximum active port number in a LAG.
            type: str
          swo_threshold:
            description: Switchover threshold in a cross-LT LAG.
            type: str
          priority:
            description: LACP aggregate actor system priority.
            type: str
          swo_revert:
            description: Switchover revert flag in a cross-LT LAG.
            type: str
            choices: [disable, enable]
          mode:
            description: LACP group mode.
            type: str
            choices: [static, dynamic]
          master_iwf:
            description: Master IWF value.
            type: str
            choices: [auto, unset]
          ports:
            description: Member port identifiers for the group.
            type: list
            elements: str
  running_config:
    description:
    - This option is used only with state C(parsed).
    - The value should be the output of C(info configure link-agg) or C(info configure link-agg flat).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(groups[].id) and C(ports[].id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(deleted) and I(config), only the sections and instances named in I(config) are deleted or reset; other sections are left alone. Without I(config) everything is deleted.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather link aggregation facts
  nokia.isam.isam_link_agg:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_link_agg:
    state: gathered
    config:
      groups:
        - id: 1/1/8/10
      ports:
        - id: 1/1/8/1

- name: Configure a LACP port and group
  nokia.isam.isam_link_agg:
    state: merged
    config:
      ports:
        - id: 1/1/8/1
          lacp_mode: passive
          timeout: short
      groups:
        - id: 1/1/8/10
          load_sharing_policy: mac-src-dst
          swo_revert: enable
          mode: dynamic
          master_iwf: auto
          ports:
            - 1/1/8/1
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
before:
  description: The configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: The commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when state is gathered
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.link_agg.link_agg import (
    Link_aggArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.link_agg.link_agg import (
    Link_agg,
)


def main():
    module = AnsibleModule(
        argument_spec=Link_aggArgs.argument_spec,
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

    result = Link_agg(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
