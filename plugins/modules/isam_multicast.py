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
author: Ansible Network Engineer
options:
  config:
    description: The provided multicast configuration.
    type: dict
    suboptions:
      igmp:
        description: IGMP multicast service context settings.
        type: dict
        suboptions:
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
        mld_snooping: true
        igmp_snooping: true
        query_interval: 125
      mcast_control:
        admin_state: true
        max_groups: 256
    state: merged
"""

RETURN = """
before:
  description: The configuration as structured data before module invocation.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
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
