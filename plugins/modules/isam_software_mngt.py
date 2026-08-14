#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_software_mngt
short_description: Manage Nokia ISAM software management configuration.
description:
  - Manages C(configure software-mngt database), C(software-mngt oswp), and C(software-mngt sw-replacement-mode) configuration.
version_added: 0.3.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided software management configuration.
    type: dict
    suboptions:
      database:
        description: Software database settings.
        type: dict
        suboptions:
          version:
            description: Software version.
            type: str
          url:
            description: Database URL.
            type: str
          backup:
            description: IPv4 database backup target.
            type: str
          backupv6:
            description: IPv6 database backup target.
            type: str
          auto_backup_interval:
            description: Automatic database backup interval.
            type: int
      oswp:
        description: OSWP settings.
        type: list
        elements: dict
        suboptions:
          id:
            description: OSWP identifier.
            type: str
            required: true
          primary_file_server_id:
            description: Primary file-server identifier.
            type: str
          second_file_server_id:
            description: Secondary file-server identifier.
            type: str
          activate:
            description: Activate this OSWP record.
            type: bool
          auto_verify:
            description: Enable automatic OSWP verification.
            type: bool
          on_schedule_time:
            description: Schedule activation at the configured time.
            type: bool
          admin_state:
            description: Enable or disable OSWP administration.
            type: bool
      sw_replacement_mode:
        description: Software replacement mode settings.
        type: dict
        suboptions:
          mode:
            description: Replacement mode.
            type: str
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
- name: Gather software management configuration
  nokia.isam.isam_software_mngt:
    state: gathered

- name: Configure software management database
  nokia.isam.isam_software_mngt:
    config:
      database:
        version: R6.2.04m
        url: tftp://10.0.0.1/software.bin
      oswp:
        - id: 1
          primary_file_server_id: 10.0.0.1
          second_file_server_id: 0.0.0.0
          activate: true
          auto_verify: true
          admin_state: true
      sw_replacement_mode:
        mode: auto
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import (
    Software_mngtArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.software_mngt.software_mngt import (
    Software_mngt,
)


def main():
    module = AnsibleModule(
        argument_spec=Software_mngtArgs.argument_spec,
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

    result = Software_mngt(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
