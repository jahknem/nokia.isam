#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_cfm
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_cfm
short_description: Manages Nokia ISAM CFM configuration.
description:
  - Manages C(configure cfm) domains, associations, MEPs, SLM settings and Y.1731 PM sessions on Nokia ISAM.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The CFM configuration.
    type: dict
    suboptions:
      domains:
        description:
          - Maintenance domains, keyed by C(domain_index), with C(name), C(level) and C(associations)
            (each keyed by C(association_index), with C(meps) and C(remote_meps)).
          - Creating a domain with attributes requires both C(name) and C(level).
            The device does not permit changing either on an existing domain; explicitly
            remove and recreate it if needed. The module never does that implicitly.
        type: list
        elements: dict
      slm:
        description:
          - SLM settings (C(configure cfm slm)); a settings block, not an instance list.
        type: dict
        suboptions:
          inactivity_time:
            description:
              - SLM inactivity timer in seconds (10-100), C(configure cfm slm inactivity-time).
              - The device default (100, C(no inactivity-time)) is not reported. I(state=replaced),
                I(state=overridden) and I(state=deleted) reset it with C(configure cfm slm no inactivity-time).
            type: int
      y1731pm:
        description:
          - Y.1731 PM sessions, keyed by C(domain_index), C(association), C(mep) and C(session_id),
            with C(type), C(target_mac), C(priority), C(admin_up), C(interval), C(size) and C(measurement_intvl).
        type: list
        elements: dict
  running_config:
    description:
      - 'Native C(info configure ... flat) output to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(replaced), only named top-level sections are reconciled. Domains are
        identified by C(domain_index), not their configurable name.
      - With C(deleted) and I(config), only named sections are touched; without I(config),
        all configured domains are removed and the SLM inactivity timer is reset.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(domains[].domain_index) and C(y1731pm[].domain_index), C(y1731pm[].association), C(y1731pm[].mep) and C(y1731pm[].session_id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
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
- name: Gather the whole resource
  nokia.isam.isam_cfm:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_cfm:
    config:
      domains:
        - domain_index: 1
      y1731pm:
        - domain_index: 1
          association: 2
          mep: 7
          session_id: 1
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.cfm.cfm import CfmArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.cfm.cfm import Cfm


def main():
    module = AnsibleModule(argument_spec=CfmArgs.argument_spec, required_if=[
        ["state", "merged", ["config"]], ["state", "replaced", ["config"]], ["state", "overridden", ["config"]],
        ["state", "rendered", ["config"]], ["state", "parsed", ["running_config"]]], supports_check_mode=True)
    module.exit_json(**Cfm(module).execute_module())


if __name__ == "__main__":
    main()
