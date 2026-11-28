#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
The module file for isam_pppoe_client_interface
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_pppoe_client_interface
short_description: Manages Nokia ISAM PPPoE client interfaces.
description:
  - Manages C(configure pppoe-client interface) on Nokia ISAM.
  - An instance is identified by I(name) and I(client_id) (CLI C((ifindex) client-id <id>)); one port can carry several client ids.
  - The write states read C(info configure pppoe-client interface flat) and compare against it; a device error fails the module.
notes:
  - Creating or changing a client interface sends all mandatory parameters (I(client_id), I(profile_name), I(username), I(password)).
    Attributes not given are taken from the device, except I(password), which the device hides; a change without I(password) fails.
  - I(password) is never compared, so a password-only change is not detected.
  - An entry without I(client_id) addresses the only client id of its port; with several client ids on the port the module fails
    (I(state=deleted) removes all client ids of the port).
  - With I(state=replaced) or C(overridden), I(mac) and I(pbit) not given are reset to their defaults.
  - I(ipversion), I(authproto) and I(mru) belong to PPP profiles and are ignored here.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: PPPoE client interfaces.
    type: list
    elements: dict
    suboptions:
      name:
        description: Interface index of the PPPoE client port (e.g. 1/1/1/1/3:100).
        type: str
        required: true
      ipversion:
        description: IP version (PPP profiles).
        type: str
      authproto:
        description: Authentication protocol (PPP profiles).
        type: str
      mru:
        description: Maximum receive unit (PPP profiles).
        type: int
      client_id:
        description:
          - PPPoE client id; together with I(name) the identity of the instance.
          - Required to create an instance; optional when the port has exactly one client id.
        type: int
      profile_name:
        description: PPP profile name (client interfaces).
        type: str
      username:
        description: User name for PPP authentication (client interfaces).
        type: str
      password:
        description: Password for PPP authentication (client interfaces).
        type: str
      mac:
        description: MAC address (client interfaces).
        type: str
      pbit:
        description: P-bit value (client interfaces).
        type: int
  running_config:
    description: Native C(info configure ... flat) output to parse with I(state=parsed).
    type: str
  state:
    description:
      - The state the configuration should be left in.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it. Without I(config) the whole resource is read.
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
  nokia.isam.isam_pppoe_client_interface:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_pppoe_client_interface:
    config:
      - name: 1/1/1/1/3:100
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
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
  type: list
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
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
  type: list
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: list
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.pppoe_client.pppoe_client import PppoeClientArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.pppoe_client.pppoe_client import PppoeClient


def main():
    module = AnsibleModule(
        argument_spec=PppoeClientArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[["state", "merged", ["config"]], ["state", "replaced", ["config"]],
                     ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
                     ["state", "parsed", ["running_config"]]],
        supports_check_mode=True,
    )
    module.exit_json(**PppoeClient(module, "interface").execute_module())


if __name__ == "__main__":
    main()
