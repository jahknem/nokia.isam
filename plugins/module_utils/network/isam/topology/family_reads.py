# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Family reads for a refresh: one ``flat detail`` read instead of many targeted reads.

A refresh of a card needs a section for every port of the card. For some sections the
whole family, read once with ``flat detail``, costs a fraction of one targeted read per
port; for others (QoS interfaces) the family is so large that targeted reads win. The
choice is data (FAMILY_READS), from read-only measurements, not a constant in code.

Proof stays the core read contract's (docs/targeted-read-contract.md):

- present: the family's own parser returns the instance from the reply;
- confirmed absent: the reply is complete (it ends with the device's terminal
  delimiter) and no line of it names the instance at its position -- ``flat detail``
  prints a line for every existing instance, also one with default values only;
- otherwise unverified: a line names the instance but the parser did not return it,
  the reply is incomplete, or the section answers the same whether it is set or not
  (targeted.ABSENCE_POLICY). Unverified instances are read targeted afterwards.

Absence is never taken from the parsed catalog alone: a line the parser does not
recognize would make an existing instance vanish from it.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER, absence_policy

# Measured read-only 2026-11-27: lab DS-LIN-TEST-01 (NDLT-F card lt:1/1/3, 48 lines) and
# one production MSAN with eight LT cards. Targeted: ~0.3-0.9 s per id (flat, plus flat
# detail for a default-only instance). Family flat detail, production: pae port 2.1 s
# (17 KB), efm-oam interface 1.5 s (20 KB), xdsl imp-noise-sensor 2.4 s (59 KB, both
# ends), l2cp user-port and pppoe-client interface 0.9 s (header only), interface port
# 13.5 s (210 KB); qos interface 98.5 s (1 MB, targeted stays cheaper).
# min_ids: from how many instances of one refresh the family read is cheaper.
_EVIDENCE = "read-only timing 2026-11-27, lab and one production MSAN (docs/topology-refresh-plan.md)"
FAMILY_READS = {
    ("isam_system_security", "pae.ports"): {
        "command": "info configure system security pae port flat detail",
        "prefix": "configure system security pae port", "min_ids": 4},
    ("efm_oam_interface", "config"): {
        "command": "info configure efm-oam interface flat detail",
        "prefix": "configure efm-oam interface", "min_ids": 4},
    ("xdsl_inm", "near_end"): {
        "command": "info configure xdsl imp-noise-sensor flat detail",
        "prefix": "configure xdsl imp-noise-sensor near-end", "min_ids": 4},
    ("xdsl_inm", "far_end"): {
        "command": "info configure xdsl imp-noise-sensor flat detail",
        "prefix": "configure xdsl imp-noise-sensor far-end", "min_ids": 4},
    ("l2cp_user_port", "config"): {
        "command": "info configure l2cp user-port flat detail",
        "prefix": "configure l2cp user-port", "min_ids": 4},
    ("pppoe_client_interface", "config"): {
        "command": "info configure pppoe-client interface flat detail",
        "prefix": "configure pppoe-client interface", "min_ids": 4},
    ("interfaces", "config"): {
        "command": "info configure interface port detail flat",
        "prefix": "configure interface port", "min_ids": 40},
}

# The device closes every flat reply with this delimiter, also an empty one
# (topology/discovery.py, _FLAT_TERMINATOR): without it the reply may be cut short.
_TERMINATOR = re.compile(r"#-{10,}")


def family_read_for(resource, section, ids):
    """The FAMILY_READS entry to use for this read, or None (read targeted).

    Never for a section under ABSENCE_POLICY (its detail read cannot prove absence),
    nor below the entry's minimum number of instances.
    """
    entry = FAMILY_READS.get((resource, section))
    if entry is None or absence_policy(resource, section) is not None:
        return None
    if not isinstance(TARGETED_GATHER.get(resource, {}).get(section), str):
        return None
    return entry if len(ids) >= int(entry["min_ids"]) else None  # type: ignore[call-overload]


def complete(reply):
    lines = [line.strip() for line in str(reply or "").splitlines() if line.strip()]
    return bool(lines) and bool(_TERMINATOR.fullmatch(lines[-1]))


def mentioned(reply, prefix, identity):
    """Whether a line of the reply names ``identity`` at the instance position."""
    pattern = re.compile(r"^\s*%s %s(?:\s|$)" % (re.escape(prefix), re.escape(str(identity))))
    return any(pattern.match(line) for line in str(reply or "").splitlines())


def classify(reply, entry, ids, parsed_ids):
    """(returned, confirmed_absent, unverified) for ``ids`` from one family reply.

    parsed_ids: the identities the family's parser returned from the reply.
    """
    whole = complete(reply)
    returned, absent, unverified = [], [], []
    for identity in ids:
        if str(identity) in parsed_ids:
            returned.append(identity)
        elif whole and not mentioned(reply, entry["prefix"], identity):
            absent.append(identity)
        else:
            unverified.append(identity)
    return returned, absent, unverified
