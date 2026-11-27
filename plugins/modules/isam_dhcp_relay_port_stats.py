#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_dhcp_relay_port_stats
short_description: Clear Nokia ISAM DHCP relay user-port statistics.
description:
  - Sends the operational administrative command C(admin dhcp-relay port-stats <vlan-port> clear-statistics)
    (CLI guide 222.2), which clears the DHCP relay statistics of an IP user interface / VLAN port.
  - This is an B(action module) it writes to the device, but performs a one-shot operation rather than
    managing persistent configuration. It has no resource states (merged/replaced/deleted/...) and is not
    idempotent; running it is an event. It is not an Ansible action plugin (controller-side helper).
  - I(clear_statistics) is the operation and must be C(true). A bare C(admin dhcp-relay port-stats <vlan-port>)
    without an operation only navigates to the port in the admin hierarchy and performs no action, so it is
    rejected rather than reported as a change.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: User ports whose DHCP relay statistics to clear.
    type: list
    elements: dict
    required: true
    suboptions:
      port:
        description:
          - The VLAN port identifier C(rack/shelf/slot/port[:vpi:vci]) or a C(vlan:rack/shelf/slot/port:...)
            path.
        type: str
        required: true
      clear_statistics:
        description:
          - Clear the port's DHCP relay statistics. This is the operation; it must be C(true).
          - C(false) (the default) names no operation and is rejected.
        type: bool
        default: false
"""

EXAMPLES = """
- name: Clear DHCP relay statistics on two user ports
  nokia.isam.isam_dhcp_relay_port_stats:
    config:
      - port: 1/1/6/1
        clear_statistics: true
      - port: vlan:1/1/6/1:3990
        clear_statistics: true

- name: Check what would run without touching the device
  nokia.isam.isam_dhcp_relay_port_stats:
    config:
      - port: 1/1/6/1
        clear_statistics: true
  check_mode: true
"""

RETURN = """
changed:
  description: Whether an action command was (or would be, in check mode) sent.
  returned: always
  type: bool
commands:
  description: The operational commands sent (or that would be sent in check mode).
  returned: always
  type: list
  elements: str
response:
  description: The device responses to the commands (empty in check mode).
  returned: when not check mode
  type: list
  elements: str
sent:
  description: Commands handed to the device (on failure, up to and including I(failed_command)).
  returned: when commands were sent (not in check mode), and on failure
  type: list
  elements: str
accepted:
  description: Commands the device answered without a recognised error.
  returned: when commands were sent (not in check mode), and on failure
  type: list
  elements: str
completed:
  description:
    - Commands confirmed to have taken effect. Without a module-specific completion check
      an accepted command counts as completed.
    - On a failure, completion of everything else is unknown; read the device back before retrying.
  returned: when commands were sent (not in check mode), and on failure
  type: list
  elements: str
failed_command:
  description: The command that failed; its outcome is unknown (it may have executed). Null when no command failed.
  returned: on failure
  type: str
pending:
  description: Commands never sent because of the failure.
  returned: on failure
  type: list
  elements: str
failure_phase:
  description: Where the run failed, C(connection), C(execution) or C(verification).
  returned: on failure
  type: str
completion_status:
  description: C(not_started) when nothing was sent, otherwise C(unknown).
  returned: on failure
  type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.dhcp_relay_port_stats.dhcp_relay_port_stats import (
    Isam_dhcp_relay_port_statsArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.dhcp_relay_port_stats.dhcp_relay_port_stats import (
    Isam_dhcp_relay_port_stats,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_dhcp_relay_port_statsArgs.argument_spec,
        supports_check_mode=True,
    )
    module.exit_json(**Isam_dhcp_relay_port_stats(module).execute_module())


if __name__ == "__main__":
    main()
