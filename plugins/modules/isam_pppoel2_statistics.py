#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_pppoel2_statistics
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_pppoel2_statistics
short_description: Manages Nokia ISAM PPPoE-L2 statistics collection.
description:
  - Manages C(configure pppoel2 statistics <vlan-port>) on Nokia ISAM.
  - The write states read C(info configure pppoel2 statistics flat) and compare against it; a device error fails the module.
  - Ports with statistics enabled are the configured instances; removal is C(no statistics <vlan-port>).
    C(vlan-port <port>) and C(vlan-port:<port>) name the same port.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: VLAN ports with PPPoE-L2 statistics settings.
    type: list
    elements: dict
    suboptions:
      name:
        description: VLAN port, as shown after C(statistics) in the device output.
        type: str
        required: true
      enabled:
        description: Collect the extensive PPPoE-L2 statistics.
        type: bool
        default: true
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned. Without I(config) the whole resource is read.
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
- name: Gather the whole resource
  nokia.isam.isam_pppoel2_statistics:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_pppoel2_statistics:
    config:
      - name: vlan-port:1/1/1/1/3:100
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pppoel2.pppoel2 import Pppoel2Args
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pppoel2.pppoel2 import Pppoel2


def main():
    module = AnsibleModule(
        argument_spec=Pppoel2Args.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[["state", "merged", ["config"]], ["state", "replaced", ["config"]],
                     ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
                     ["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**Pppoel2(module).execute_module())


if __name__ == "__main__":
    main()
