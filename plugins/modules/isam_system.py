#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_system
short_description: Manages system configuration on Nokia ISAM.
description:
  - Manages the C(configure system) resources including id, security, sntp,
    sync-if-timing, syslog, and transaction settings.
version_added: 1.0.0
author: Jan Kuehnemund
options:
  config:
    description: System configuration grouped by resource type.
    type: dict
    suboptions:
      id:
        description: System identification parameters.
        type: dict
        suboptions:
          name:
            description: System name.
            type: str
          location:
            description: System location.
            type: str
          contact:
            description: System contact information.
            type: str
      security:
        description: System security settings.
        type: dict
        suboptions:
          ssh:
            description: Enable SSH access.
            type: bool
          telnet:
            description: Enable telnet access.
            type: bool
          snmp:
            description: Enable SNMP access.
            type: bool
      sntp:
        description: SNTP configuration.
        type: dict
        suboptions:
          server:
            description: SNTP server IP address.
            type: str
          port:
            description: SNTP server port.
            type: int
          poll_interval:
            description: Polling interval in seconds.
            type: int
      syslog:
        description: Syslog configuration.
        type: dict
        suboptions:
          server:
            description: Syslog server address.
            type: str
          facility:
            description: Syslog facility.
            type: str
          severity:
            description: Syslog severity level.
            type: str
      sync_if_timing:
        description: Synchronous interface timing configuration.
        type: dict
        suboptions:
          mode:
            description: Timing mode.
            type: str
          source:
            description: Timing source.
            type: str
      transaction:
        description: Transaction configuration.
        type: dict
        suboptions:
          timeout:
            description: Transaction timeout in seconds.
            type: int
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description: Desired resource state.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather system config
  nokia.isam.isam_system:
    state: gathered

- name: Render system config
  nokia.isam.isam_system:
    state: rendered
    config:
      id:
        name: ISAM-01
        location: Datacenter-A
        contact: admin@example.com
      security:
        ssh: true
        telnet: false
        snmp: true
      sntp:
        server: 10.0.0.1
        port: 123
        poll_interval: 3600
      syslog:
        server: 10.0.0.2
        facility: local0
        severity: info
      sync_if_timing:
        mode: free-run
        source: internal
      transaction:
        timeout: 300
"""

RETURN = """
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
  description: Gathered structured system data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured system data.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system.system import (
    Isam_systemArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.system.system import (
    Isam_system,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_systemArgs.argument_spec,
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

    result = Isam_system(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
