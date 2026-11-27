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
  - With I(requests), several relations are enumerated in one call. Each distinct
    source command is read once and every request is enumerated from that reply,
    with the same rules as a single call (C(discoveries), one record per request,
    in request order). A refresh round of one card (bridge ports of every line)
    then costs one read of the interface stack instead of one per line.
version_added: "1.1.0"
author: Jan Kühnemund (@jahknem)
options:
  kind:
    description:
      - Parent object kind in the semantic topology graph.
      - Required unless I(requests) is given; mutually exclusive with it.
    type: str
    choices: [msan, rack, shelf, pon, ont, ont_slot, card, applique, uni, xdsl_line, ethernet_port, bonding_group, lag,
              bridge_port]
  identity:
    description:
      - Canonical identity of the parent object.
      - For C(kind=bridge_port), use the encoding C(<port kind>:<port identity>),
        for example C(lag:1/1/8/1), C(xdsl_line:1/1/3/1) or C(uni:1/1/5/1/3/1/1).
      - Required unless I(requests) is given.
    type: str
  child_kind:
    description:
      - Direct child kind to enumerate.
      - Required unless I(requests) is given.
    type: str
    choices: [rack, shelf, card, applique, ont, ont_slot, uni, pon, xdsl_line, ethernet_port, cage, bonding_group, lag,
              channel_pair, transceiver, bridge_port, vlan_port, uplink]
  requests:
    description:
      - Several enumerations in one call, each with I(kind), I(identity) and
        I(child_kind) as above. Every distinct source command is read once.
      - An invalid parent or relation in any request fails the call before any read.
    type: list
    elements: dict
    suboptions:
      kind:
        description: Parent object kind.
        type: str
        required: true
        choices: [msan, rack, shelf, pon, ont, ont_slot, card, applique, uni, xdsl_line, ethernet_port, bonding_group,
                  lag, bridge_port]
      identity:
        description: Canonical identity of the parent object (see I(identity)).
        type: str
        required: true
      child_kind:
        description: Direct child kind to enumerate.
        type: str
        required: true
        choices: [rack, shelf, card, applique, ont, ont_slot, uni, pon, xdsl_line, ethernet_port, cage, bonding_group,
                  lag, channel_pair, transceiver, bridge_port, vlan_port, uplink]
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

- name: Enumerate the bridge ports of two lines with one read of the interface stack
  nokia.isam.isam_topology_discovery:
    requests:
      - {kind: xdsl_line, identity: 1/1/3/1, child_kind: bridge_port}
      - {kind: xdsl_line, identity: 1/1/3/2, child_kind: bridge_port}
    allow_broad_read: true
  register: line_bridges

- name: Enumerate the VLAN ports of one bridge port
  nokia.isam.isam_topology_discovery:
    kind: bridge_port
    identity: lag:1/1/8/1
    child_kind: vlan_port
    allow_broad_read: true
  register: lag_vlans
"""

RETURN = """
discoveries:
  description: With I(requests), one enumeration result per request, in request order, each shaped like C(discovery).
  returned: when I(requests) is given
  type: list
  elements: dict
discovery:
  description: One direct-neighbor enumeration result.
  returned: without I(requests)
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


KINDS = ["msan", "rack", "shelf", "pon", "ont", "ont_slot", "card", "applique", "uni",
         "xdsl_line", "ethernet_port", "bonding_group", "lag", "bridge_port"]
CHILD_KINDS = ["rack", "shelf", "card", "applique", "ont", "ont_slot", "uni", "pon", "xdsl_line",
               "ethernet_port", "cage", "bonding_group", "lag", "channel_pair", "transceiver",
               "bridge_port", "vlan_port", "uplink"]


def _prepare(kind, identity, child_kind):
    """(kind, parent identity, child kind, adapter) of one request; raises UnknownIdentity."""
    _validate_parent(kind, identity)
    if kind == "bridge_port":
        identity = decode("bridge_port", identity)[1]
    return kind, identity, child_kind, adapter_for(kind, child_kind)


def _enumerate(sources, connection, request, allow_broad_read):
    """The discovery record of one prepared request.

    ``sources`` caches each command's reply for this call: (response, status) or the
    exception its read raised, so every request on one source sees the same reply and
    the source is read once. Raises UnknownIdentity for a source not understood.
    """
    kind, identity, child_kind, adapter = request
    command, read_scope = adapter["command"], adapter["read_scope"]
    if read_scope in ("device", "family") and not allow_broad_read:
        return result(kind, identity, child_kind, "unsupported", command=command, read_scope=read_scope,
                      error="broad_enumeration_requires_allow_broad_read")
    if command not in sources:
        try:
            sources[command] = _read(connection(), command)
        except Exception as exc:
            sources[command] = exc
    read = sources[command]
    if isinstance(read, Exception):
        # The exception text may echo device output (configuration); report only a
        # stable error class and the exception type, as ihub_config does.
        return result(kind, identity, child_kind, "error", command=command, read_scope=read_scope,
                      error="%s (%s)" % (error_class(read), type(read).__name__))
    response, read_status = read
    if read_status != "ok":
        return result(kind, identity, child_kind, "unsupported", command=command,
                      read_scope=read_scope, error="enumeration_source_%s" % read_status)
    try:
        if (kind, child_kind) == ("pon", "ont"):
            return parse_ont_serials(response, identity)
        if (kind, child_kind) == ("ont", "ont_slot"):
            return parse_ont_slots(response, identity)
        return enumerate_children(kind, identity, child_kind, response)
    except UnknownIdentity:
        raise
    except Exception as exc:
        return result(kind, identity, child_kind, "error", command=command, read_scope=read_scope,
                      error="%s (%s)" % (error_class(exc), type(exc).__name__))


def main():
    module = AnsibleModule(
        argument_spec=dict(
            kind=dict(type="str", choices=KINDS),
            identity=dict(type="str"),
            allow_broad_read=dict(type="bool", default=False),
            child_kind=dict(type="str", choices=CHILD_KINDS),
            requests=dict(type="list", elements="dict", options=dict(
                kind=dict(type="str", required=True, choices=KINDS),
                identity=dict(type="str", required=True),
                child_kind=dict(type="str", required=True, choices=CHILD_KINDS),
            )),
        ),
        required_one_of=[["kind", "requests"]],
        mutually_exclusive=[["kind", "requests"], ["identity", "requests"], ["child_kind", "requests"]],
        required_together=[["kind", "identity", "child_kind"]],
        supports_check_mode=True,
    )
    params = module.params
    batch = params["requests"] is not None
    wanted = params["requests"] if batch else [
        {"kind": params["kind"], "identity": params["identity"], "child_kind": params["child_kind"]}]
    try:
        prepared = [_prepare(item["kind"], item["identity"], item["child_kind"]) for item in wanted]
    except UnknownIdentity as exc:
        module.fail_json(msg=str(exc), changed=False)

    # Read-only: enumeration never changes the device, so check mode reads like a normal run.
    connections = []

    def connection():
        if not connections:
            connections.append(get_resource_connection(module))
        return connections[0]

    sources = {}
    try:
        discoveries = [_enumerate(sources, connection, request, params["allow_broad_read"]) for request in prepared]
    except UnknownIdentity as exc:
        module.fail_json(msg=str(exc), changed=False)
    if batch:
        module.exit_json(changed=False, discoveries=discoveries)
    module.exit_json(changed=False, discovery=discoveries[0])


if __name__ == "__main__":
    main()
