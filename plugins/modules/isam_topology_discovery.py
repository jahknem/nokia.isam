#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Read-only child enumeration for the semantic topology graph."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_topology_discovery
short_description: Enumerate direct children of one ISAM object for recursive refresh
description:
  - Performs one fresh, read-only child enumeration for a single direct-neighbor
    relation in the semantic topology graph.
  - This module never writes configuration; check mode therefore enumerates like a normal run.
  - The ISAM has no scoped "list children of X" command for most of these
    relations, so enumeration reads the smallest whole source that contains the
     children (device-wide ONT index, transceiver inventory, IHUB port inventory or interface stack,
    family-wide ONT, equipment or interface configuration) and filters by the
    parent identity. The true breadth is recorded in C(read_scope); this is the
    documented enumeration method, not a hidden widening of a scoped request.
  - A successful empty result confirms that the requested relation has no
    children within the enumerated source. An unsupported or failed enumeration
    is reported as such and must not be interpreted as an empty child list.
  - The returned record is evidence for one relation only. Recursive coverage
    requires successful fresh evidence for every required relation in the
    selected subtree, assembled by the caller.
version_added: "1.1.0"
author: Jan Kühnemund (@jahknem)
options:
  kind:
    description: Parent object kind in the semantic topology graph.
    type: str
    required: true
    choices: [msan, rack, shelf, pon, ont, ont_slot, card, applique, uni, xdsl_line, ethernet_port, bonding_group, lag,
              bridge_port]
  identity:
    description:
      - Canonical identity of the parent object.
      - For C(kind=bridge_port), use the encoding C(<port kind>:<port identity>),
        for example C(lag:1/1/8/1), C(xdsl_line:1/1/3/1) or C(uni:1/1/5/1/3/1/1).
    type: str
    required: true
  child_kind:
    description: Direct child kind to enumerate.
    type: str
    required: true
    choices: [rack, shelf, card, applique, ont, ont_slot, uni, pon, xdsl_line, ethernet_port, cage, bonding_group, lag,
              channel_pair, transceiver, bridge_port, vlan_port, uplink]
  allow_broad_read:
    description:
      - Explicitly permit the device/family-wide enumeration source declared
        for this relation. Without permission, returns unsupported without
        issuing enumeration commands. Merely requesting a scoped root does not
        authorize reading its siblings' configuration.
    type: bool
    default: false
"""

EXAMPLES = """
- name: Enumerate the ONTs configured on one PON
  nokia.isam.isam_topology_discovery:
    kind: pon
    identity: 1/1/5/10
    child_kind: ont
    allow_broad_read: true
  register: pon_children

- name: Enumerate the slots of one ONT
  nokia.isam.isam_topology_discovery:
    kind: ont
    identity: 1/1/5/10/1
    child_kind: ont_slot
    allow_broad_read: true
  register: ont_children

- name: Enumerate the UNIs of one ONT slot
  nokia.isam.isam_topology_discovery:
    kind: ont_slot
    identity: 1/1/5/10/1/1
    child_kind: uni
    allow_broad_read: true
  register: slot_children

- name: Enumerate the PON ports of one linecard
  nokia.isam.isam_topology_discovery:
    kind: card
    identity: lt:1/1/5
    child_kind: pon
    allow_broad_read: true
  register: card_children

- name: Enumerate the transceiver cages of one controller card
  nokia.isam.isam_topology_discovery:
    kind: card
    identity: nt-a
    child_kind: transceiver
    allow_broad_read: true
  register: nt_cages

- name: Enumerate the bridge port of one UNI
  nokia.isam.isam_topology_discovery:
    kind: uni
    identity: 1/1/5/1/3/1/1
    child_kind: bridge_port
    allow_broad_read: true
  register: uni_bridge

- name: Enumerate the IHUB optical ports of one controller card
  nokia.isam.isam_topology_discovery:
    kind: card
    identity: nt-a
    child_kind: uplink
    allow_broad_read: true
  register: nt_ports

- name: Enumerate the VLAN ports of one bridge port
  nokia.isam.isam_topology_discovery:
    kind: bridge_port
    identity: lag:1/1/8/1
    child_kind: vlan_port
    allow_broad_read: true
  register: lag_vlans
