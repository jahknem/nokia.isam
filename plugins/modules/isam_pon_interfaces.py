#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_pon_interfaces
short_description: Manages Nokia ISAM PON interface attributes.
description:
  - Resource module for C(configure pon interface).
version_added: 1.0.0
author: Jan Kuhnemund (@jahknem)
options:
  config:
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: PON interface index.
      label:
        type: str
        description: Label of the PON port.
      fec_dn:
        type: str
        choices: [enable, disable]
        description: Downstream FEC setting.
      ponid_interval:
        type: int
        description: Interval to send GPON-ID PLOAM message in seconds.
      ponid_identifier:
        type: str
        description: GPON ID identifier.
      tconts_per_frame:
        type: int
        description: Maximum number of TCONT containers per upstream frame.
      admin_state:
        type: str
        choices: [up, down]
        description: Administrative state of the interface.
      tc_layer:
        type: dict
        suboptions:
          pm_collect:
            type: str
            choices: [none, pm-enable, tca-enable]
            description: OLT-side aggregate TC layer PM mode.
          tca_enable:
            type: bool
            description: Convenience flag mapping to tc-layer pm-collect tca-enable when true.
  running_config:
    type: str
    description: Native running configuration for parsed state.
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
    description: Module state.
"""

EXAMPLES = """
- name: Render PON interface commands
  nokia.isam.isam_pon_interfaces:
    config:
      - name: 1/1/1/1
        label: access-pon-1
        fec_dn: enable
        ponid_interval: 10
        ponid_identifier: '00000000000001'
        tconts_per_frame: 44
        admin_state: down
        tc_layer:
          pm_collect: tca-enable
    state: rendered
"""

RETURN = """
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted)
  type: list
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: list
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), C(deleted)
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Gathered resource facts.
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description: Parsed structured data from I(running_config).
  returned: when I(state) is C(parsed)
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pon_interfaces.pon_interfaces import Pon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_interfaces.pon_interfaces import Pon_interfaces


def main():
    module = AnsibleModule(
        argument_spec=Pon_interfacesArgs.argument_spec,
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

    result = Pon_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
