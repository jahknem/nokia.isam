#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_trouble_shooting_pon
short_description: Manages PON trouble-shooting statistics of Nokia ISAM.
description:
  - Manages C(configure trouble-shooting pon statistics) on Nokia ISAM devices
    (extensive trouble-shooting counters per PON port and the PON traffic thresholds).
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
notes:
  - Enabling counters requires operator security privileges, the per-port thresholds equipment privileges.
  - The detail output of C(info configure trouble-shooting pon) prints the thresholds of every PON port;
    ports at their defaults (C(no bw-th-up no bw-th-dn)) and the default interval are not reported.
  - PON ports are given as C(rack/shelf/slot/port), or C(x-pon:...) / C(25g-pon:...) for XGS and 25G PON ports.
options:
  config:
    description: Trouble-shooting statistics configuration.
    type: dict
    suboptions:
      interfaces:
        description:
          - PON ports with the extensive trouble-shooting counters enabled
            (C(configure trouble-shooting pon statistics [no] interface <port>)).
        type: list
        elements: dict
        suboptions:
          name:
            description: PON port.
            type: str
            required: true
      threshold:
        description: Traffic threshold crossing alerts (C(configure trouble-shooting pon statistics threshold)).
        type: dict
        suboptions:
          interval:
            description:
              - Ethernet traffic TCA detection interval for PON in seconds (C(interval)), range 60-86400.
                Device default C(300).
            type: int
          interfaces:
            description:
              - Per-port average rate thresholds (C(threshold interface <port>)). Every PON port has them;
                they are set and reset (C(no bw-th-up)/C(no bw-th-dn)), never removed.
            type: list
            elements: dict
            suboptions:
              name:
                description: PON port.
                type: str
                required: true
              bw_th_up:
                description:
                  - Average upstream rate threshold in kbps (C(bw-th-up)), 0 disables. Device default C(0).
                type: int
              bw_th_dn:
                description:
                  - Average downstream rate threshold in kbps (C(bw-th-dn)), 0 disables. Device default C(0).
                type: int
  running_config:
    description:
      - 'Native C(info configure trouble-shooting pon flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - C(merged) enables the named counter interfaces and sets the given values.
      - C(replaced) replaces each given section; the counter interfaces when I(interfaces) is given (others are
        disabled), the interval when I(threshold) is given (reset when omitted) and each named threshold port
        completely (omitted thresholds are reset).
      - C(overridden) makes the whole configuration equal to I(config); counters not named are disabled,
        threshold ports not named are reset to the defaults.
      - C(deleted) without I(config) disables all counters and resets the interval and all thresholds;
        with I(config) only the named counter interfaces and threshold ports (and the interval when given).
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device,
        selected by C(interfaces[].name) and C(threshold.interfaces[].name) (targeted gathering).
        Other fields are ignored and absent instances are not returned; an instance with only default
        values is read with C(flat detail) and returned with its identity only (statistics interfaces,
        a switch without attributes, are present unless the device says "instance does not exist").
        C(read_outcomes) reports each named instance present or confirmed absent. Without I(config) the
        whole resource is read.
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
- name: Enable counters on a PON port and set thresholds
  nokia.isam.isam_trouble_shooting_pon:
    config:
      interfaces:
        - name: 1/1/2/1
      threshold:
        interval: 900
        interfaces:
          - name: 1/1/2/1
            bw_th_up: 500000
            bw_th_dn: 2000000
    state: merged

# commands:
# - configure trouble-shooting pon statistics interface 1/1/2/1
# - configure trouble-shooting pon statistics threshold interval 900
# - configure trouble-shooting pon statistics threshold interface 1/1/2/1 bw-th-up 500000 bw-th-dn 2000000

- name: Reset everything to the device defaults
  nokia.isam.isam_trouble_shooting_pon:
    state: deleted

# commands (for the configuration above):
# - configure trouble-shooting pon statistics no interface 1/1/2/1
# - configure trouble-shooting pon statistics threshold no interval
# - configure trouble-shooting pon statistics threshold interface 1/1/2/1 no bw-th-up no bw-th-dn

- name: Read only the thresholds of one port
  nokia.isam.isam_trouble_shooting_pon:
    config:
      threshold:
        interfaces:
          - name: 1/1/2/1
    state: gathered

# reads:
# - info configure trouble-shooting pon statistics threshold interface 1/1/2/1 flat
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
  - configure trouble-shooting pon statistics threshold interface 1/1/2/1 bw-th-up 500000 bw-th-dn 2000000
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.trouble_shooting_pon.trouble_shooting_pon import (
    Trouble_shooting_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.trouble_shooting_pon.trouble_shooting_pon import (
    Trouble_shooting_pon,
)


def main():
    module = AnsibleModule(
        argument_spec=Trouble_shooting_ponArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Trouble_shooting_pon(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
