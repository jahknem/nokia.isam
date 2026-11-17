#!/usr/bin/env python
"""Summarise what a flat ISAM configuration contains that the resource families do not model.

Usage (the collection must be importable, e.g. the tree tox builds):
    PYTHONPATH=.tox/collections python tools/gap_report.py <info-configure-flat.txt> [--json] [--top N]

Prints only CLI keyword/attribute *names* and counts, never values, so the output is safe
to share even for a live capture.
"""
from __future__ import absolute_import, division, print_function

import argparse
import json
import sys

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
    gap_report,
    nesting_stats,
    parse_config_tree,
)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("capture")
    parser.add_argument("--json", action="store_true", help="print the full report as JSON")
    parser.add_argument("--top", type=int, default=15, help="unclaimed nodes to list")
    args = parser.parse_args(argv)

    with open(args.capture, errors="replace") as fh:
        text = fh.read()
    report = gap_report(parse_config_tree(text))
    if args.json:
        json.dump(report, sys.stdout, indent=2, sort_keys=True)
        print()
        return 0

    stats = nesting_stats(text)
    print("lines by nesting source: %s" % ", ".join("%s=%d" % kv for kv in sorted(stats.items())))
    print()
    print("%-30s %7s %8s  %s" % ("family", "lines", "unmod.", "nodes with unmodelled attributes"))
    for family, entry in sorted(report["families"].items()):
        n_attrs = sum(len(v) for v in entry["unmodelled"].values())
        nodes = ", ".join(sorted(entry["unmodelled"]))
        flag = "" if entry["argspec"] else " (no argspec found)"
        print("%-30s %7d %8d  %s%s" % (family, entry["lines"], n_attrs, nodes[:90], flag))
    unclaimed = sorted(report["unclaimed"].items(), key=lambda kv: (-kv[1], kv[0]))
    print()
    print("unclaimed: %d nodes, %d lines" % (len(unclaimed), sum(n for _k, n in unclaimed)))
    for node, n in unclaimed[:args.top]:
        print("  %6d  %s" % (n, node))
    return 0


if __name__ == "__main__":
    sys.exit(main())
