#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ntp_onts
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ntp_onts
short_description: Manages Nokia ISAM NTP ONT attributes.
description:
  - Manages C(configure ntp ont) attributes on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided NTP ONT configuration.
    type: list
    elements: dict
    suboptions:
      ont_id:
        type: str
        required: true
        description: ONT identifier (e.g. 1/1/1).
      server:
        type: str
        description: NTP server IP address or hostname.
      port:
        type: int
        description: NTP server port number.
      poll_interval:
        type: int
        description: NTP polling interval in seconds.
      enable:
        type: bool
        description: Enable or disable NTP on the ONT.
  running_config:
    description: The state-parsed running config.
    type: str
  state:
    description: The state the configuration should be left in.
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
- name: Render NTP ONT configuration
  nokia.isam.isam_ntp_onts:
    config:
      - ont_id: 1/1/1
        server: 10.0.0.1
        port: 123
        poll_interval: 60
        enable: true
    state: rendered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
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
  type: list
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ntp_onts.ntp_onts import (
    Ntp_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ntp_onts.ntp_onts import (
    Ntp_onts,
)


def main():
    """Main entry point for module execution."""
    module = AnsibleModule(
        argument_spec=Ntp_ontsArgs.argument_spec,
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

    result = Ntp_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