"""

RETURN = """
discovery:
  description: One direct-neighbor enumeration result.
  returned: always
  type: dict
  contains:
    schema_version:
      description: Topology graph schema version.
      type: int
    discovery_version:
      description: Discovery result contract version.
      type: int
    parent:
      description: Graph node key of the parent.
      type: str
    child_kind:
      description: Direct child kind enumerated.
      type: str
    status:
      description: C(ok), C(unsupported) or C(error).
      type: str
    children:
      description: Sorted child identities; empty only when status is C(ok).
      type: list
      elements: str
    command:
      description: The read command used, when status is C(ok).
      type: str
    read_scope:
      description: True breadth of the enumeration source (C(device), C(family) or C(scoped)).
      type: str
    collected_at:
      description: UTC timestamp of the enumeration.
      type: str
    error:
      description:
        - Failure reason when status is not C(ok), a stable token such as
          C(broad_enumeration_requires_allow_broad_read).
        - For a failed read, the error class (C(timeout), C(connection_error) or C(device_error))
          and the exception type, for example C(connection_error (ConnectionError)); raw
          device or exception text is never returned.
      type: str
    source:
      description: Evidence source.
      type: str
changed:
  description: Always false; this module only reads.
  returned: always
  type: bool
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    _is_absent_error,
    _is_unsupported_node,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read_outcomes import error_class
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.discovery import (
    adapter_for,
    _validate_parent,
    enumerate_children,
    parse_ont_serials,
    parse_ont_slots,
    result,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import (
    UnknownIdentity,
    decode,
)


def _read(connection, command):
    """Return (response, status). status is 'ok', 'unsupported' or 'absent'.

    A device/family-wide enumeration source that answers 'invalid token' is
    unsupported, NOT an empty child list. An absent-instance error likewise must
    not be reported as confirmed absence of children. Only a clean reply (even a
    header-only table) is 'ok'.
    """
    try:
        response = connection.get(command)
    except Exception as exc:
        text = str(exc)
        if _is_unsupported_node(text):
            return "", "unsupported"
        if _is_absent_error(text):
            return "", "absent"
        raise
    if _is_unsupported_node(response):
        return "", "unsupported"
    if _is_absent_error(response):
        return "", "absent"
    # Enumeration consumes whole-source replies, not single-instance replies.
    # Keep the header so a recognized empty source is distinguishable from a
    # blank/truncated/garbled transport response.
    return response, "ok"


def main():
    module = AnsibleModule(
        argument_spec=dict(
            kind=dict(type="str", required=True,
                      choices=["msan", "rack", "shelf", "pon", "ont", "ont_slot", "card", "applique", "uni",
                               "xdsl_line", "ethernet_port", "bonding_group", "lag", "bridge_port"]),
            identity=dict(type="str", required=True),
            allow_broad_read=dict(type="bool", default=False),
            child_kind=dict(type="str", required=True,
                            choices=["rack", "shelf", "card", "applique", "ont", "ont_slot", "uni", "pon", "xdsl_line",
                                     "ethernet_port", "cage", "bonding_group", "lag", "channel_pair", "transceiver",
                                      "bridge_port", "vlan_port", "uplink"]),
        ),
        supports_check_mode=True,
    )
    kind = module.params["kind"]
    identity = module.params["identity"]
    child_kind = module.params["child_kind"]
    relation = (kind, child_kind)
    try:
        _validate_parent(kind, identity)
        if kind == "bridge_port":
            identity = decode("bridge_port", identity)[1]
        adapter = adapter_for(kind, child_kind)
    except UnknownIdentity as exc:
        module.fail_json(msg=str(exc), changed=False)

    command, read_scope = adapter["command"], adapter["read_scope"]
    # Read-only: enumeration never changes the device, so check mode reads like a normal run.
    if read_scope in ("device", "family") and not module.params["allow_broad_read"]:
        module.exit_json(changed=False, discovery=result(
            kind, identity, child_kind, "unsupported", command=command, read_scope=read_scope,
            error="broad_enumeration_requires_allow_broad_read"))

    connection = get_resource_connection(module)
    discovery = None
    try:
        response, read_status = _read(connection, command)
        if read_status != "ok":
            discovery = result(kind, identity, child_kind, "unsupported", command=command,
                               read_scope=read_scope, error="enumeration_source_%s" % read_status)
        elif relation == ("pon", "ont"):
            discovery = parse_ont_serials(response, identity)
        elif relation == ("ont", "ont_slot"):
            discovery = parse_ont_slots(response, identity)
        else:
            discovery = enumerate_children(kind, identity, child_kind, response)
    except UnknownIdentity as exc:
        module.fail_json(msg=str(exc), changed=False)
    except Exception as exc:
        # The exception text may echo device output (configuration); report only a
        # stable error class and the exception type, as ihub_config does.
        discovery = result(kind, identity, child_kind, "error", command=command, read_scope=read_scope,
                           error="%s (%s)" % (error_class(exc), type(exc).__name__))
    module.exit_json(changed=False, discovery=discovery)


if __name__ == "__main__":
    main()
