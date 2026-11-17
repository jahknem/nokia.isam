#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_system_security
short_description: Manages Nokia ISAM system security (operators, profiles, SNMP, RADIUS).
description:
  - Manages C(configure system security) on Nokia ISAM.
  - Secret values (operator passwords, RADIUS secrets, SNMP community strings) are redacted in output.
version_added: 0.3.14
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided system security configuration.
    type: dict
    suboptions:
      operators:
        type: list
        elements: dict
        description: Operators.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          password:
            type: str
            no_log: true
            description: Password.
          profile:
            type: str
            description: Profile.
          prompt:
            type: str
            description: Prompt.
          description:
            type: str
            description: Description.
          more:
            type: bool
            description: More.
          confirm_prompt:
            type: bool
            description: Confirm prompt.
          bgn_time:
            type: str
            description: Bgn time.
          end_time:
            type: str
            description: End time.
      profiles:
        type: list
        elements: dict
        description: Profiles.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          description:
            type: str
            description: Description.
          slot_numbering:
            type: str
            description: Slot numbering.
          prompt:
            type: str
            description: Prompt.
          password_timeout:
            type: str
            description: Password timeout.
          terminal_timeout:
            type: str
            description: Terminal timeout.
          permissions:
            type: dict
            description: Permissions.
      snmp_communities:
        type: list
        elements: dict
        description: Snmp communities.
        suboptions:
          name:
            type: str
            required: true
            no_log: true
            description: Name.
          host_address:
            type: str
            description: Host address.
          context:
            type: str
            description: Context.
          privilege:
            type: str
            description: Privilege.
          read_view:
            type: str
            description: Read view.
          write_view:
            type: str
            description: Write view.
          notify_view:
            type: str
            description: Notify view.
      snmp_views:
        type: list
        elements: dict
        description: Snmp views.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          subtree:
            type: str
            description: Subtree.
          type:
            type: str
            description: Type.
      snmp_managers:
        type: list
        elements: dict
        description: Snmp managers.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          destination:
            type: str
            description: Destination.
          notify_profile:
            type: str
            description: Notify profile.
          nt:
            type: bool
            description: Nt.
          shub:
            type: bool
            description: Shub.
          ihub:
            type: bool
            description: Ihub.
          epon:
            type: bool
            description: Epon.
          vvpsa:
            type: bool
            description: Vvpsa.
          xvps1:
            type: bool
            description: Xvps1.
          xvps2:
            type: bool
            description: Xvps2.
          xvps3:
            type: bool
            description: Xvps3.
          xvps4:
            type: bool
            description: Xvps4.
          xvps5:
            type: bool
            description: Xvps5.
          xvps6:
            type: bool
            description: Xvps6.
          xvps7:
            type: bool
            description: Xvps7.
          xvps8:
            type: bool
            description: Xvps8.
      snmp_notify_profiles:
        type: list
        elements: dict
        description: Snmp notify profiles.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          snmp_version:
            type: str
            description: Snmp version.
      radius_auth_servers:
        type: list
        elements: dict
        description: Radius auth servers.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          router_instance:
            type: str
            description: Router instance.
          ip_address:
            type: str
            description: Ip address.
          secret:
            type: str
            no_log: true
            description: Secret.
          port:
            type: int
            description: Port.
          timeout_limit:
            type: int
            description: Timeout limit.
          dead_interval:
            type: int
            description: Dead interval.
          retry_limit:
            type: int
            description: Retry limit.
          admin_down:
            type: bool
            description: Admin down.
      radius_policies:
        type: list
        elements: dict
        description: Radius policies.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          nas_id:
            type: str
            description: Nas id.
          nas_ip_address:
            type: str
            description: Nas ip address.
          keep_domain_name:
            type: bool
            description: Keep domain name.
          disable_accnt_msg:
            type: bool
            description: Disable accnt msg.
          disable_eap:
            type: bool
            description: Disable eap.
          acc_interval:
            type: int
            description: Acc interval.
          auth_server:
            type: str
            description: Auth server.
          auth_router_inst:
            type: str
            description: Auth router inst.
          acc_server:
            type: str
            description: Acc server.
          acc_router_inst:
            type: str
            description: Acc router inst.
          priority:
            type: int
            description: Priority.
      radius_auth_super_user:
        type: dict
        description: Radius auth super user.
        suboptions:
          operator_policy:
            type: str
            description: Operator policy.
          aut_s_unreach_act:
            type: str
            description: Aut s unreach act.
      radius_dyn_auth_clients:
        type: list
        elements: dict
        description: Radius dyn auth clients.
        suboptions:
          name:
            type: str
            required: true
            description: Name.
          ip_address:
            type: str
            description: Ip address.
          secret:
            type: str
            no_log: true
            description: Secret.
          router_instance:
            type: str
            description: Router instance.
  running_config:
    description: Device configuration to parse with I(state=parsed).
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by their C(name) in each list (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read. The C(radius_auth_super_user) settings block is read whole.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """

- name: Read the whole system security configuration
  nokia.isam.isam_system_security:
    state: gathered

- name: Read only one operator (targeted gathering)
  nokia.isam.isam_system_security:
    config:
      operators:
        - name: isadmin
    state: gathered

- name: Merge an SNMP view
  nokia.isam.isam_system_security:
    config:
      snmp_views:
        - name: everything
          subtree: "*"
          type: include
    state: merged
"""

RETURN = """

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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import (
    Isam_system_securityArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.system_security.system_security import (
    Isam_system_security,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_system_securityArgs.argument_spec,
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
    result = Isam_system_security(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
