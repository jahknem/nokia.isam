#!/usr/bin/env python
"""Audit canonical resources for explicit object relationships (no device access).

PYTHONPATH=.tox/py312-core219/collections .tox/py312-core219/bin/python \
    tools/topology_report.py private-facts.json --msan DEVICE [--graph private-graph.json]

Accepts plain ansible_network_resources or an isam_facts module result. Summary
output is counts only. Graph output contains object/profile identities, so keep
it private. It is not a refresh certificate or an execution plan.
"""

import argparse
from collections import Counter
import json
import os

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("capture")
    parser.add_argument("--msan", required=True)
    parser.add_argument("--graph")
    args = parser.parse_args()
    with open(args.capture) as source:
        data = json.load(source)
    resources = data.get("ansible_facts", data).get("ansible_network_resources", data)
    graph = build_graph(resources, args.msan)
    print("Objects/configuration:", dict(sorted(Counter(n["kind"] for n in graph["nodes"]).items())))
    print("Edges:", dict(sorted(Counter(e["relation"] for e in graph["edges"]).items())))
    print("Mapping gaps:", dict(sorted(Counter(g["reason"] for g in graph["gaps"]).items())))
    catalog = export_catalog()
    evidence = Counter(e for obj in catalog["objects"].values()
                       for e in obj.get("discovery_evidence", {}).values())
    print("Discovery adapters by evidence:", dict(sorted(evidence.items())))
    print("Unmodeled configuration domains:", catalog["unmodeled_configuration_domains"])
    print("Partial configuration domains:", catalog["partial_configuration_domains"])
    print("Recursive coverage: NOT certified (fresh scoped discovery still required)")
    if args.graph:
        # Do not truncate an existing artifact or accidentally make it readable
        # to other users. No raw configuration is included in this artifact.
        fd = os.open(args.graph, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as target:
            json.dump(graph, target, indent=1)
            target.write("\n")


if __name__ == "__main__":
    main()
