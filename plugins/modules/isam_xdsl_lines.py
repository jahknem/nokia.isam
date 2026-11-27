#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_lines
short_description: Manages XDSL line attributes of Nokia ISAM.
description:
  - Manages C(configure xdsl line) settings on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Initial implementation covers fields observed on live C(info configure xdsl line).
options:
  config:
    description: List of XDSL lines to configure.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        aliases: [if_index]
        description: XDSL line interface index, for example C(1/1/3/1).
      service_profile:
        type: str
        aliases: [service-profile]
        description: Service profile reference.
      spectrum_profile:
        type: str
        aliases: [spectrum-profile]
        description: Spectrum profile reference.
      dpbo_profile:
        type: str
        aliases: [dpbo-profile]
        description: DPBO profile reference.
      vect_profile:
        type: str
        aliases: [vect-profile]
        description: Vectoring profile reference.
      admin_up:
        type: bool
        aliases: [admin-up]
        description: Administrative state of the XDSL line.
      rtx_profile:
        type: str
        aliases: [rtx-profile]
        description: Retransmission (RTX) profile reference; C(no rtx-profile) is not reported.
      sos_profile:
        type: str
        aliases: [sos-profile]
        description: SOS profile reference; C(no sos-profile) is not reported.
      ansi_t1413:
        type: bool
        description: Allow the C(ansi-t1413) operating mode on the line; C(no ansi-t1413) reads as C(false).
      etsi_dts:
        type: bool
        description: Allow the C(etsi-dts) operating mode on the line; C(no etsi-dts) reads as C(false).
      g992_1_a:
        type: bool
        description: Allow the C(g992-1-a) operating mode on the line; C(no g992-1-a) reads as C(false).
      g992_1_b:
        type: bool
        description: Allow the C(g992-1-b) operating mode on the line; C(no g992-1-b) reads as C(false).
      g992_2_a:
        type: bool
        description: Allow the C(g992-2-a) operating mode on the line; C(no g992-2-a) reads as C(false).
      g992_3_a:
        type: bool
        description: Allow the C(g992-3-a) operating mode on the line; C(no g992-3-a) reads as C(false).
      g992_3_b:
        type: bool
        description: Allow the C(g992-3-b) operating mode on the line; C(no g992-3-b) reads as C(false).
      g992_3_aj:
        type: bool
        description: Allow the C(g992-3-aj) operating mode on the line; C(no g992-3-aj) reads as C(false).
      g992_3_l1:
        type: bool
        description: Allow the C(g992-3-l1) operating mode on the line; C(no g992-3-l1) reads as C(false).
      g992_3_l2:
        type: bool
        description: Allow the C(g992-3-l2) operating mode on the line; C(no g992-3-l2) reads as C(false).
      g992_3_am:
        type: bool
        description: Allow the C(g992-3-am) operating mode on the line; C(no g992-3-am) reads as C(false).
      g992_5_a:
        type: bool
        description: Allow the C(g992-5-a) operating mode on the line; C(no g992-5-a) reads as C(false).
      g992_5_b:
        type: bool
        description: Allow the C(g992-5-b) operating mode on the line; C(no g992-5-b) reads as C(false).
      ansi_t1_424:
        type: bool
        description: Allow the C(ansi-t1.424) operating mode on the line (CLI keyword contains a dot; the option uses an underscore); C(no ansi-t1.424) reads as C(false).
      etsi_ts:
        type: bool
        description: Allow the C(etsi-ts) operating mode on the line; C(no etsi-ts) reads as C(false).
      itu_g993_1:
        type: bool
        description: Allow the C(itu-g993-1) operating mode on the line; C(no itu-g993-1) reads as C(false).
      ieee_802_3ah:
        type: bool
        description: Allow the C(ieee-802.3ah) operating mode on the line (CLI keyword contains a dot; the option uses an underscore); C(no ieee-802.3ah) reads as C(false).
      g992_5_aj:
        type: bool
        description: Allow the C(g992-5-aj) operating mode on the line; C(no g992-5-aj) reads as C(false).
      g992_5_am:
        type: bool
        description: Allow the C(g992-5-am) operating mode on the line; C(no g992-5-am) reads as C(false).
      g993_2_8a:
        type: bool
        description: Allow the C(g993-2-8a) operating mode on the line; C(no g993-2-8a) reads as C(false).
      g993_2_8b:
        type: bool
        description: Allow the C(g993-2-8b) operating mode on the line; C(no g993-2-8b) reads as C(false).
      g993_2_8c:
        type: bool
        description: Allow the C(g993-2-8c) operating mode on the line; C(no g993-2-8c) reads as C(false).
      g993_2_8d:
        type: bool
        description: Allow the C(g993-2-8d) operating mode on the line; C(no g993-2-8d) reads as C(false).
      g993_2_12a:
        type: bool
        description: Allow the C(g993-2-12a) operating mode on the line; C(no g993-2-12a) reads as C(false).
      g993_2_12b:
        type: bool
        description: Allow the C(g993-2-12b) operating mode on the line; C(no g993-2-12b) reads as C(false).
      g993_2_17a:
        type: bool
        description: Allow the C(g993-2-17a) operating mode on the line; C(no g993-2-17a) reads as C(false).
      g993_2_30a:
        type: bool
        description: Allow the C(g993-2-30a) operating mode on the line; C(no g993-2-30a) reads as C(false).
      g993_2_35b:
        type: bool
        description: Allow the C(g993-2-35b) operating mode on the line; C(no g993-2-35b) reads as C(false).
      imp_noise_sensor:
        type: bool
        description: Impulse noise sensor (C(imp-noise-sensor)); C(no imp-noise-sensor) reads as C(false).
      auto_switch:
        type: bool
        description: Automatic switching (C(auto-switch)); C(no auto-switch) reads as C(false).
      carrier_data_mode:
        type: str
        choices: ['off', 'on', on-init]
        description: Carrier data mode (C(carrier-data-mode)); C(no carrier-data-mode) is not reported.
      transfer_mode:
        type: str
        choices: [atm, ptm, system-default]
        description: Transfer mode (C(transfer-mode)); C(no transfer-mode) is not reported.
      vect_qln_mode:
        type: str
        choices: [without-cancel, with-cancel]
        description: Vectoring QLN mode (C(vect-qln-mode)); C(no vect-qln-mode) is not reported.
      vect_fallback:
        type: str
        choices: [auto, forced]
        description: Vectoring fallback (C(vect-fallback)); C(no vect-fallback) is not reported.
      tca_line_threshold:
        type: dict
        description:
          - Threshold crossing alert thresholds of the line (C(configure xdsl line <if-index> tca-line-threshold)).
          - A threshold is set with C(tca-line-threshold <attr> <value>) and reset with C(tca-line-threshold no <attr>);
            C(enable) is set with C(tca-line-threshold enable) and reset with C(tca-line-threshold no enable).
          - Defaults (C(no enable), C(no <attr>) or a threshold of C(0)) are not reported, and a requested C(0) or
            C(false) equals an absent value.
          - Syntax from the CLI reference; the set and reset forms are not verified on a device.
        suboptions:
          enable:
            type: bool
            description: Report TCAs for this line (C(enable)).
          es_nearend:
            type: int
            description: C(es-nearend) threshold (errored seconds near end, 15 min, 0-900; 0 disables).
          ses_nearend:
            type: int
            description: C(ses-nearend) threshold (severely errored seconds near end, 15 min, 0-900; 0 disables).
          uas_nearend:
            type: int
            description: C(uas-nearend) threshold (unavailable seconds near end, 15 min, 0-900; 0 disables).
          leftr_nearend:
            type: int
            description: C(leftr-nearend) threshold (leftr seconds near end, 15 min, 0-900; 0 disables).
          leftr_day_nearend:
            type: int
            description: C(leftr-day-nearend) threshold (leftr seconds near end, 1 day, 0-86400; 0 disables).
          es_day_nearend:
            type: int
            description: C(es-day-nearend) threshold (errored seconds near end, 1 day, 0-86400; 0 disables).
          ses_day_nearend:
            type: int
            description: C(ses-day-nearend) threshold (severely errored seconds near end, 1 day, 0-86400; 0 disables).
          uas_day_nearend:
            type: int
            description: C(uas-day-nearend) threshold (unavailable seconds near end, 1 day, 0-86400; 0 disables).
          es_farend:
            type: int
            description: C(es-farend) threshold (errored seconds far end, 15 min, 0-900; 0 disables).
          ses_farend:
            type: int
            description: C(ses-farend) threshold (severely errored seconds far end, 15 min, 0-900; 0 disables).
          uas_farend:
            type: int
            description: C(uas-farend) threshold (unavailable seconds far end, 15 min, 0-900; 0 disables).
          es_day_farend:
            type: int
            description: C(es-day-farend) threshold (errored seconds far end, 1 day, 0-86400; 0 disables).
          ses_day_farend:
            type: int
            description: C(ses-day-farend) threshold (severely errored seconds far end, 1 day, 0-86400; 0 disables).
          uas_day_farend:
            type: int
            description: C(uas-day-farend) threshold (unavailable seconds far end, 1 day, 0-86400; 0 disables).
          leftr_farend:
            type: int
            description: C(leftr-farend) threshold (leftr seconds far end, 15 min, 0-900; 0 disables).
          leftr_day_farend:
            type: int
            description: C(leftr-day-farend) threshold (leftr seconds far end, 1 day, 0-86400; 0 disables).
          reinit:
            type: int
            description: C(reinit) threshold (re-initialisations, 15 min, 0-2147483647; 0 disables).
          reinit_day:
            type: int
            description: C(reinit-day) threshold (re-initialisations, 1 day, 0-2147483647; 0 disables).
  running_config:
    description:
      - 'Native C(info configure xdsl line) output to parse.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - B(WARNING) - C(overridden) resets every line not listed in I(config), and C(deleted) resets every line
        named by its identity alone (every line without I(config)). The reset includes C(no admin-up), which
        takes those lines administratively down and drops their service. List every line that must stay up
        (with C(admin_up=true)), or name single attributes with C(deleted).
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
- name: Configure an XDSL line
  nokia.isam.isam_xdsl_lines:
    config:
      - name: 1/1/3/1
        service_profile: "13"
        spectrum_profile: "2"
        dpbo_profile: "1"
        vect_profile: "10"
        admin_up: true
    state: merged

- name: Gather XDSL line facts
  nokia.isam.isam_xdsl_lines:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_xdsl_lines:
    config:
      - name: 1/1/3/1
    state: gathered

- name: Enable TCA reporting with a 15 min errored seconds threshold
  nokia.isam.isam_xdsl_lines:
    config:
      - name: 1/1/3/1
        tca_line_threshold:
          enable: true
          es_nearend: 10
    state: merged
# - configure xdsl line 1/1/3/1 tca-line-threshold enable es-nearend 10
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
    - Only C(confirmed_absent) -- the device's explicit "instance does not exist" signal
      about that instance -- is evidence the instance is gone. C(unknown) (a header-only
      reply, an invalid-token rejection, a missing dependency, or a failed read) is never
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
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With I(running_config) (offline preview) it is the supplied configuration.
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
  - With I(running_config) (offline preview) they are rendered only, never sent.
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_lines.xdsl_lines import (
    Xdsl_linesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_lines.xdsl_lines import (
    Xdsl_lines,
)


def main():
    """Main entry point for module execution."""
    module = AnsibleModule(
        argument_spec=Xdsl_linesArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Xdsl_lines(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
