#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_qos_global
short_description: Manages Nokia ISAM global QoS settings.
description:
  - Manages the global C(configure qos) settings on Nokia ISAM that no other QoS
    module owns, namely the bare C(configure qos) settings, the per line card
    C(configure qos global <lt>) settings, the DSL/NNI control packet policers,
    the per protocol line control packet policers, P-bit scheduling and the QoS
    handling of upstream protocols on DSL line cards.
  - QoS interfaces, profiles, TCAs and the maps are managed by M(nokia.isam.isam_qos_interfaces),
    M(nokia.isam.isam_qos_profiles), M(nokia.isam.isam_qos_tca) and M(nokia.isam.isam_qos_maps).
  - Values equal to the device default (C(no X) in detailed output) are not reported;
    setting an option to its default is idempotent.
  - Unknown keywords and unknown enumeration values in device output are ignored.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against the CLI help of Nokia ISAM 6.2.04ng and lab device output.
  - This module works with connection C(network_cli).
  - The bare C(configure qos) settings (I(general)) have no CLI node of their own; reading
    them takes C(info configure qos flat), which also returns all QoS interface, profile, TCA
    and map lines. That read is only made when I(general) is in scope (no I(config),
    I(config.general) given, or I(state=overridden)); otherwise one
    C(info configure qos <node> flat) per section is read.
options:
  config:
    description: The global QoS configuration.
    type: dict
    suboptions:
      general:
        description: The bare C(configure qos) settings.
        type: dict
        suboptions:
          atm_overhead_fact:
            description: ATM overhead factor in percent (1-100, default 85).
            type: int
          eth_efm_fact:
            description: Ethernet EFM overhead factor in percent (1-100, default 97).
            type: int
          enable_alignment:
            description: DSCP to P-bit alignment for all forwarded L3 traffic (default disabled).
            type: bool
          cac_mode:
            description: Global connection admission control mode (default C(msr)).
            type: str
            choices: [nocac, msr, alr]
          use_dei:
            description: Global control of DEI awareness (default disabled).
            type: bool
          set_dei:
            description: Global control of DEI remarking (default disabled).
            type: bool
      line_cards:
        description:
          - Board-level queue and performance settings, C(configure qos global <lt>).
          - Line cards whose settings are all default are not reported.
        type: list
        elements: dict
        suboptions:
          name:
            description: Line card, as printed by the device (C(lt:1/1/2)); C(1/1/2) is accepted too.
            type: str
            required: true
          buffer_occ_thresh:
            description: Partial buffer occupancy alarm threshold in percent (0-100, default 0).
            type: int
          queue_stats:
            description: Generate queue statistics (default disabled).
            type: bool
          dsload_tca:
            description: Downstream card-level load threshold crossing alarm (default disabled).
            type: bool
          dsload_thresh:
            description: Downstream fan-out load alarm threshold in percent (0-100, default 0).
            type: int
          buffer_tca:
            description: Aggregation buffer overflow threshold crossing alarm (default disabled).
            type: bool
          up_buf_thresh:
            description: Upstream aggregation buffer overflow TCA threshold (default 0).
            type: int
          up_obc_thresh:
            description: OBC-directed upstream aggregation buffer overflow TCA threshold (default 0).
            type: int
          dn_obc_thresh:
            description: OBC-directed downstream aggregation buffer overflow TCA threshold (default 0).
            type: int
          dn_buf_thresh:
            description: Downstream data aggregation buffer overflow TCA threshold (default 0).
            type: int
          part_buf_thresh:
            description: Dropped lower class packets of global buffer occupancy TCA threshold (default 0).
            type: int
      dsl_ctrl_pkt_policer:
        description: The upstream DSL control packet policer, C(configure qos dsl-ctrl-pkt-policer).
        type: dict
        suboptions:
          sustained_rate:
            description: Maximum sustainable rate in packets/s (1-64, default 15).
            type: int
          burst_size:
            description: Maximum burst size in packets (1-128, default 10).
            type: int
          protocol_ctrl:
            description: Police ARP/RIP packets handled as data packets (default C(police-arprip)).
            type: str
            choices: [police-arprip, nopolice-arprip]
      nni_ctrl_pkt_policer:
        description: The NNI control packet policer, C(configure qos nni-ctrl-pkt-policer).
        type: dict
        suboptions:
          sustained_rate:
            description: Maximum sustainable rate in packets/s (1-256, default 64).
            type: int
          burst_size:
            description: Maximum burst size in packets (1-256, default 128).
            type: int
      ctrl_pkt_policer:
        description:
          - Per protocol line control packet policers, C(configure qos ctrl-pkt-policer <protocol>).
          - Entries are created per protocol and removed with C(configure qos no ctrl-pkt-policer <protocol>).
        type: list
        elements: dict
        suboptions:
          protocol:
            description: Protocol, one of C(arp), C(igmp), C(dhcpv4), C(dhcpv6), C(icmpv6), C(cfm), C(pppox).
            type: str
            required: true
          sustained_rate:
            description: Sustained rate in packets/s (1-64, default 15).
            type: int
          burst_size:
            description: Burst size in packets (1-128, default 10).
            type: int
      pbit_scheduling:
        description: P-bit based scheduling for the S+C VLAN forwarder, C(configure qos pbit-scheduling).
        type: dict
        suboptions:
          sc_xcon_us:
            description: S+C cross connect, upstream (default C(svlanpbitbased)).
            type: str
            choices: [svlanpbitbased, cvlanpbitbased]
          sc_xcon_dn:
            description: S+C cross connect, downstream (default C(svlanpbitbased)).
            type: str
            choices: [svlanpbitbased, cvlanpbitbased]
          sc_rb_us:
            description: S+C residential bridge, upstream (default C(svlanpbitbased)).
            type: str
            choices: [svlanpbitbased, cvlanpbitbased]
          sc_rb_dn:
            description: S+C residential bridge, downstream (default C(cvlanpbitbased)).
            type: str
            choices: [svlanpbitbased, cvlanpbitbased]
      upstr_prot_dsl:
        description: QoS handling of upstream protocols on DSL line cards, C(configure qos upstr-prot-dsl).
        type: dict
        suboptions:
          enable:
            description: Enable QoS handling of upstream protocols (default disabled).
            type: bool
  running_config:
    description:
      - 'Device configuration to parse with I(state=parsed) (output of C(info configure qos flat)).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - C(merged) sets the given options. C(replaced) also resets the options a given section
      or line card omits; ctrl-pkt-policer entries not named are kept. C(overridden) also
      resets every section and line card not given and removes ctrl-pkt-policer entries not given.
    - C(deleted) without I(config) resets everything to the defaults and removes all ctrl-pkt-policer
      entries; with I(config) only the sections it names (an empty dict or list names the whole
      section), for I(line_cards) and I(ctrl_pkt_policer) only the named entries if any are named.
    - With C(gathered) and I(config.line_cards), only the named line cards are read from the device,
      selected by C(name) (targeted gathering). Other fields are ignored and absent line cards are
      not returned; a line card with only default values is read with C(flat detail) and returned
      with its name only, and C(read_outcomes) reports each named line card present or confirmed
      absent where the device allows it. With other sections in I(config) only those sections are read; without
      I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Merge global QoS settings
  nokia.isam.isam_qos_global:
    config:
      general:
        cac_mode: alr
        enable_alignment: true
      line_cards:
        - name: lt:1/1/2
          queue_stats: true
          dsload_tca: true
          dsload_thresh: 80
      dsl_ctrl_pkt_policer:
        sustained_rate: 20
      pbit_scheduling:
        sc_rb_dn: svlanpbitbased
    state: merged

