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
    description:
      - 'The state-parsed running config.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(uni_idx) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)
read_outcomes:
  description:
    - Sanitized per-instance read outcomes for a targeted read (I(state) is C(gathered)
      and I(config) names instances).
    - Each outcome names the config section that addressed the instance (for example
      C(config)) and the selector -- the instance identity, a composite identity
      recorded joined by C(/). Instances in different sections that share an identity
      value are different instances and are reported separately.
    - Each outcome records the command axis (C(ok), C(rejected) or C(failed)) and the
      instance-existence axis (C(present), C(confirmed_absent) or C(unknown)).
    - Only C(confirmed_absent) is evidence the instance is gone -- the device's explicit
      "instance does not exist" about that instance, or a header-only reply to its
      C(flat detail) read (which prints every existing instance, also one with defaults
      only). C(unknown) (an invalid-token rejection, a missing dependency, another
      instance's line, a setting whose reads never show it, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(failed) or C(unverified)) is reported at resource level under
      C(parse); C(failed) means the family parser could not process the reply,
      C(unverified) that no parser records its coverage of the reply (a read never claims
      a complete parse).
    - A named instance the device rejected (C(invalid token)) is missing from C(gathered)
      exactly like an absent one; the module also warns, naming the rejected selectors.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.0.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With C(deleted) and I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: list
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With C(deleted) and I(running_config) (offline preview of the removal) they are rendered only, never
    sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: list
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: list
# END resource_returns
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
