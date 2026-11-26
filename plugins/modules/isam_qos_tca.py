#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_qos_tca
short_description: Manages Nokia ISAM per-queue QoS threshold crossing alarms.
description:
  - Manages C(configure qos tca <port> queue <n>) attributes on Nokia ISAM.
version_added: 0.3.14
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided QoS TCA configuration.
    type: list
    elements: dict
    suboptions:
      name:
        type: str
        required: true
        description: Port or LAG identifier (e.g. C(1/1/5/1/3/1/1)).
      queue:
        type: int
        required: true
        description: Queue index within the port.
      tca_enable:
        type: bool
        description: Enable threshold crossing alarms for the queue.
      load_thresh:
        type: int
        description: Load threshold (percent).
      dis_frame_th:
        type: int
        description: Discarded-frames threshold.
      qpeak_usage_th:
        type: int
        description: Queue peak usage threshold (percent).
  running_config:
    description:
      - 'Device configuration to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) and C(queue) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - Queues are not individually removable on the device; C(deleted) and C(overridden) reset their attributes.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Merge QoS TCA settings for one queue
  nokia.isam.isam_qos_tca:
    config:
      - name: 1/1/5/1/3/1/1
        queue: 0
        tca_enable: true
        load_thresh: 80
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_qos_tca:
    config:
      - name: 1/1/5/1/3/1/1
        queue: 0
    state: gathered

- name: Reset the TCA attributes of a queue
  nokia.isam.isam_qos_tca:
    config:
      - name: 1/1/5/1/3/1/1
        queue: 0
    state: deleted
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_tca.qos_tca import (
    Qos_tcaArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_tca.qos_tca import (
    Qos_tca,
)


def main():
    module = AnsibleModule(
        argument_spec=Qos_tcaArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Qos_tca(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
