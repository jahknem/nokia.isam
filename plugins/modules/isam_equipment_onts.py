#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_equipment_onts
short_description: Manages equipment ONT configuration on Nokia ISAM.
description:
  - Manages C(configure equipment ont) interface, slot, software control, loop detection and PM collection entries.
  - Keywords in device output that are not modelled are ignored; they never make a read fail.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    type: dict
    description: Equipment ONT configuration.
    suboptions:
      interfaces:
        description: ONT interface entries.
        type: list
        elements: dict
        suboptions:
          ont_idx:
            description: ONT interface index.
            type: str
            required: true
          sw_ver_pland:
            description: Planned software version mode.
            type: str
          sernum:
            description: ONT serial number.
            type: str
          subslocid:
            description: Subscriber location ID.
            type: str
          fec_up:
            description: Upstream FEC setting.
            type: str
          sw_dnload_version:
            description: Software download version mode.
            type: str
          plnd_var:
            description: Planned ONT variant.
            type: str
          enable_aes:
            description: AES enable setting.
            type: str
          log_auth_pwd:
            description: Logical authentication password.
            type: str
          cvlantrans_mode:
            description: C-VLAN translation mode.
            type: str
          planned_us_rate:
            description: Planned upstream rate.
            type: str
          bridge_map_mode:
            description: ONT bridge mapping mode.
            type: str
            choices: [1-mp-bridge-map-filter, n-p-bridge-map-filter, n-mp-bridge-map-filter]
          ont_enable:
            description: ONT enable mode.
            type: str
            choices: [auto, disable, enable]
          p2p_enable:
            description: Point-to-point enable mode.
            type: str
            choices: [disable, enable]
          optics_hist:
            description: Optical history collection mode.
            type: str
            choices: [disable, enable]
          voip_allowed:
            description: Voice-over-IP allowance mode.
            type: str
            choices: [disable, enable, iphost, veip]
          iphc_allowed:
            description: IP host connectivity allowance mode.
            type: str
            choices: [disable, enable]
          battery_bkup:
            description:
              - Battery backup (C(battery-bkup)), C(disable) or C(enable); device default C(disable).
            type: str
          berint:
            description:
              - Accumulation interval in downstream frames for the ONU BER calculation (C(berint)), 8000-100000; device default C(8000).
            type: str
          desc1:
            description:
              - Free-form ONT description 1 (C(desc1)), at most 64 characters; device default empty.
            type: str
          desc2:
            description:
              - Free-form ONT description 2 (C(desc2)), at most 64 characters; device default empty.
            type: str
          provversion:
            description:
              - Provisioned version number (C(provversion)); device default C(*).
            type: str
          pwr_shed_prof_id:
            description:
              - Power shed profile index (C(pwr-shed-prof-id)), C(none) or 0-50; device default C(none).
            type: str
          rf_filter:
            description:
              - RF video filter (C(rf-filter)), one of C(pass-none), C(pass-low), C(pass-low-high), C(pass-low-middle);
                device default C(pass-low-high).
            type: str
          us_police_mode:
            description:
              - Upstream police mode (C(us-police-mode)), C(local), C(remote) or the obsolete C(network); device default C(local).
            type: str
          slid_visibility:
            description:
              - SLID visibility (C(slid-visibility)), C(disabled), C(enabled-slid-on) or C(enabled-all); device default C(disabled).
            type: str
          log_auth_id:
            description:
              - Logical authentication id of the ONT (C(log-auth-id)), at most 24 characters; device default empty.
            type: str
          sn_bundle_ctrl:
            description:
              - Serial number bundling with SLID/LOID (C(sn-bundle-ctrl)), C(unbundle), C(bundle) or C(auto); device default C(unbundle).
            type: str
          pland_cfgfile1:
            description:
              - Planned configuration file 1 version (C(pland-cfgfile1)); device default C(DISABLED).
            type: str
          pland_cfgfile2:
            description:
              - Planned configuration file 2 version (C(pland-cfgfile2)); device default C(DISABLED).
            type: str
          dnload_cfgfile1:
            description:
              - Configuration file 1 version to download (C(dnload-cfgfile1)); device default C(DISABLED).
            type: str
          dnload_cfgfile2:
            description:
              - Configuration file 2 version to download (C(dnload-cfgfile2)); device default C(DISABLED).
            type: str
          us_tcpolice_mode:
            description:
              - Upstream TC (GEM port) police mode (C(us-tcpolice-mode)), C(local) or C(remote); device default C(local).
            type: str
          oltdscppbitalign:
            description:
              - Whether the OLT aligns DSCP to P-bit for this ONU (C(oltdscppbitalign)), C(disable) or C(enable); device default C(disable).
            type: str
          ratelimit_us_dhcp:
            description:
              - Upstream DHCP rate limit in packets per second (C(ratelimit-us-dhcp)), 0 (disabled) to 16; device default C(10).
            type: str
          ratelimit_us_arp:
            description:
              - Upstream ARP rate limit in packets per second (C(ratelimit-us-arp)), 0 (disabled) to 16; device default C(10).
            type: str
          flush_mac:
            description:
              - Flush learned MACs when UNIs of this ONT go down (C(flush-mac)), C(disable) or C(enable); device default C(disable).
            type: str
          template_name:
            description:
              - ONU auto-provisioning template name (C(template-name)), at most 20 characters; device default C(DEFAULT).
            type: str
          evtocd:
            description:
              - Extended VLAN tagging operation configuration data ME control (C(evtocd)), C(disable) or C(enable); device default C(enable).
            type: str
          vtfd:
            description:
              - VLAN tagging filter data ME control (C(vtfd)), C(disable) or C(enable); device default C(enable).
            type: str
          pwr_shed_prof_name:
            description:
              - Power shed profile name (C(pwr-shed-prof-name)) as displayed by the device.
              - The CLI help lists it only as a display parameter; a value given here is rendered as C(pwr-shed-prof-name <value>),
                which is unverified on the device. Prefer O(config.interfaces[].pwr_shed_prof_id) for writes.
            type: str
          admin_state:
            description: Administrative state.
            type: str
            choices: [up, down]
          tc_layer:
            description:
              - TC-layer performance monitor collection (C(configure equipment ont interface <ont-idx> tc-layer)).
              - A field is set with C(tc-layer <attr> <value>) and reset with C(tc-layer no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              olt_pm_collect:
                description: Value of C(olt-pm-collect).
                type: str
              od_pm_collect:
                description: Value of C(od-pm-collect).
                type: str
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
          tc_layer_threshold:
            description:
              - TC-layer threshold crossing alert thresholds (C(configure equipment ont interface <ont-idx> tc-layer-threshold)).
              - A field is set with C(tc-layer-threshold <attr> <value>) and reset with C(tc-layer-threshold no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              lost_frags_down:
                description: Value of C(lost-frags-down).
                type: str
              lost_frags_up:
                description: Value of C(lost-frags-up).
                type: str
              bad_headers_down:
                description: Value of C(bad-headers-down).
                type: str
          mcast_tc_layer:
            description:
              - Multicast TC-layer performance monitor collection (C(configure equipment ont interface <ont-idx> mcast-tc-layer)).
              - A field is set with C(mcast-tc-layer <attr> <value>) and reset with C(mcast-tc-layer no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
          fec_tc_layer:
            description:
              - FEC TC-layer performance monitor collection (C(configure equipment ont interface <ont-idx> fec-tc-layer)).
              - A field is set with C(fec-tc-layer <attr> <value>) and reset with C(fec-tc-layer no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              olt_pm_collect:
                description: Value of C(olt-pm-collect).
                type: str
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
          ethernet:
            description:
              - Ethernet performance monitor collection (C(configure equipment ont interface <ont-idx> ethernet)).
              - A field is set with C(ethernet <attr> <value>) and reset with C(ethernet no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
          xg_tc_layer:
            description:
              - XG TC-layer performance monitor collection (C(configure equipment ont interface <ont-idx> xg-tc-layer)).
              - A field is set with C(xg-tc-layer <attr> <value>) and reset with C(xg-tc-layer no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              olt_pm_collect:
                description: Value of C(olt-pm-collect).
                type: str
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
          phy_layer:
            description:
              - Physical layer performance monitor collection (C(configure equipment ont interface <ont-idx> phy-layer)).
              - A field is set with C(phy-layer <attr> <value>) and reset with C(phy-layer no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              olt_pm_collect:
                description: Value of C(olt-pm-collect).
                type: str
          delay_act:
            description:
              - Delayed software activation (C(configure equipment ont interface <ont-idx> delay-act)).
              - A field is set with C(delay-act <attr> <value>) and reset with C(delay-act no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              at:
                description: Value of C(at).
                type: str
          cpu_load:
            description:
              - ONT CPU load performance monitor collection (C(configure equipment ont interface <ont-idx> cpu-load)).
              - A field is set with C(cpu-load <attr> <value>) and reset with C(cpu-load no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
          memory_usage:
            description:
              - ONT memory usage performance monitor collection (C(configure equipment ont interface <ont-idx> memory-usage)).
              - A field is set with C(memory-usage <attr> <value>) and reset with C(memory-usage no <attr>); a field at its default (C(no <attr>)) is not reported.
              - No CLI help is available for this sub-node; values are passed to the device as given.
            type: dict
            suboptions:
              ont_pm_collect:
                description: Value of C(ont-pm-collect).
                type: str
      slots:
        description: ONT slot entries.
        type: list
        elements: dict
        suboptions:
          ont_slot_idx:
            description: ONT slot index.
            type: str
            required: true
          planned_card_type:
            description: Planned card type.
            type: str
          plndnumdataports:
            description: Planned number of data ports.
            type: int
          plndnumvoiceports:
            description: Planned number of voice ports.
            type: int
          port_type:
            description: Port type.
            type: str
          transp_mode_rem:
            description: Transparent mode remote setting.
            type: str
          no_mcast_control:
            description: Multicast control setting.
            type: str
          admin_state:
            description: Administrative state.
            type: str
            choices: [up, down]
      sw_ctrls:
        description: ONT software control entries.
        type: list
        elements: dict
        suboptions:
          sw_ctrl_id:
            description: Software control ID.
            type: int
            required: true
          hw_version:
            description: Hardware version match.
            type: str
          ont_variant:
            description: ONT variant.
            type: str
          plnd_sw_version:
            description: Planned software version.
            type: str
          plnd_sw_ver_conf:
            description: Planned software version confirmation.
            type: str
          sw_dwload_ver:
            description: Software download version.
            type: str
          pland_cfgfile1:
            description: Planned configuration file 1 version (C(pland-cfgfile1)); C(no pland-cfgfile1) resets it to C(DISABLED).
            type: str
          pland_cfgfile2:
            description: Planned configuration file 2 version (C(pland-cfgfile2)); C(no pland-cfgfile2) resets it to C(DISABLED).
            type: str
          dnload_cfgfile1:
            description: Download configuration file 1 version (C(dnload-cfgfile1)); C(no dnload-cfgfile1) resets it to C(DISABLED).
            type: str
          dnload_cfgfile2:
            description: Download configuration file 2 version (C(dnload-cfgfile2)); C(no dnload-cfgfile2) resets it to C(DISABLED).
            type: str
          delay_act:
            description:
              - Delayed software activation (C(configure equipment ont sw-ctrl <id> delay-act)).
              - Set with C(delay-act at <value>), reset with C(delay-act no at); unset is not reported.
            type: dict
            suboptions:
              at:
                description: Activation time (C(at)), passed to the device as given.
                type: str
      loops:
        description:
          - ONT loop detection (C(configure equipment ont loop <ont-idx>)).
          - The node exists with its ONT and is not created or removed; C(deleted), C(replaced) and C(overridden)
            reset fields to the CLI default with C(no loop-detect) / C(no loop-portautoshut).
          - A field at its CLI default is not reported, and is the same as an unset field; an ONT with only defaults is not returned.
        type: list
        elements: dict
        suboptions:
          ont_idx:
            description: ONT index.
            type: str
            required: true
          loop_detect:
            description: Loop detection admin state (C(loop-detect)); CLI default C(no-control).
            type: str
            choices: [no-control, disable, enable]
          loop_portautoshut:
            description: Automatic port shutdown on a detected loop (C(loop-portautoshut)); CLI default C(enable).
            type: str
            choices: [disable, enable]
      pm_collects:
        description:
          - ONT XGS-PON performance monitor collection (C(configure equipment ont pm-collect <ont-idx>)).
          - The node exists with its ONT and is not created or removed; removal resets it with C(no xg-pm-collect).
          - The CLI default is not reported, and is the same as an unset field; an ONT with only the default is not returned.
        type: list
        elements: dict
        suboptions:
          ont_idx:
            description: ONT index.
            type: str
            required: true
          xg_pm_collect:
            description: Performance monitor collection (C(xg-pm-collect)); CLI default C(disable).
            type: str
            choices: [enable, disable]
  running_config:
    description:
      - 'Device-native running configuration to parse.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(interfaces[].ont_idx), C(slots[].ont_slot_idx), C(sw_ctrls[].sw_ctrl_id), C(loops[].ont_idx) and C(pm_collects[].ont_idx) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - With C(merged), C(replaced) or C(deleted) and I(config) naming only C(interfaces) and C(slots), the current configuration is likewise read only for the named instances.
    - Deleting an ONT (C(interfaces)) removes its C(loops) and C(pm_collects) settings with it; no reset is sent for them.
    - With C(deleted) and no I(config), or an empty I(config), all gathered ONT interfaces, slots and software-control entries are removed. Interfaces are shut down before slots and interfaces are removed. This is destructive; provide explicit identities to limit deletion.
    - Whole-entry C(deleted) reasserts C(admin-state down) separately for each removed interface and slot, even if gathered down. Before any removal, live execution waits one second and checks targeted detail readback, up to five times. Unconfirmed shutdown or a read error stops deletion; commands are never retried. Named-setting deletion does not shut down the parent object.
    - Check mode reports the same shutdown/removal plan but does not write, wait or perform readiness polling. A write or verification failure reports accepted and pending commands; read back the device before deciding whether to retry.
    - Interface and slot C(admin_state) commands are emitted separately from other creation or update parameters.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather equipment ONTs
  nokia.isam.isam_equipment_onts:
    state: gathered

- name: Render an ONT interface
  nokia.isam.isam_equipment_onts:
    state: rendered
    config:
      interfaces:
        - ont_idx: 1/1/5/1/1
          sw_ver_pland: auto
          sernum: ALCL:00000002
          admin_state: up

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_equipment_onts:
    config:
      interfaces:
        - ont_idx: 1/1/5/1/3
      slots:
        - ont_slot_idx: 1/1/5/1/3/1
    state: gathered

- name: Enable loop detection and XGS-PON PM collection of an ONT
  nokia.isam.isam_equipment_onts:
    config:
      loops:
        - ont_idx: 1/1/5/1/3
          loop_detect: enable
          loop_portautoshut: disable
      pm_collects:
        - ont_idx: 1/1/5/1/3
          xg_pm_collect: enable
    state: merged
# - configure equipment ont loop 1/1/5/1/3 loop-detect enable loop-portautoshut disable
# - configure equipment ont pm-collect 1/1/5/1/3 xg-pm-collect enable
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
    - The parse axis (C(complete), C(partial), C(failed) or C(unverified)) is reported at
      resource level under C(parse); C(unverified) means the parser did not record its
      coverage of the reply.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
commands:
  description: The set of commands pushed to the remote device.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: The provided configuration rendered in device-native format.
  returned: when state is rendered
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when state is gathered
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when state is parsed
  type: dict
accepted:
  description: Commands accepted before a staged deletion failure; this is not proof that deletion completed.
  returned: on a staged deletion failure
  type: list
  elements: str
failed_command:
  description: Command whose execution failed, or null when shutdown verification failed. Its outcome may be unknown.
  returned: on a staged deletion failure
  type: str
pending:
  description: Planned commands that were never sent after a staged deletion failure.
  returned: on a staged deletion failure
  type: list
  elements: str
failure_phase:
  description: Whether staged deletion stopped during execution or shutdown verification.
  returned: on a staged deletion failure
  type: str
completion_status:
  description: Unknown after a staged deletion failure; inspect readback before retrying.
  returned: on a staged deletion failure
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.equipment_onts.equipment_onts import (
    Equipment_ontsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.equipment_onts.equipment_onts import (
    Equipment_onts,
)


def main():
    module = AnsibleModule(
        argument_spec=Equipment_ontsArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Equipment_onts(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
