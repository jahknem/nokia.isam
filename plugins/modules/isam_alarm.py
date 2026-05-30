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
author: Jan Kuehnemund
options:
  config:
    description: Alarm configuration grouped by resource type.
    type: dict
    suboptions:
      log:
        description: Global alarm log severity settings.
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
            description: Alarm entry index (alarm type).
            type: str
            required: true
          severity:
            description: Alarm severity threshold.
            type: str
            choices: [indeterminate, warning, minor, major, critical]
          service_affecting:
            description: Whether the alarm is service-affecting.
            type: bool
          reporting:
            description: Enable alarm reporting.
            type: bool
          logging:
            description: Enable alarm logging.
            type: bool
      filters:
        description: Alarm filter configuration list.
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
            description: Alarm type to filter.
            type: str
          status:
            description: Filter status.
            type: int
          threshold:
            description: Filter threshold value.
            type: int
          window:
            description: Filter window value.
            type: int
          suppressions:
            description: Sub-filter suppression entries.
            type: list
            elements: dict
            suboptions:
              filterid:
                description: Suppression filter ID.
                type: int
                required: true
              interface:
                description: Interface for suppression.
                type: str
              alarmid:
                description: Alarm type for suppression.
                type: str
              status:
                description: Suppression status.
                type: int
              threshold:
                description: Suppression threshold.
                type: int
      delta_log:
        description: Delta log full action settings.
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
        description: Customizable alarm profile entries.
        type: list
        elements: dict
        suboptions:
          name:
            description: Profile name.
            type: str
            required: true
  running_config:
    description: Device-native running configuration for parsed state.
    type: str
  state:
    description: The state the configuration should be left in.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather alarm configuration
  nokia.isam.isam_alarm:
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
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: dict
after:
  description: Configuration after module execution.
  returned: when changed
  type: dict
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured alarm data.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed structured alarm data.
  returned: when state is parsed
  type: dict
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
