#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_dist_service
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_dist_service
short_description: Manages distributed service configuration on Nokia ISAM.
description:
  - Manages C(configure dist-service) entries on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided distributed service configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Distributed service identifier.
      service_type:
        type: str
        description: Service type.
        choices: [unknown, epipe, p3pipe, tls, vprn, ies, mirror, apipe, fpipe, ipipe, cpipe]
      qos_profile:
        type: str
        description: QoS profile of the service, C(none) for no profile.
  running_config:
    description: The state-parsed running config (output of C(info configure dist-service flat)).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
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
- name: Configure a distributed service
  nokia.isam.isam_dist_service:
    config:
      - name: "100"
        service_type: epipe
        qos_profile: gold
    state: merged

- name: Gather all distributed services
  nokia.isam.isam_dist_service:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_dist_service:
    config:
      - name: "100"
    state: gathered
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dist_service.dist_service import Isam_dist_serviceArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dist_service.dist_service import Isam_dist_service


def main():
    """Main entry point for module execution."""
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
