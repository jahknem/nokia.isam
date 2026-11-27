# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""A whole refresh in one module call, on one connection (isam_refresh).

The rounds of topology/refresh.py run here back to back: the context read, the
discovery rounds, the configuration reads and the reference rounds, then
``evaluate()``. Every discovery source is read once for the whole run (one
``show interface stack`` for every bridge-port and VLAN-port round of a card); reads
go through isam_read's isolated read path, so every targeted read follows the core
read contract. Only read commands are sent.

The freshness window of the evaluation is the run itself: discovery collected during
the run is fresh for as long as the run took, and nothing from before the run counts.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import time
from datetime import datetime, timezone

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read import read_all
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import refresh
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.discovery import _validate_parent, result
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.identity import UnknownIdentity
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.source_reads import (
    enumerate_request,
    prepare,
)

# A refresh never loops forever: discovery has as many rounds as the object model is
# deep, reference rounds as long as definitions name further definitions.
MAX_ROUNDS = 20


def _utc(seconds):
    """ISO-8601 UTC with "Z", the form discovery timestamps use."""
    return datetime.fromtimestamp(seconds, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(module, root, sections=None, allow_broad_read=False, data=False):
    """The refresh outcome of ``root`` (kind, identity) plus run statistics.

    ``sections``: a partial refresh (see refresh.wanted_sections). ``data``: keep the
    configuration read results in the outcome (``reads``), credentials removed.
    """
    refresh.wanted_sections(sections)  # unknown names fail before any read
    _validate_parent(*root)  # so does an invalid root (UnknownIdentity)
    started = time.time()
    connections = []

    def connection():
        # The reads (isam_read's path) and the discovery sources share one connection.
        if not connections:
            connections.append(getattr(module, "_connection", None) or get_resource_connection(module))
        return connections[0]

    sources = {}
    context_results, _status = read_all(module, refresh.context_reads(root))
    context = refresh.context_from(context_results)

    discovery, rounds = [], 0
    while True:
        requests, _unimplemented = refresh.discovery_requests(root, discovery, context, sections)
        if not requests:
            break
        rounds += 1
        if rounds > MAX_ROUNDS:
            raise RuntimeError("discovery did not converge in %d rounds" % MAX_ROUNDS)
        for request in requests:
            prepared = prepare(request["kind"], request["identity"], request["child_kind"])
            try:
                found = enumerate_request(sources, connection, prepared, allow_broad_read)
            except UnknownIdentity:
                # A source reply not understood completely (no footer or terminator,
                # an unrecognized row): this relation is an error, the refresh goes on
                # and names the gap.
                kind, identity, child_kind, adapter = prepared
                found = result(kind, identity, child_kind, "error", command=adapter["command"],
                               read_scope=adapter["read_scope"], error="source_not_understood")
            discovery.append(found)

    objects = refresh.known_objects(root, discovery)
    reads, _needs = refresh.configuration_reads(objects, context, sections)
    results, _status = read_all(module, reads)
    results = context_results + results
    reference_rounds = 0
    while True:
        pending = refresh.pending_reference_reads(results)
        if not pending:
            break
        reference_rounds += 1
        if reference_rounds > MAX_ROUNDS:
            raise RuntimeError("reference reads did not converge in %d rounds" % MAX_ROUNDS)
        more, _status = read_all(module, pending)
        results += more

    finished = time.time()
    outcome = refresh.evaluate(root, discovery, results, now=_utc(finished),
                               max_age_seconds=int(finished - started) + 5,
                               collected_since=_utc(started - 1), context=context, sections=sections)
    outcome["discovery"] = discovery
    outcome["stats"] = {
        "seconds": round(finished - started, 1),
        "discovery_rounds": rounds,
        "discovery_requests": len(discovery),
        "source_reads": len(sources),
        "configuration_reads": len(reads),
        "reference_rounds": reference_rounds,
        "ids_read": sum(len(read.get("ids") or []) for read in reads),
    }
    if data:
        outcome["reads"] = results
    return outcome
