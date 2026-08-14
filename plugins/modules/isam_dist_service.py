#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

MODULE_DESCRIPTION = """
module: isam_dist_service
short_description: Manages distributed service configuration on Nokia ISAM.
description: Manages distributed service configuration on Nokia ISAM.
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
      service_type:
        type: str
        choices: [unknown, epipe, p3pipe, tls, vprn, ies, mirror, apipe, fpipe, ipipe, cpipe]
        default: apipe
      qos_profile:
        type: str
        default: none
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dist_service.dist_service import Isam_dist_serviceArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dist_service.dist_service import Isam_dist_service


def main():
    module = AnsibleModule(
        argument_spec=Isam_dist_serviceArgs.argument_spec,
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
    module.exit_json(**Isam_dist_service(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_dist_service
short_description: Manage Nokia ISAM distributed services
description: Manage Nokia ISAM distributed services.
"""
