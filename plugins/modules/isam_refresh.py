#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""A complete (or partial) refresh of one ISAM object subtree in one task."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_refresh
short_description: Refresh one ONT, PON or card of an ISAM in one task, every part proven present, absent or a named gap
description:
  - Runs the whole topology refresh of one object (an ONT, a PON, a card, or another
    object kind of the topology model) in one task on one connection; the context
    read of the card types, the discovery rounds that find every child object, the
    configuration reads of every applicable section of every object, and the reads
    of the shared definitions that configuration refers to.
  - Every applicable (object, section) comes back as C(present), C(absent) (the device
    confirmed it) or a gap with a reason. C(complete) is true only without any gap.
    A gap is never interpreted as empty.
  - Each discovery source is read once per task, however many objects are enumerated
    from it (for example one C(show interface stack) for the bridge and VLAN ports of
    every line of a card).
  - With I(sections), only those configuration sections are read, and discovery only
    goes as deep as the objects they configure (a partial refresh: C(complete) then
    refers to the question asked).
  - This module never writes configuration; check mode reads like a normal run.
version_added: "1.1.0"
author: Jan Kühnemund (@jahknem)
options:
  kind:
    description: Object kind of the root of the refresh.
    type: str
    required: true
    choices: [pon, ont, ont_slot, uni, card, xdsl_line, ethernet_port, bonding_group, lag]
  identity:
    description: Canonical identity of the root, for example C(1/1/5/1/3) (ONT) or C(lt:1/1/3) (card).
    type: str
    required: true
  sections:
    description:
      - Read only these configuration sections, as C(resource) (all its sections) or
        C(resource.section), for example C(qos_interfaces) or C(equipment_onts.interfaces).
      - Without it every applicable section is read.
    type: list
    elements: str
  allow_broad_read:
    description:
      - Permit the device- or family-wide discovery sources (port table, interface
        stack, ONT index). Without it discovery returns C(unsupported) and the refresh
        is incomplete.
    type: bool
    default: false
  return_data:
    description: Include the configuration read results (C(reads)), credentials removed.
    type: bool
    default: false
"""

EXAMPLES = """
- name: Refresh one ONT completely
  nokia.isam.isam_refresh:
    kind: ont
    identity: 1/1/5/1/3
    allow_broad_read: true
  register: ont

- name: Only the QoS of every UNI and VLAN port of one ONT
  nokia.isam.isam_refresh:
    kind: ont
    identity: 1/1/5/1/3
    sections: [qos_interfaces]
    allow_broad_read: true
  register: ont_qos
"""

RETURN = """
refresh:
  description: The refresh outcome.
  returned: always
  type: dict
  contains:
    complete:
      description: True only when every applicable part is present or confirmed absent and every relation was enumerated.
      type: bool
    root:
      description: Kind and identity of the root.
      type: list
    objects:
      description: Every object found, as C([kind, identity]).
      type: list
    sections:
      description: One entry per (object, section) with C(status) present, absent or gap (and C(reason) for a gap).
      type: list
    references:
      description: The shared definitions read, with their status.
      type: list
    not_applicable:
      description: Sections and child kinds the card-type rules exclude, with the reason.
      type: list
    gaps:
      description: Everything that kept the refresh incomplete, each with a reason.
      type: list
    sections_requested:
      description: The sections of a partial refresh, or null.
      type: list
    discovery:
      description: The discovery records (see isam_topology_discovery).
      type: list
    stats:
      description: Run statistics (seconds, discovery rounds and requests, source reads, configuration reads, ids read).
      type: dict
    reads:
      description: The configuration read results (see isam_read), when I(return_data) is true.
      type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import UnknownIdentity
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.refresh_run import run
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.refresh import wanted_sections


def main():
    module = AnsibleModule(
        argument_spec=dict(
            kind=dict(type="str", required=True,
                      choices=["pon", "ont", "ont_slot", "uni", "card", "xdsl_line", "ethernet_port",
                               "bonding_group", "lag"]),
            identity=dict(type="str", required=True),
            sections=dict(type="list", elements="str"),
            allow_broad_read=dict(type="bool", default=False),
            return_data=dict(type="bool", default=False),
        ),
        supports_check_mode=True,
    )
    params = module.params
    try:
        wanted_sections(params["sections"])
    except ValueError as exc:
        module.fail_json(msg=str(exc), changed=False)
    # One connection for the whole refresh: reads and discovery sources share it.
    module._connection = get_resource_connection(module)
    try:
        outcome = run(module, (params["kind"], params["identity"]), sections=params["sections"],
                      allow_broad_read=params["allow_broad_read"], data=params["return_data"])
    except UnknownIdentity as exc:
        module.fail_json(msg=str(exc), changed=False)
    module.exit_json(changed=False, refresh=outcome)


if __name__ == "__main__":
    main()
