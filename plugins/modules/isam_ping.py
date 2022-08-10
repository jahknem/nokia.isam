#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ping
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ping
short_description: 'Runs ping on an ISAM Device.'
description: 'Runs a ping with the given parameters on an ISAM Device against any IP Address.'
author: Jan Kühnemund
notes:
  - 'Tested against Nokia ISAM with OS Version R6.2.04m'
options:
  ip_address:
    description: The IP Address to ping.
    type: str
    required: true
  detail_rapid:
    description:
    - detail - show extra information in error cases
    - rapid  - change the units for 'interval' from seconds to centiseconds
    - These models are mutually exclusive.
    type: str
  time_to_live:
    description:
    - The time-to-live for the ping.
    type: int
    default: 64
  type_of_service:
    description:
    - The type of service for the ping.
    type: int
    default: 0
  bytes:
    description:
    - The number of bytes to send in the ping.
    type: int
    default: 56
  pattern:
    description:
    - The pattern to use for the ping.
    type: int
    default:  system-generated sequential pattern
  centisecs:
    description:
    - "If 'rapid' is selected, 1..10000 centiseconds, default: 1 centisecond"
    type: int
    default: 1
  secs:
    description:
    - "Otherwise, 1..10000 seconds, default: 1 second"
    type: int
    default: 1
  bypass-routing:
    description:
    - "Bypass routing for the ping. This is useful for pinging a host on the same subnet as the ISAM device."
    type: bool
    default: false
  requests:
    description:
    - The number of requests to send in the ping.
    type: int
    default: 1
  do-not-fragment:
    description:
    - "Do not fragment the ping."
    type: bool
    default: false
  interface-name:
    description:
    - "The name of the interface to use for the ping"
    type: str
  router-instance:
    description:
    - "The name of the router instance to use for the ping"
    type: str
    choices:
    - "Base"
    - "management"
    - "vpls-management"
  timeout:
    description:
    - "The number of seconds to wait for a response."
    type: int
    default: 5
  service-name:
    description:
    - "The name of the service to use for the ping"
    type: str
  fc-name:
    type: str
    choices:
    - 'be'
    - 'l2'
    - 'af'
    - 'l1'
    - 'h2'
    - 'ef'
    - 'h1'
    - 'nc'
    default: 'nc'
"""

EXAMPLES = """

"""

RETURN = """
before:
  description: The configuration prior to the module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
  sample: >
    This output will always be in the same format as the
    module argspec.
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted) or C(purged)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
rendered:
  description: The provided configuration in the task rendered in device-native format (offline).
  returned: when I(state) is C(rendered)
  type: list
  sample:
    - sample command 1
    - sample command 2
    - sample command 3
gathered:
  description: Facts about the network resource gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
parsed:
  description: The device native config provided in I(running_config) option parsed into structured data as per module argspec.
  returned: when I(state) is C(parsed)
  type: list
  sample: >
    This output will always be in the same format as the
    module argspec.
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.isam.isam.plugins.module_utils.network.isam.argspec.ping.ping import (
    PingArgs,
)
from ansible_collections.isam.isam.plugins.module_utils.network.isam.config.ping.ping import (
    Ping,
)


def main():
    """
    Main entry point for module execution

    :returns: the result form module invocation
    """
    module = AnsibleModule(
        argument_spec=PingArgs.argument_spec,
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

    result = Ping(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
