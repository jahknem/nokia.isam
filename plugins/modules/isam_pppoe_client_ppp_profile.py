#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_pppoe_client_ppp_profile
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_pppoe_client_ppp_profile
short_description: Manages Nokia ISAM PPPoE client PPP profiles.
description:
  - Manages C(configure pppoe-client ppp-profile) on Nokia ISAM.
  - The write states read C(info configure pppoe-client ppp-profile flat) and compare against it; a device error fails the module.
  - Attributes at their device default (I(ipversion=ipv4), I(authproto=auto), I(mru=1500)) equal absent ones. With I(state=replaced) or C(overridden),
    attributes not given are reset (C(no ipversion) etc.); deletion uses C(no ppp-profile <name>).
  - I(client_id), I(profile_name), I(username), I(password), I(mac) and I(pbit) belong to client interfaces and are ignored here.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: PPP profiles.
    type: list
    elements: dict
    suboptions:
      name:
        description: PPP profile name.
        type: str
        required: true
      ipversion:
        description: IP version (PPP profiles).
        type: str
      authproto:
        description: Authentication protocol (PPP profiles).
        type: str
      mru:
        description: Maximum receive unit (PPP profiles).
        type: int
      client_id:
        description: PPPoE client id (client interfaces).
        type: int
      profile_name:
        description: PPP profile name (client interfaces).
        type: str
      username:
        description: User name for PPP authentication (client interfaces).
        type: str
      password:
        description: Password for PPP authentication (client interfaces).
        type: str
      mac:
        description: MAC address (client interfaces).
        type: str
      pbit:
        description: P-bit value (client interfaces).
        type: int
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
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
- name: Gather the whole resource
  nokia.isam.isam_pppoe_client_ppp_profile:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_pppoe_client_ppp_profile:
    config:
      - name: home
    state: gathered
"""

RETURN = """
extends_documentation_fragment: nokia.isam.read_outcomes
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pppoe_client.pppoe_client import PppoeClientArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pppoe_client.pppoe_client import PppoeClient


def main():
    module = AnsibleModule(
        argument_spec=PppoeClientArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[["state", "merged", ["config"]], ["state", "replaced", ["config"]],
                     ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
                     ["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**PppoeClient(module, "profile").execute_module())


if __name__ == "__main__":
    main()
