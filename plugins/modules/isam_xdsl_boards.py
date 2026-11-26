#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_boards
short_description: Resource module to configure xdsl board settings
description:
  - Manages C(configure xdsl board) and C(configure xdsl vp-board) settings
    on Nokia ISAM devices.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Tested against Nokia ISAM 6.2.04ng
  - This module works with connection C(network_cli)
  - Attribute removal uses the C(no <keyword>) forms the device prints in its detail output.
    I(state=deleted), and boards/VP boards dropped by I(state=overridden), render
    C(configure xdsl no board <id>) / C(configure xdsl no vp-board <id>).
  - Keywords the device prints but this module does not model are ignored when reading.
options:
  config:
    description: XDSL board configuration.
    type: dict
    suboptions:
      boards:
        description:
          - List of XDSL board entries (C(configure xdsl board)).
          - Attributes at their default (printed as C(no <keyword>) by the detail output) are not reported.
        type: list
        elements: dict
        suboptions:
          board_id:
            type: str
            required: true
            description: Board identifier (rack/shelf/slot), for example C(1/1/3).
          admin_state:
            type: str
            choices: [up, down]
            description:
              - Administrative state (C(admin-state)).
              - Not printed by the R6.2 boards seen so far; kept for compatibility.
          card_type:
            type: str
            description:
              - Card type (C(card-type)).
              - Not printed by the R6.2 boards seen so far; kept for compatibility.
          dpbo_profile:
            type: str
            description: DPBO profile of the board (C(dpbo-profile)); removed with C(no dpbo-profile).
          vce_profile:
            type: str
            description: Vectoring control entity profile (C(vce-profile)); removed with C(no vce-profile).
          vplt_autodiscover:
            type: str
            description: Vectoring processing LT auto-discovery (C(vplt-autodiscover)); removed with C(no vplt-autodiscover).
          vce_capacity_mode:
            type: str
            description: VCE capacity mode (C(vce-capacity-mode)); removed with C(no vce-capacity-mode).
          leg_upbo_profile:
            type: str
            description: Legacy UPBO profile (C(leg-upbo-profile)); removed with C(no leg-upbo-profile).
          vect_class:
            type: str
            description: Vectoring class (C(vect-class)); removed with C(no vect-class).
          vect_fallback:
            type: dict
            description:
              - Vectoring fallback settings (C(configure xdsl board <id> vect-fallback)).
            suboptions:
              fb_vplt_com_fail:
                type: bool
                description:
                  - Fall back on vectoring processing LT communication failure (C(fb-vplt-com-fail)).
                  - C(false) renders C(no fb-vplt-com-fail), the default, which is not reported.
              fb_cpe_cap_mism:
                type: bool
                description:
                  - Fall back on CPE capability mismatch (C(fb-cpe-cap-mism)).
                  - C(false) renders C(no fb-cpe-cap-mism), the default, which is not reported.
              fb_conf_not_feas:
                type: bool
                description:
                  - Fall back when the configuration is not feasible (C(fb-conf-not-feas)).
                  - C(false) renders C(no fb-conf-not-feas), the default, which is not reported.
              spectrum_profile:
                type: str
                description: Fallback spectrum profile (C(spectrum-profile)); removed with C(no spectrum-profile).
              service_profile:
                type: str
                description: Fallback service profile (C(service-profile)); removed with C(no service-profile).
              dpbo_profile:
                type: str
                description: Fallback DPBO profile (C(dpbo-profile)); removed with C(no dpbo-profile).
              rtx_profile:
                type: str
                description: Fallback retransmission profile (C(rtx-profile)); removed with C(no rtx-profile).
              sos_profile:
                type: str
                description: Fallback SOS profile (C(sos-profile)); removed with C(no sos-profile).
          auto_port_reset:
            type: dict
            description:
              - Automatic port reset settings (C(configure xdsl board <id> auto-port-reset)).
            suboptions:
              max_retry_attempt:
                type: int
                description: Maximum number of reset attempts (C(max-retry-attempt)); removed with C(no max-retry-attempt).
              reset_interval:
                type: int
                description: Reset interval (C(reset-interval)); removed with C(no reset-interval).
              reset_threshold:
                type: int
                description: Reset threshold (C(reset-threshold)); removed with C(no reset-threshold).
      vp_boards:
        description: List of XDSL VP board entries (C(configure xdsl vp-board)).
        type: list
        elements: dict
        suboptions:
          vp_board_id:
            type: str
            required: true
            description: VP board identifier.
          admin_state:
            type: str
            choices: [up, down]
            description:
              - Administrative state (C(admin-state)).
              - Not printed by the R6.2 VP boards seen so far; kept for compatibility.
          vp_links:
            type: list
            elements: dict
            description:
              - Vectoring processing links of the VP board (C(vp-link <link_id>)).
              - Links without an expected LT (C(no lt-expect), the default) are not reported.
              - With I(state=replaced) or I(state=overridden), links not listed get C(no lt-expect).
            suboptions:
              link_id:
                type: str
                required: true
                description: VP link index, for example C(1).
              lt_expect:
                type: str
                description: Expected LT slot of the link (C(lt-expect)); removed with C(no lt-expect).
  running_config:
    description:
      - 'This option is used only with state I(parsed).'
      - 'The value of this option should be the output received from the device by executing the command C(info configure xdsl board).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(boards[].board_id) and C(vp_boards[].vp_board_id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather xdsl boards
  nokia.isam.isam_xdsl_boards:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_xdsl_boards:
    config:
      boards:
        - board_id: 1/1/3
      vp_boards:
        - vp_board_id: 1/1/4
    state: gathered

- name: Merge an xdsl board
  nokia.isam.isam_xdsl_boards:
    config:
      boards:
        - board_id: 1/1/3
          vce_profile: "10"
          vect_fallback:
            fb_vplt_com_fail: true
          auto_port_reset:
            max_retry_attempt: 3
      vp_boards:
        - vp_board_id: 1/1/1
          vp_links:
            - link_id: "1"
              lt_expect: 1/1/4
    state: merged
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
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_boards.xdsl_boards import (
    Xdsl_boardsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_boards.xdsl_boards import (
    Xdsl_boards,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_boardsArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Xdsl_boards(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
