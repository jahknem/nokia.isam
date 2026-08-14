#!/usr/bin/python
from __future__ import absolute_import, division, print_function

DOCUMENTATION = """
module: isam_security_ext_authenticator
short_description: Run Nokia ISAM 802.1X port authentication actions.
description:
  - Implements the admin security ext-authenticator command documented in PDFs 227 and 228.
  - The command is an operational administrative action rather than persistent configuration.
options:
  config:
    description: Ports on which to perform the administrative action.
    type: list
    elements: dict
    suboptions:
      port:
        description: Interface port identifier.
        type: str
        required: true
      clear_statistics:
        description: Clear the port's authentication statistics.
        type: bool
        default: false
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
