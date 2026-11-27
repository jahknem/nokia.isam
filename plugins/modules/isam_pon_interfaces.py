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
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: PON interface configuration entries.
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
      ber_calc_period: {type: int, description: BER calculation period (1-864000 deciseconds).}
      polling_period: {type: int, description: PON polling period (1-864000 deciseconds).}
      sig_degrade_th: {type: int, description: Signal degradation threshold (4-10).}
      sig_fail_th: {type: int, description: Signal failure threshold (3-8).}
      raman_reduct:
        type: str
        choices: [enable, disable]
        description: Raman reduction setting.
      closest_ont: {type: int, description: Closest ONT distance in km (0-40; XGS 0-20).}
      diff_reach: {type: int, choices: [20, 34, 40], description: Differential reach in km.}
      pon_tag: {type: str, description: Up to 16 hexadecimal characters.}
      pon_id: {type: str, description: Up to 8 hexadecimal characters.}
      mcast_encrypt:
        type: str
        choices: [enable, disable]
        description: Multicast encryption setting.
      auth_method:
        type: str
        choices: [sn-slid, logical, loidpre, logical-std, loidpre-std, loid-sn-slid]
        description:
          - ONT authentication mode of the PON (C(auth-method)); device default C(sn-slid).
          - C(sn-slid) serial number and SLID, C(logical) logical, C(loidpre) LOID-precedence mix,
            C(logical-std) and C(loidpre-std) their standard variants, C(loid-sn-slid) LOID, serial number and SLID mixed.
          - Can only be changed while the interface is administratively down.
      ponid_interval:
        type: int
        description: Interval to send GPON-ID PLOAM message in seconds.
      ponid_odn:
        type: str
        choices: [a, b, bplus, c, cplus, auto]
        description: ODN profile used for PON-ID handling.
      ponid_identifier:
        type: str
        description: Exactly 14 hexadecimal characters.
      tconts_per_frame:
        type: int
        description: Maximum number of TCONT containers per upstream frame (0-64).
      max_ranging_onts: {type: int, description: Maximum number of ranging ONTs (0-128).}
      pon_speed:
        type: str
        choices: [nominal, 10g-10g, 10g-2.5g]
        description:
          - PON line rate (C(pon-speed)); device default C(nominal), the nominal rate of the PON technology.
          - C(10g-10g) is 10G down / 10G up, C(10g-2.5g) 10G down / 2.5G up.
      burst_overhead:
        type: str
        choices: [robust, reduced]
        description: Burst mode overhead (C(burst-overhead)); device default C(robust).
      onu_prov_mode:
        type: str
        choices: [semi-auto, auto]
        description:
          - ONU auto-provisioning mode (C(onu-prov-mode)); device default C(semi-auto).
          - With C(semi-auto) the template file is named in the ONT configuration; with C(auto) it is selected
            from the ONT type.
      admin_state:
        type: str
        choices: [up, down]
        description: Administrative state of the interface.
      tc_layer:
        description: TC-layer performance monitoring settings.
        type: dict
        suboptions:
          pm_collect:
            type: str
            choices: [none, pm-enable, tca-enable]
            description: OLT-side aggregate TC layer PM mode.
          tca_enable:
            type: bool
            description: Convenience flag mapping to tc-layer pm-collect tca-enable when true.
      tc_layer_threshold:
        type: dict
        description: TC-layer threshold settings.
        suboptions:
          error_frags_up: {type: str, description: Errored-fragments threshold or disabled.}
      mcast_tc_layer:
        type: dict
        description: Multicast TC-layer PM collection settings.
        suboptions:
          pm_collect: {type: str, choices: [enable, disable], description: Enable or disable multicast TC-layer PM collection.}
      phy_layer:
        type: dict
        description: Physical-layer PM collection settings.
        suboptions:
          pm_collect: {type: str, choices: [enable, disable], description: Enable or disable physical-layer PM collection.}
      fec_tc_layer:
        type: dict
        description: FEC TC-layer PM collection settings.
        suboptions:
          pm_collect: {type: str, choices: [enable, disable], description: Enable or disable FEC TC-layer PM collection.}
      xg_tc_layer:
        type: dict
        description: XG TC-layer PM collection settings.
        suboptions:
          pm_collect: {type: str, choices: [enable, disable], description: Enable or disable XG TC-layer PM collection.}
      otdr:
        type: dict
        description: OTDR mode settings.
        suboptions:
          mode: {type: str, choices: [enable, disable, test], description: OTDR operating mode.}
      utilization:
        type: dict
        description: PON and ONT utilization performance monitoring (C(configure pon interface <idx> utilization)).
        suboptions:
          pon_pmcollect:
            type: str
            choices: [none, pm-enable, tca-enable, inherit]
            description: PON utilization performance monitoring (C(pon-pmcollect)); C(inherit) (device default) takes the system-wide generic-pon value.
          ont_pmcollect:
            type: str
            choices: [enable, disable, inherit]
            description: Detailed per-ONT utilization performance monitoring (C(ont-pmcollect)); C(inherit) (device default) takes the system-wide generic-pon value.
          ontbulk_pmcollect:
            type: str
            choices: [enable, disable]
            description: ONT utilization PM bulk collection via BFMU (C(ontbulk-pmcollect)); device default C(disable).
          threshold:
            type: dict
            description: Utilization TCA thresholds (C(utilization threshold)); every value is a number or C(disabled).
            suboptions:
              txmcutilhi:
                type: str
                description: Threshold on transmitted multicast utilization (percent, 0-100) raising the high-level alarm (C(txmcutilhi)), or C(disabled) (device default).
              txmcutilmd:
                type: str
                description: Threshold on transmitted multicast utilization (percent, 0-100) raising the medium-level alarm (C(txmcutilmd)), or C(disabled) (device default).
              txmcutillo:
                type: str
                description: Threshold on transmitted multicast utilization (percent, 0-100) raising the low-level alarm (C(txmcutillo)), or C(disabled) (device default).
              txtotutilhi:
                type: str
                description: Threshold on total transmitted utilization (percent, 0-100) raising the high-level alarm (C(txtotutilhi)), or C(disabled) (device default).
              txtotutilmd:
                type: str
                description: Threshold on total transmitted utilization (percent, 0-100) raising the medium-level alarm (C(txtotutilmd)), or C(disabled) (device default).
              txtotutillo:
                type: str
                description: Threshold on total transmitted utilization (percent, 0-100) raising the low-level alarm (C(txtotutillo)), or C(disabled) (device default).
              rxtotutilhi:
                type: str
                description: Threshold on total received utilization (percent, 0-100) raising the high-level alarm (C(rxtotutilhi)), or C(disabled) (device default).
              rxtotutilmd:
                type: str
                description: Threshold on total received utilization (percent, 0-100) raising the medium-level alarm (C(rxtotutilmd)), or C(disabled) (device default).
              rxtotutillo:
                type: str
                description: Threshold on total received utilization (percent, 0-100) raising the low-level alarm (C(rxtotutillo)), or C(disabled) (device default).
              dbacongperiodhi:
                type: str
                description: Threshold on DBA congestion period (percent, 0-100) raising the high-level alarm (C(dbacongperiodhi)), or C(disabled) (device default).
              dbacongperiodmd:
                type: str
                description: Threshold on DBA congestion period (percent, 0-100) raising the medium-level alarm (C(dbacongperiodmd)), or C(disabled) (device default).
              dbacongperiodlo:
                type: str
                description: Threshold on DBA congestion period (percent, 0-100) raising the low-level alarm (C(dbacongperiodlo)), or C(disabled) (device default).
              txucdropfrmhi:
                type: str
                description: Threshold on transmitted unicast dropped frames (0-1000000000) raising the high-level alarm (C(txucdropfrmhi)), or C(disabled) (device default).
              txucdropfrmmd:
                type: str
                description: Threshold on transmitted unicast dropped frames (0-1000000000) raising the medium-level alarm (C(txucdropfrmmd)), or C(disabled) (device default).
              txucdropfrmlo:
                type: str
                description: Threshold on transmitted unicast dropped frames (0-1000000000) raising the low-level alarm (C(txucdropfrmlo)), or C(disabled) (device default).
              txmcdropfrmhi:
                type: str
                description: Threshold on transmitted multicast dropped frames (0-1000000000) raising the high-level alarm (C(txmcdropfrmhi)), or C(disabled) (device default).
              txmcdropfrmmd:
                type: str
                description: Threshold on transmitted multicast dropped frames (0-1000000000) raising the medium-level alarm (C(txmcdropfrmmd)), or C(disabled) (device default).
              txmcdropfrmlo:
                type: str
                description: Threshold on transmitted multicast dropped frames (0-1000000000) raising the low-level alarm (C(txmcdropfrmlo)), or C(disabled) (device default).
              txbcdropfrmhi:
                type: str
                description: Threshold on transmitted broadcast dropped frames (0-1000000000) raising the high-level alarm (C(txbcdropfrmhi)), or C(disabled) (device default).
              txbcdropfrmmd:
                type: str
                description: Threshold on transmitted broadcast dropped frames (0-1000000000) raising the medium-level alarm (C(txbcdropfrmmd)), or C(disabled) (device default).
              txbcdropfrmlo:
                type: str
                description: Threshold on transmitted broadcast dropped frames (0-1000000000) raising the low-level alarm (C(txbcdropfrmlo)), or C(disabled) (device default).
              rxtotdropfrmhi:
                type: str
                description: Threshold on total received dropped frames (0-1000000000) raising the high-level alarm (C(rxtotdropfrmhi)), or C(disabled) (device default).
              rxtotdropfrmmd:
                type: str
                description: Threshold on total received dropped frames (0-1000000000) raising the medium-level alarm (C(rxtotdropfrmmd)), or C(disabled) (device default).
              rxtotdropfrmlo:
                type: str
                description: Threshold on total received dropped frames (0-1000000000) raising the low-level alarm (C(rxtotdropfrmlo)), or C(disabled) (device default).
              numtcint:
                type: str
                description: Contiguous 5-minute intervals (1-96) the non-DBA utilization thresholds must be exceeded before a TCA is raised or cleared (C(numtcint)); device default C(1).
              numtcintdba:
                type: str
                description: Contiguous 5-minute intervals (1-96) the DBA congestion thresholds must be exceeded before a TCA is raised or cleared (C(numtcintdba)); device default C(1).
              dbacongthresh:
                type: str
                description: DBA congestion threshold as a percentage (0-100) of the maximum consumable bandwidth (C(dbacongthresh)); device default C(90).
      deact_ont_tca:
        type: dict
        description: Deactivated-ONT detection for the PON (C(deact-ont-tca)).
        suboptions:
          mode:
            type: str
            choices: [disable, percent, number]
            description: Detection mode (C(mode)); device default C(disable).
          monitor_interval:
            type: int
            description: Detection interval in seconds (C(monitor-interval), 5-300); device default C(30).
          threshold_percent:
            type: dict
            description: Thresholds in percent of the ONTs (C(threshold-percent)).
            suboptions:
              high:
                type: int
                description: Deactivated-ONT detection high threshold in percent (C(high), 1-100); device default C(90).
              high_clr:
                type: int
                description: Deactivated-ONT detection high clear threshold in percent (C(high-clr), 1-100); device default C(90).
              low:
                type: int
                description: Deactivated-ONT detection low threshold in percent (C(low), 1-100); device default C(40).
              low_clr:
                type: int
                description: Deactivated-ONT detection low clear threshold in percent (C(low-clr), 1-100); device default C(40).
          threshold_number:
            type: dict
            description: Thresholds as a number of ONTs (C(threshold-number)).
            suboptions:
              high:
                type: int
                description: Deactivated-ONT detection high threshold as a number of ONTs (C(high), 1-128); device default C(57).
              high_clr:
                type: int
                description: Deactivated-ONT detection high clear threshold as a number of ONTs (C(high-clr), 1-128); device default C(57).
              low:
                type: int
                description: Deactivated-ONT detection low threshold as a number of ONTs (C(low), 1-128); device default C(25).
              low_clr:
                type: int
                description: Deactivated-ONT detection low clear threshold as a number of ONTs (C(low-clr), 1-128); device default C(25).
  running_config:
    description:
      - 'Native running configuration for parsed state.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
    - A value equal to its device default counts as unset when comparing (the comparison read prints defaults, a plain read omits them); with C(merged) an explicit default is still sent where the device holds another value.
    - With C(merged), C(replaced) or C(deleted) and I(config), the current configuration is likewise read only for the named instances.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
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

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_pon_interfaces:
    config:
      - name: 1/1/5/3
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

