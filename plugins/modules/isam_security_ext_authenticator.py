#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_security_ext_authenticator
short_description: Run Nokia ISAM 802.1X port authentication actions.
description:
  - Sends the operational administrative command C(admin security ext-authenticator <port> clear-statistics)
    (CLI guide 227.2), which clears a port's non-accounting 802.1X authentication statistics.
  - This is an B(action module) it writes to the device, but performs a one-shot operation rather than
    managing persistent configuration. It has no resource states (merged/replaced/deleted/...) and is not
    idempotent; running it is an event. It is not an Ansible action plugin (controller-side helper).
  - I(clear_statistics) is the operation and must be C(true). A bare C(admin security ext-authenticator <port>)
    without an operation only navigates to the port in the admin hierarchy and performs no action, so it is
    rejected rather than reported as a change.
version_added: 0.3.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Ports on which to perform the administrative action.
    type: list
    elements: dict
    required: true
    suboptions:
      port:
        description: Interface port identifier (e.g. C(1/1/1/1) or an ONT/UNI path).
        type: str
        required: true
      clear_statistics:
        description:
          - Clear the port's non-accounting authentication statistics. This is the operation; it must be C(true).
          - C(false) (the default) names no operation and is rejected.
        type: bool
        default: false
"""

EXAMPLES = """
- name: Clear 802.1X authentication statistics on two ports
  nokia.isam.isam_security_ext_authenticator:
    config:
      - port: 1/1/1/1
        clear_statistics: true
      - port: 1/1/1/2
        clear_statistics: true

- name: Check what would run without touching the device
  nokia.isam.isam_security_ext_authenticator:
    config:
      - port: 1/1/1/1
        clear_statistics: true
  check_mode: true
"""

RETURN = """
changed:
  description: Whether an action command was (or would be, in check mode) sent.
  returned: always
  type: bool
commands:
  description: The operational commands sent (or that would be sent in check mode).
  returned: always
  type: list
  elements: str
response:
  description: The device responses to the commands (empty in check mode).
  returned: when not check mode
  type: list
  elements: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.security_ext_authenticator.security_ext_authenticator import (
    Isam_security_ext_authenticatorArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.security_ext_authenticator.security_ext_authenticator import (
    Isam_security_ext_authenticator,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_security_ext_authenticatorArgs.argument_spec,
        supports_check_mode=True,
    )
    module.exit_json(**Isam_security_ext_authenticator(module).execute_module())


if __name__ == "__main__":
    main()