# Commands:
# configure qos enable-alignment cac-mode alr
# configure qos global lt:1/1/2 queue-stats dsload-tca dsload-thresh 80
# configure qos dsl-ctrl-pkt-policer sustained-rate 20
# configure qos pbit-scheduling sc-rb-dn svlanpbitbased

- name: Read only the named line cards (targeted gathering)
  nokia.isam.isam_qos_global:
    config:
      line_cards:
        - name: lt:1/1/2
    state: gathered

- name: Reset the DSL control packet policer to its defaults
  nokia.isam.isam_qos_global:
    config:
      dsl_ctrl_pkt_policer: {}
    state: deleted

# Commands (when only sustained_rate differed from the default):
# configure qos dsl-ctrl-pkt-policer no sustained-rate

- name: Parse device output
  nokia.isam.isam_qos_global:
    running_config: |
      configure qos no atm-overhead-fact no eth-efm-fact enable-alignment no cac-mode no use-dei no set-dei
      configure qos global lt:1/1/2 no buffer-occ-thresh queue-stats no dsload-tca
    state: parsed
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
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With I(running_config) (offline preview) they are rendered only, never sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
  sample:
  - configure qos cac-mode nocac
  - configure qos global lt:1/1/2 queue-stats
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
  sample:
  - configure qos upstr-prot-dsl enable
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_global.qos_global import (
    Qos_globalArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_global.qos_global import (
    Qos_global,
)


def main():
    module = AnsibleModule(
        argument_spec=Qos_globalArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Qos_global(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
