#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_ethernet_onts
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_ethernet_onts
short_description: Manages Nokia ISAM ONT Ethernet port provisioning.
description:
  - Manages C(configure ethernet ont) attributes on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Initial implementation covers live-observed ONT Ethernet UNI fields.
options:
  config:
    description: The provided ONT Ethernet port configuration.
    type: list
    elements: dict
    suboptions:
      uni_idx:
        type: str
        required: true
        aliases: [name]
        description: Identification of the ONT Ethernet UNI interface index.
      cust_info:
        type: str
        description: Customer or port information string.
      auto_detect:
        type: str
        description: Auto detection configuration.
        choices:
          - 10_100baset-auto
          - 10baset-fd
          - 100baset-fd
          - 1000baset-fd
          - auto-basetfd
          - 10gig-fd
          - 2.5gig-fd
          - 5gig-fd
          - 10baset-auto
          - 10baset-hd
          - 100baset-hd
          - 1000baset-hd
          - autobaset-hd
          - 10_100_1000baset-auto
          - 100baset-auto
          - auto
          - 1000baset-auto
      power_control:
        type: str
        description: PoE power control (C(power-control)); C(no power-control) is not reported.
        choices: [enable, disable]
      pse_class:
        type: str
        description: PSE class (C(pse-class)); C(no pse-class) is not reported.
        choices: ['0', '1', '2', '3', '4', '5']
      pse_pw_priority:
        type: str
        description: PSE power priority (C(pse-pw-priority)); C(no pse-pw-priority) is not reported.
        choices: [critical, high, low]
      pwr_override:
        type: str
        description: Power override (C(pwr-override)); C(no pwr-override) is not reported.
        choices: [enable, disable]
      lpt_mode:
        type: str
        description: Link pass-through mode (C(lpt-mode)); C(no lpt-mode) is not reported.
        choices: [not-supported, enabled, disabled]
      admin_state:
        type: str
        description: Administrative state of the interface.
        choices:
          - up
          - down
      phy:
        type: dict
        description:
          - Physical layer settings (C(configure ethernet ont <uni-idx> phy)).
          - Set with C(phy <attr> <value>), reset with C(phy no <attr>); sent as its own command, never joined
            with the UNI attributes. Syntax from the CLI reference, not verified on a device.
          - Defaults (C(no <attr>) or the default value) are not reported and a requested default equals an absent value.
        suboptions:
          pm:
            type: str
            description: Physical layer PM collection (C(pm)); device default C(disable).
            choices: [enable, disable]
      l2:
        type: dict
        description:
          - Layer 2 PM and threshold crossing alerts (C(configure ethernet ont <uni-idx> l2)).
          - Set with C(l2 <attr> <value>), reset with C(l2 no <attr>); sent as its own command. Syntax from the
            CLI reference, not verified on a device.
          - Defaults are not reported and a requested default equals an absent value.
        suboptions:
          pm:
            type: str
            description: Layer 2 PM collection (C(pm)); device default C(disable).
            choices: [enable, disable]
          tca:
            type: str
            description: Layer 2 threshold crossing alerts (C(tca)); device default C(disable).
            choices: [enable, disable]
          dropped_frames_up:
            type: str
            description: Upstream dropped frames threshold, C(disable) or 0-4294967295 (C(dropped-frames-up)); device default C(disable).
          dropped_frames_dn:
            type: str
            description: Downstream dropped frames threshold, C(disable) or 0-4294967295 (C(dropped-frames-dn)); device default C(disable).
          pm_collect_ext:
            type: dict
            description:
              - Extended 32 bit PM (C(configure ethernet ont <uni-idx> l2 pm-collect-ext)), set with
                C(l2 pm-collect-ext <attr> <value>) and reset with C(l2 pm-collect-ext no <attr>).
            suboptions:
              pm_collect:
                type: str
                description: Extended PM collection (C(pm-collect)); device default C(disable).
                choices: [enable, disable]
              p_bits:
                type: int
                description: P-bit filter of the collected PM data, 0-7, or 255 for not used (C(p-bits)); device default C(255) (0xFF).
              vlan_id:
                type: int
                description: VLAN filter of the collected PM data, 0 for not used (C(vlan-id)); device default C(0).
      cfm:
        type: dict
        description:
          - CFM settings of the UNI (C(configure ethernet ont <uni-idx> cfm)), set with C(cfm portshut-ais) and
            reset with C(cfm no portshut-ais). Syntax from the CLI reference, not verified on a device.
        suboptions:
          portshut_ais:
            type: bool
            description: Shut the UNI down on a downstream AIS PDU (C(portshut-ais)); C(no portshut-ais) is the default and not reported.
  running_config:
    description: The state-parsed running config.
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(uni_idx) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    - An Ethernet UNI has no remove command; C(deleted) resets its settings. A UNI named by C(uni_idx) alone has every setting reset, otherwise only the named settings; without I(config) every UNI is reset. Settings without a C(no) form (e.g. C(auto_detect)) are kept, with a warning.
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
- name: Render ONT Ethernet port configuration
  nokia.isam.isam_ethernet_onts:
    config:
      - uni_idx: 1/1/1/1/1/1/1
        cust_info: "Customer port 1"
        auto_detect: auto
        admin_state: up
    state: rendered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_ethernet_onts:
    config:
      - uni_idx: 1/1/5/1/3/1/1
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ethernet_onts.ethernet_onts import (
    Ethernet_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.ethernet_onts.ethernet_onts import (
    Ethernet_onts,
)


def main():
    """Main entry point for module execution."""
    module = AnsibleModule(
        argument_spec=Ethernet_ontsArgs.argument_spec,
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

    result = Ethernet_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
