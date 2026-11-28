#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_alarm
short_description: Manages Nokia ISAM alarm configuration.
description:
  - Manages C(configure alarm) log, entry, filter, suppression, delta-log, custom-profile, and HGU TR069 custom alarm settings.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: Alarm configuration grouped by resource type.
    type: dict
    suboptions:
      log:
        description:
          - Global alarm log severity settings.
          - No removal form in the CLI; left unchanged by I(state=deleted) and when omitted with I(state=overridden).
        type: dict
        suboptions:
          log_sev_level:
            description: Lowest severity level to log alarms.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
          log_full_action:
            description: Action when log buffer is full.
            type: str
            choices: [wrap, halt]
          non_itf_rep_sev_level:
            description: Minimum severity to report non-interface alarms.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
      entries:
        description: Alarm entry configuration list.
        type: list
        elements: dict
        suboptions:
          index:
            description:
              - Alarm entry index (alarm type), for example C(door), C(board-missing) or C(xdsl-ne-los).
              - Not restricted by the module; the set of alarm types depends on the software release
                (R6.2.04 knows more than a thousand) and is validated by the device.
            type: str
            required: true
          severity:
            description:
              - Alarm severity. C(ignore) means the alarm is not processed by the system.
              - With I(state=replaced) or I(state=overridden) an omitted severity is reset to the device default (C(no severity)).
            type: str
            choices: [indeterminate, warning, minor, major, critical, ignore]
          service_affecting:
            description:
              - Whether the alarm is service-affecting.
              - The CLI has no reset to the default for the flags (C(no service-affecting) sets C(false)), so omitted
                flags are left unchanged by every state.
            type: bool
          reporting:
            description: Enable alarm reporting.
            type: bool
          logging:
            description: Enable alarm logging.
            type: bool
      filters:
        description:
          - Alarm filter configuration list.
          - The device holds a fixed table of temporal and spatial filters; filters cannot be removed. With
            I(state=deleted) or I(state=overridden) C(status), C(threshold) and C(window) are reset (C(no status) etc.);
            C(alarmid) has no removal form and is left unchanged (with a warning unless it is C(all)).
        type: list
        elements: dict
        suboptions:
          fltr_type:
            description: Filter type.
            type: str
            required: true
            choices: [temporal, spatial]
          filterid:
            description: Unique filter number (1-31).
            type: int
            required: true
          alarmid:
            description:
              - Alarm type to filter, C(all) or an alarm type (see I(entries[].index)); validated by the device.
            type: str
          status:
            description: Filter status (device default C(not-used)).
            type: str
            choices: [not-used, used]
          threshold:
            description: Filter threshold value (2-65535, device default 2).
            type: int
          window:
            description: Filter window in seconds (1-65535, device default 60), temporal filters only.
            type: int
          suppressions:
            description:
              - Alarm suppression filter (C(configure alarm suppression filterid ..)) with the same filterid as this
                temporal filter; only valid under a temporal filter.
              - Suppression filters cannot be removed. On removal C(status) and C(threshold) are reset; C(interface)
                and C(alarmid) have no removal form and are left unchanged with a warning.
            type: list
            elements: dict
            suboptions:
              filterid:
                description: Suppression filter ID, equal to the filterid of the enclosing temporal filter.
                type: int
                required: true
              interface:
                description: LT slot of the suppression filter, for example C(lt:1/1/4).
                type: str
              alarmid:
                description: Alarm type for suppression.
                type: str
                choices: [board-missing, board-init]
              status:
                description: Suppression status (device default C(not-used)).
                type: str
                choices: [not-used, used]
              threshold:
                description: Suppression threshold (1-100, device default 1).
                type: int
      delta_log:
        description:
          - Delta log full action settings.
          - No removal form in the CLI; left unchanged by I(state=deleted) and when omitted with I(state=overridden).
        type: dict
        suboptions:
          indet_log_full_action:
            description: Indeterminate severity log full action.
            type: str
            choices: [wrap, halt]
          warn_log_full_action:
            description: Warning severity log full action.
            type: str
            choices: [wrap, halt]
          minor_log_full_action:
            description: Minor severity log full action.
            type: str
            choices: [wrap, halt]
          major_log_full_action:
            description: Major severity log full action.
            type: str
            choices: [wrap, halt]
          crit_log_full_act:
            description: Critical severity log full action.
            type: str
            choices: [wrap, halt]
      custom_profiles:
        description:
          - Customizable alarm profile entries.
          - Removed with C(configure alarm no custom-profile <name>).
        type: list
        elements: dict
        suboptions:
          name:
            description: Profile name.
            type: str
            required: true
          mnemonic1:
            description: Mnemonic of external alarm 1.
            type: str
          description1:
            description: Description of external alarm 1.
            type: str
          visible1:
            description: Whether external alarm 1 triggers a visible alarm output.
            type: bool
          audible1:
            description: Whether external alarm 1 triggers an audible alarm output.
            type: bool
          polarity1:
            description: Polarity of external alarm 1 (C(normal) or C(inverse)).
            type: str
          severity1:
            description: Severity of external alarm 1.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
          mnemonic2:
            description: Mnemonic of external alarm 2.
            type: str
          description2:
            description: Description of external alarm 2.
            type: str
          visible2:
            description: Whether external alarm 2 triggers a visible alarm output.
            type: bool
          audible2:
            description: Whether external alarm 2 triggers an audible alarm output.
            type: bool
          polarity2:
            description: Polarity of external alarm 2 (C(normal) or C(inverse)).
            type: str
          severity2:
            description: Severity of external alarm 2.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
          mnemonic3:
            description: Mnemonic of external alarm 3.
            type: str
          description3:
            description: Description of external alarm 3.
            type: str
          visible3:
            description: Whether external alarm 3 triggers a visible alarm output.
            type: bool
          audible3:
            description: Whether external alarm 3 triggers an audible alarm output.
            type: bool
          polarity3:
            description: Polarity of external alarm 3 (C(normal) or C(inverse)).
            type: str
          severity3:
            description: Severity of external alarm 3.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
          mnemonic4:
            description: Mnemonic of external alarm 4.
            type: str
          description4:
            description: Description of external alarm 4.
            type: str
          visible4:
            description: Whether external alarm 4 triggers a visible alarm output.
            type: bool
          audible4:
            description: Whether external alarm 4 triggers an audible alarm output.
            type: bool
          polarity4:
            description: Polarity of external alarm 4 (C(normal) or C(inverse)).
            type: str
          severity4:
            description: Severity of external alarm 4.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
          mnemonic5:
            description: Mnemonic of external alarm 5.
            type: str
          description5:
            description: Description of external alarm 5.
            type: str
          visible5:
            description: Whether external alarm 5 triggers a visible alarm output.
            type: bool
          audible5:
            description: Whether external alarm 5 triggers an audible alarm output.
            type: bool
          polarity5:
            description: Polarity of external alarm 5 (C(normal) or C(inverse)).
            type: str
          severity5:
            description: Severity of external alarm 5.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
      hgutr069_custs:
        description:
          - HGU TR069 customizable alarms.
          - Removed with C(configure alarm no hgutr069-cust <alarm-id>).
        type: list
        elements: dict
        suboptions:
          alarm_id:
            description: HGU TR069 customizable alarm ID (for example C(cust-alm1)).
            type: str
            required: true
          description:
            description: Alarm description (1-64 characters), mandatory when the alarm is created.
            type: str
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by
        C(entries[].index) and C(filters[].fltr_type) and C(filters[].filterid) and C(custom_profiles[].name) and
        C(hgutr069_custs[].alarm_id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it.
        Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather alarm configuration
  nokia.isam.isam_alarm:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_alarm:
    config:
      entries:
        - index: xdsl-ne-los
      filters:
        - fltr_type: temporal
          filterid: 3
      custom_profiles:
        - name: cabinet1
    state: gathered

- name: Configure alarm log severity
  nokia.isam.isam_alarm:
    config:
      log:
        log_sev_level: warning
        log_full_action: wrap
        non_itf_rep_sev_level: minor
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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.alarm.alarm import (
    AlarmArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.alarm.alarm import (
    Alarm,
)


def main():
    module = AnsibleModule(
        argument_spec=AlarmArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Alarm(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