import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pon_interfaces.pon_interfaces import Pon_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pon_interfaces.pon_interfaces import Pon_interfaces


def _validate_pon_config(module):
    """Validate constraints that depend on more than one PON field."""
    for item in module.params.get("config") or []:
        name = item["name"]
        if not re.match(
            r"^(?:\d+/\d+/\d+/\d+|(?:x-pon|25g-pon):\d+/\d+/\d+/\d+)$", name
        ):
            module.fail_json(msg="Invalid PON interface name: %s" % name)
        if item.get("label") is not None and len(item["label"]) > 80:
            module.fail_json(msg="PON label must not exceed 80 characters")
        for field, limit in (("pon_tag", 16), ("pon_id", 8)):
            value = item.get(field)
            if value is not None and (
                len(value) > limit or not re.match(r"^[0-9A-Fa-f]*$", value)
            ):
                module.fail_json(msg="%s must contain at most %d hexadecimal characters" % (field, limit))
        identifier = item.get("ponid_identifier")
        if identifier is not None and not re.match(r"^[0-9A-Fa-f]{14}$", identifier):
            module.fail_json(msg="ponid_identifier must contain exactly 14 hexadecimal characters")
        if (
            item.get("sig_degrade_th") is not None
            and item.get("sig_fail_th") is not None
            and item["sig_degrade_th"] <= item["sig_fail_th"]
        ):
            module.fail_json(msg="sig_degrade_th must be greater than sig_fail_th")
        if name.startswith("x-pon:") and item.get("closest_ont") is not None and item["closest_ont"] > 20:
            module.fail_json(msg="closest_ont must be between 0 and 20 for XGS PON")
        if name.startswith("x-pon:") and item.get("diff_reach") is not None and item["diff_reach"] not in (20, 40):
            module.fail_json(msg="diff_reach must be 20 or 40 for XGS PON")


def main():
    module = AnsibleModule(
        argument_spec=Pon_interfacesArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    _validate_pon_config(module)

    result = Pon_interfaces(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
