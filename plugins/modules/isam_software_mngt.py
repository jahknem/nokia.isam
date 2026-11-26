#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_software_mngt
short_description: Manage Nokia ISAM software management configuration.
description:
  - Manages C(configure software-mngt database), C(software-mngt oswp), and C(software-mngt sw-replacement-mode) configuration.
version_added: 0.3.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided software management configuration.
    type: dict
    suboptions:
      database:
        description: Software database settings (C(configure software-mngt database)).
        type: dict
        suboptions:
          version:
            description: Value C(configure software-mngt database version) (no removal form).
            type: str
          url:
            description: Value C(configure software-mngt database url) (no removal form).
            type: str
          activate:
            description: Value C(configure software-mngt database activate); device default C(manually).
            type: str
            choices: [after-download, manually]
          backup:
            description: Value C(configure software-mngt database backup); device default C(manually).
            type: str
          backupv6:
            description: Value C(configure software-mngt database backupv6); device default C(manually).
            type: str
          auto_backup_interval:
            description: Value C(configure software-mngt database auto-backup-intvl); device default C(24).
            type: int
      oswp:
        description: OSWP records (C(configure software-mngt oswp)).
        type: list
        elements: dict
        suboptions:
          id:
            description: Instance identifier.
            type: str
            required: true
          primary_file_server_id:
            description: Value C(configure software-mngt oswp primary-file-server-id) (no removal form).
            type: str
          second_file_server_id:
            description: Value C(configure software-mngt oswp second-file-server-id) (no removal form).
            type: str
          download_set:
            description: Value C(configure software-mngt oswp download-set) (no removal form).
            type: str
            choices: [min-set, actual-set, complete-set]
          autofetch:
            description: Value C(configure software-mngt oswp autofetch) (no removal form).
            type: str
            choices: [disabled, enabled]
          activate:
            description: Value C(configure software-mngt oswp activate); device default C(manually).
            type: str
            choices: [manually, after-download, on-schedule]
          auto_verify:
            description: Value C(configure software-mngt oswp auto-verify); device default C(disabled).
            type: str
            choices: [disabled, enabled]
          on_schedule_time:
            description: Value C(configure software-mngt oswp on-schedule-time); no concrete default.
            type: str
          admin_state:
            description: On/off flag C(configure software-mngt oswp admin-state).
            type: bool
      sw_replacement_mode:
        description: Software replacement mode (C(configure software-mngt sw-replacement-mode)).
        type: dict
        suboptions:
          mode:
            description: C(configure software-mngt sw-replacement-mode <value>).
            type: str
            choices: [upgrade-via-active, upgrade-via-standby, lt-by-lt]
  running_config:
    description:
      - 'Device native configuration to parse.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - The state of the configuration after module completion.
      - C(replaced) reconciles named OSWP entries and leaves unnamed OSWPs untouched;
        only C(overridden) removes OSWPs absent from the requested configuration.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
        C(oswp[].id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without
        I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_software_mngt:
    config:
      oswp:
        - id: "1"
    state: gathered

- name: Gather software management configuration
  nokia.isam.isam_software_mngt:
    state: gathered

- name: Configure software management database
  nokia.isam.isam_software_mngt:
    config:
      database:
        version: R6.2.04m
        url: tftp://192.0.2.1/software.bin
      oswp:
        - id: 1
          primary_file_server_id: 192.0.2.1
          second_file_server_id: 0.0.0.0
          activate: after-download
          auto_verify: enabled
          admin_state: true
      sw_replacement_mode:
        mode: upgrade-via-standby
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import (
    Software_mngtArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.software_mngt.software_mngt import (
    Software_mngt,
)


def main():
    module = AnsibleModule(
        argument_spec=Software_mngtArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Software_mngt(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
