#!/usr/bin/python
MODULE_DESCRIPTION = """
module: isam_efm_oam_interface
short_description: Manage Nokia ISAM EFM OAM interfaces
description: Manage Nokia ISAM EFM OAM interfaces.
options:
  config:
    type: list
  running_config:
    type: str
  state:
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.efm_oam.efm_oam import EfmOamArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.efm_oam.efm_oam import EfmOam


def main():
    module = AnsibleModule(
        argument_spec=EfmOamArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**EfmOam(module).execute_module())


if __name__ == "__main__":
    main()

DOCUMENTATION = """
module: isam_efm_oam_interface
short_description: Manage Nokia ISAM EFM OAM interfaces
description:
  - Manages C(configure efm-oam interface) on Nokia ISAM.
version_added: 0.3.13
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The EFM OAM interface configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Interface, e.g. C(1/1/5/1/3/1/1).
      admin_up:
        type: bool
        description: Enable EFM OAM on the interface.
      passive_mode:
        type: bool
        description: Passive mode.
      keep_alive_intvl:
        type: str
        description: Keep-alive interval.
      response_intvl:
        type: str
        description: Response interval.
  running_config:
    description: Device configuration to parse with I(state=parsed).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Merge the configuration of one port
  nokia.isam.isam_efm_oam_interface:
    config:
      - name: 1/1/5/1/3/1/1
        admin_up: true
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_efm_oam_interface:
    config:
      - name: 1/1/5/1/3/1/1
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
