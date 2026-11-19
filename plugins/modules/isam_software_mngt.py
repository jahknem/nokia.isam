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
        description: Software database settings (C(configure software-mngt database)).
        type: dict
        suboptions:
          version:
            description: Value C(configure software-mngt database version) (no removal form).
            type: str
          url:
            description: Value C(configure software-mngt database url) (no removal form).
            type: str
          activate:
            description: Value C(configure software-mngt database activate); device default C(manually).
            type: str
            choices: [after-download, manually]
          backup:
            description: Value C(configure software-mngt database backup); device default C(manually).
            type: str
          backupv6:
            description: Value C(configure software-mngt database backupv6); device default C(manually).
            type: str
          auto_backup_interval:
            description: Value C(configure software-mngt database auto-backup-intvl); device default C(24).
            type: int
      oswp:
        description: OSWP records (C(configure software-mngt oswp)).
        type: list
        elements: dict
        suboptions:
          id:
            description: Instance identifier.
            type: str
            required: true
          primary_file_server_id:
            description: Value C(configure software-mngt oswp primary-file-server-id) (no removal form).
            type: str
          second_file_server_id:
            description: Value C(configure software-mngt oswp second-file-server-id) (no removal form).
            type: str
          download_set:
            description: Value C(configure software-mngt oswp download-set) (no removal form).
            type: str
            choices: [min-set, actual-set, complete-set]
          autofetch:
            description: Value C(configure software-mngt oswp autofetch) (no removal form).
            type: str
            choices: [disabled, enabled]
          activate:
            description: Value C(configure software-mngt oswp activate); device default C(manually).
            type: str
            choices: [manually, after-download, on-schedule]
          auto_verify:
            description: Value C(configure software-mngt oswp auto-verify); device default C(disabled).
            type: str
            choices: [disabled, enabled]
          on_schedule_time:
            description: Value C(configure software-mngt oswp on-schedule-time); no concrete default.
            type: str
          admin_state:
            description: On/off flag C(configure software-mngt oswp admin-state).
            type: bool
      sw_replacement_mode:
        description: Software replacement mode (C(configure software-mngt sw-replacement-mode)).
        type: dict
        suboptions:
          mode:
            description: C(configure software-mngt sw-replacement-mode <value>).
            type: str
            choices: [upgrade-via-active, upgrade-via-standby, lt-by-lt]
  running_config:
    description: Device native configuration to parse.
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - C(replaced) reconciles named OSWP entries and leaves unnamed OSWPs untouched;
        only C(overridden) removes OSWPs absent from the requested configuration.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
        C(oswp[].id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without
        I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_software_mngt:
    config:
      oswp:
        - id: "1"
    state: gathered

- name: Gather software management configuration
  nokia.isam.isam_software_mngt:
    state: gathered

- name: Configure software management database
  nokia.isam.isam_software_mngt:
    config:
      database:
        version: R6.2.04m
        url: tftp://192.0.2.1/software.bin
      oswp:
        - id: 1
          primary_file_server_id: 192.0.2.1
          second_file_server_id: 0.0.0.0
          activate: after-download
          auto_verify: enabled
          admin_state: true
      sw_replacement_mode:
        mode: upgrade-via-standby
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
