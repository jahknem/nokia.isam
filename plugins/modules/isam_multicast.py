#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_multicast
short_description: Manage Nokia ISAM multicast configuration.
description:
  - Manages C(configure igmp mcast-svc-context) and C(configure mcast-control) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided multicast configuration.
    type: dict
    suboptions:
      igmp:
        description: IGMP multicast service context settings.
        type: dict
        suboptions:
          mcast_svc_context:
            description: Multicast service context name.
            type: str
          mld_snooping:
            description: Enable or disable MLD snooping.
            type: bool
          mld_querier:
            description: Enable or disable MLD querier.
            type: bool
          igmp_snooping:
            description: Enable or disable IGMP snooping.
            type: bool
          igmp_querier:
            description: Enable or disable IGMP querier.
            type: bool
          query_interval:
            description: IGMP query interval in seconds.
            type: int
          query_response_interval:
            description: IGMP query response interval in seconds.
            type: int
          robustness_count:
            description: IGMP robustness count.
            type: int
      mcast_control:
        description: Multicast control settings.
        type: dict
        suboptions:
          mcast_svc_context:
            description: Multicast service context name.
            type: str
          admin_state:
            description: Enable or disable multicast control.
            type: bool
          max_groups:
            description: Maximum number of multicast groups.
            type: int
          max_sources:
            description: Maximum number of sources per group.
            type: int
  running_config:
    description: Device native configuration to parse.
    type: str
  state:
    description: The state of the configuration after module completion.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather multicast configuration
  nokia.isam.isam_multicast:
    state: gathered

- name: Configure IGMP multicast service context
  nokia.isam.isam_multicast:
    config:
      igmp:
        mcast_svc_context: default
        mld_snooping: true
        igmp_snooping: true
        query_interval: 125
      mcast_control:
        mcast_svc_context: default
        admin_state: true
        max_groups: 256
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
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
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
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.multicast.multicast import (
    MulticastArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.multicast.multicast import (
    Multicast,
)


def main():
    module = AnsibleModule(
        argument_spec=MulticastArgs.argument_spec,
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

    result = Multicast(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
