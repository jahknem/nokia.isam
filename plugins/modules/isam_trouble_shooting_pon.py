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
        Other fields are ignored and absent instances are not returned; an instance with nothing
        configured answers like an absent one and is not returned either. Without I(config) the whole
        resource is read.
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
before:
  description: The configuration prior to module execution.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description: The resulting configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  sample:
    - configure trouble-shooting pon statistics threshold interface 1/1/2/1 bw-th-up 500000 bw-th-dn 2000000
rendered:
  description: The provided configuration in device-native format.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
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
