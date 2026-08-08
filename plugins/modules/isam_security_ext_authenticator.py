#!/usr/bin/python
from __future__ import absolute_import, division, print_function

DOCUMENTATION = """
module: isam_security_ext_authenticator
short_description: Render or parse Nokia ISAM 802.1X port authentication commands.
description:
  - Implements the admin security ext-authenticator command documented in PDFs 227 and 228.
  - This resource is intentionally render/parse only; it never sends commands to a device.
options:
  config:
    type: list
    elements: dict
    suboptions:
      port:
        type: str
        required: true
      clear_statistics:
        type: bool
        default: false
  running_config:
    type: str
  state:
    type: str
    choices: [rendered, parsed]
    default: rendered
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
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Isam_security_ext_authenticator(module).execute_module())


if __name__ == "__main__":
    main()
