#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_channel_pair_pm
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_channel_pair_pm
short_description: Manages Nokia ISAM channel-pair FEC and TC layer PM collection.
description:
  - Manages C(configure channel-pair interface <name> fec-tc-layer|xg-tc-layer pm-collect) on Nokia ISAM.
  - Platforms without channel-pair support (C(invalid token)) have no instances.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Channel-pair interfaces.
    type: list
    elements: dict
    suboptions:
      name:
        description: Channel-pair interface (e.g. 1/1/5/3).
        type: str
        required: true
      fec_tc_layer:
        description: PM collection on the FEC TC layer.
        type: str
        choices: [enable, disable]
      xg_tc_layer:
        description: PM collection on the XG TC layer.
        type: str
        choices: [enable, disable]
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
  nokia.isam.isam_channel_pair_pm:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_channel_pair_pm:
    config:
      - name: 1/1/5/3
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.channel_pair_pm.channel_pair_pm import Channel_pair_pmArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_variants.pon_variants import Channel_pair_pm


def main():
    module = AnsibleModule(argument_spec=Channel_pair_pmArgs.argument_spec, mutually_exclusive=[["config", "running_config"]], required_if=[["state", x, ["config"]] for x in ("merged", "replaced", "overridden", "rendered")] + [["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Channel_pair_pm(module).execute_module())

if __name__ == "__main__": main()
