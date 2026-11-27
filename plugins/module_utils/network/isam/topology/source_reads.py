# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Reading discovery sources: one reply per command per run, shared by every request.

Used by isam_topology_discovery (one call, several requests) and isam_refresh (one
whole refresh). ``sources`` caches each command's reply for the caller's run, so a
device-wide table (``show interface stack``) is read once however many parents are
enumerated from it.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

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
    utc_now,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import (
    UnknownIdentity,
    decode,
)


def read_source(connection, command):
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


def prepare(kind, identity, child_kind):
    """(kind, parent identity, child kind, adapter) of one request; raises UnknownIdentity.

    A bridge-port parent is given as "<port kind>:<port identity>" (module parameter)
    or as the (port kind, port identity) pair the planner uses.
    """
    if kind == "bridge_port" and isinstance(identity, (list, tuple)):
        identity = "%s:%s" % tuple(identity)
    _validate_parent(kind, identity)
    if kind == "bridge_port":
        identity = decode("bridge_port", identity)[1]
    return kind, identity, child_kind, adapter_for(kind, child_kind)


def enumerate_request(sources, connection, request, allow_broad_read):
    """The discovery record of one prepared request.

    ``sources`` caches each command's reply for this call: (response, status, read at)
    or the exception its read raised, so every request on one source sees the same reply
    and the source is read once. A record's ``collected_at`` is the time the source was
    read, not the time it was parsed. Raises UnknownIdentity for a source not understood.
    """
    kind, identity, child_kind, adapter = request
    command, read_scope = adapter["command"], adapter["read_scope"]
    if read_scope in ("device", "family") and not allow_broad_read:
        return result(kind, identity, child_kind, "unsupported", command=command, read_scope=read_scope,
                      error="broad_enumeration_requires_allow_broad_read")
    if command not in sources:
        try:
            response, status = read_source(connection(), command)
            sources[command] = (response, status, utc_now())
        except Exception as exc:
            sources[command] = exc
    read = sources[command]
    if isinstance(read, Exception):
        # The exception text may echo device output (configuration); report only a
        # stable error class and the exception type, as ihub_config does.
        return result(kind, identity, child_kind, "error", command=command, read_scope=read_scope,
                      error="%s (%s)" % (error_class(read), type(read).__name__))
    response, read_status, read_at = read
    if read_status != "ok":
        return result(kind, identity, child_kind, "unsupported", command=command, collected_at=read_at,
                      read_scope=read_scope, error="enumeration_source_%s" % read_status)
    try:
        if (kind, child_kind) == ("pon", "ont"):
            found = parse_ont_serials(response, identity)
        elif (kind, child_kind) == ("ont", "ont_slot"):
            found = parse_ont_slots(response, identity)
        else:
            found = enumerate_children(kind, identity, child_kind, response)
        found["collected_at"] = read_at
        return found
    except UnknownIdentity:
        raise
    except Exception as exc:
        return result(kind, identity, child_kind, "error", command=command, read_scope=read_scope,
                      error="%s (%s)" % (error_class(exc), type(exc).__name__))
