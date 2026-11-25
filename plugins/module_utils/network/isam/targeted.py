# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Targeted gathering: which resources read single instances, by which identity field.

When ``config`` names instances, ``state: gathered`` reads only those instances.
Without ``config`` the whole resource is read, as before. Only identity fields matter
for the selection; absent instances are simply missing from the result.

The tables are views of relations/<family>.py, the one place a family declares
its instance lists and identities (pure data; tools outside Ansible read those files).

resource (facts name) -> {instance list: identity}
  instance list: "config" when config itself is the list, else the key in config
                 (dotted for nested keys, e.g. "syslog.destinations").
  identity:      a field name, or a list of field names for a composite identity.

Lists inside an instance (QoS queues, bridge VLANs, ...) are read with their instance.
Resources without instance lists (dhcp_server, generic_pon, l2cp, ...) are single
settings blocks and always read completely. Resources not read through the facts
registry (pppoe_client_*, pppoel2_statistics) are keyed by their module name.

Whole-node catalog families: a few instance lists have no single-instance read --
the device only exposes the whole node (interface_alarms; the vlan priority-regen
profiles). For them a targeted request reads the node once and reports each named
instance from the parsed catalog (present, or unknown -- absence from the catalog
is not established absence, because the parser's catalog completeness is
unverified); the gathered string stays the full catalog. The read scope of every
targeted resource is machine-readable in TARGETED_READ_SCOPE ('whole_node' for
these families, 'instance' otherwise). That is the documented exception to the
scoped-read contract (see docs/targeted-gathering.md, "Whole-node reads").

TARGETED_WRITES: resources whose merged/replaced/deleted also compare against only
the named instances (resources made of instance lists, where that is exact).
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.relations import FAMILIES

# IHUB families are whole-source reads and promise no targeted gathering.
TARGETED_GATHER = {
    resource: {name: section["identity"] for name, section in family["sections"].items()}
    for resource, family in FAMILIES.items()
    if family["sections"] and family.get("source") != "ihub"
}

# Read scope per targeted resource: what an explicit request (state gathered,
# config names instances) actually sends to the device. Derived from the read
# commands the facts classes send, not from the topology ownership scope
# (device_global describes ownership, not CLI read scope).
#   "instance"   -- one scoped command per requested instance (the scoped-read
#                   contract; the default for every TARGETED_GATHER resource not
#                   listed here).
#   "whole_node" -- the firmware exposes no single-instance read: one whole-node
#                   command serves all requested instances, and each instance is
#                   reported from the parsed catalog (present / unknown; see
#                   docs/targeted-gathering.md, "Whole-node reads").
# Declared as "read_scope" in relations/<family>.py; keep in sync with the facts classes that call facts_base.get_whole_node_targeted
# (tests/unit/modules/network/isam/test_targeted_gathered.py asserts both
# directions).
TARGETED_READ_SCOPE = {resource: family["read_scope"] for resource, family in FAMILIES.items() if "read_scope" in family}


def read_scope(resource):
    """The read scope an explicit targeted request for ``resource`` triggers.

    'whole_node' for the catalog families with no single-instance read,
    'instance' for every other targeted resource.
    """
    return TARGETED_READ_SCOPE.get(resource, "instance")


TARGETED_WRITES = tuple(sorted(resource for resource, family in FAMILIES.items() if family.get("targeted_writes")))
