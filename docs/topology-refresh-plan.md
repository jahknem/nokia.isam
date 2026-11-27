# Topology refresh: state and required changes

This records what the complete topology refresh (an ONT, a PON or a card: every part
proven present, confirmed absent, or named as a gap) still needs before it can land on
`main`. It is the hand-over for the topology PR; keep it current until that PR merges.

## Where things are

On `main` (PR #16): the semantic graph, catalogs, discovery adapters per (parent kind,
child kind), card ports from `show interface port` (strict port names), owner
re-resolution, the read-only IHUB families and `isam_topology_discovery`. All resource
families the refresh reads are on `main` too (#11–#15, #17, #18).

Not on `main`, only in local branches of the maintainer's checkout:

| Part | Purpose |
| --- | --- |
| `topology/refresh.py` | refresh planner: context round, discovery rounds, configuration reads, reference rounds, `evaluate()` |
| `topology/cards.py` | card-type rules (children per card type, entries created with the card, NT-only parts) |
| `topology/objects.py`, `scopes.py`, `dependencies.py`, `write_order.py` | object model, scopes, part dependency graph, write order |
| `relations/` (one file per family) | identity, object kind, `creates`, `created_with`, `references`, `observable`, write prerequisites with live evidence |
| `read.py`, `plugins/modules/isam_read.py` | several isolated targeted reads in one task, one outcome each |
| tests | `test_topology_refresh.py`, `test_relations.py`, `test_topology_write_order.py`, `test_topology_dependencies.py`, `test_isam_read.py` |

**Those local branches must never be pushed.** They descend from an unsanitized history
(private paths, internal addresses, production host names). The topology PR is cut from
`main` and the files are carried over and checked for host names, internal addresses and
local paths before the first push (AGENTS.md, "Sanitization").

## Required changes for the topology PR

1. **Port onto `main`.** Carry the parts above onto a branch from `main`. `read.py` /
   `isam_read` must use the shared read contract (`facts_base.get_targeted_config`,
   `read_outcomes`, `targeted.ABSENCE_POLICY`) instead of their own probe logic; the
   relations' imports of family code now resolve, since every family is on `main`.
   Register `isam_read` in the contract scope and the 0.3.13 lock lists.
2. **Owner existence before `created_with`.** `evaluate()` may turn an empty read of an
   entry the device creates with its object (`interface port ont:<ont>`) into "present
   with defaults" only when that object exists: from discovery, or from its creating
   section (relations `creates`). Object absent: the entry is absent. Undecided: gap.
   (Fixed in the local branch with tests; a free ONT index was reported with a present
   interface entry before.)
3. **`xdsl_onts` is created with every ONT**, GPON/Ethernet ones included (live read
   2026-11-27: `flat detail` prints `no dpbo-profile` for an existing ONT, header only for
   a free index). The relation carries `created_with` (local branch); no applicability
   rule is needed.
4. **Dependency gaps of a missing parent.** A bridge port or QoS entry of a missing UNI is
   read as `unknown` with `dependency_gap: lower-interface`. `evaluate()` must conclude
   "absent" when the parent object is confirmed absent, and keep the gap otherwise.
5. **`_resolve_owners` on fresh evidence only** (review of #16) — done in the review
   follow-up PR: `attach_discovery` applies the same freshness rule as `coverage()`.
   The refresh planner must pass its run window (`now`, `max_age_seconds`,
   `collected_since`) when it attaches discovery.
6. **Card rules as data, one structure per kind.** Consolidate the keys in `cards.py`;
   move `_ALIASES` (prefixes such as `pon:`, `ont:`, `uni:`, `vlan:`) into the object
   model. Fleet evidence for the rules: read-only fleet survey, 2026-11-26.
7. **Relations and module semantics must agree.** The relations knew on 2026-11-25 that
   the ANI and NTP entries are created with the ONT, but the modules still sent
   `no tca-thresh` / `configure ntp no ont` (no effect on the device) until 2026-11-27. Add
   a test: a section with `created_with` must not render a removal of the entry in
   `deleted`/`overridden`, only resets.
8. **Write order: QoS before bridge VLANs.** A VLAN on a UNI's bridge port needs bandwidth
   profiles on that UNI's upstream queues first (VLAN MGT error 277). Live 2026-11-27:
   VLAN 99 needed queue 0; VLAN 20 on L2 forwarder 699 needed queues 4 and 5 (the queue
   follows the VLAN's QoS mapping). The relation exists (`relations/bridges.py`);
   `write_order.py` must enforce it and the planner must name the queues.
9. **Core follow-ups that affect the refresh** — done in the review follow-up PR: the
   detail probe is decided per command (an instance check of another section no longer
   switches it off); whole-node reads honour `ABSENCE_POLICY`; a missing dependency on
   the detail probe keeps its `dependency_gap` label.

## Live evidence so far (DS-LIN-TEST-01)

| Refresh | Result |
| --- | --- |
| card NDPS-C `lt:1/1/1` | complete, 0 gaps |
| card NDLT-F `lt:1/1/3` | 342 gaps, run before the later probe fixes; rerun pending |
| cards NELT-B, FGLT-B | runs failed on a VPN drop; rerun pending |
| ONT `1/1/5/1/3` (exists) | 46 sections: 25 present, 15 absent, 6 gaps (5 × `isam_dhcp_relay` not observable, by design; 1 × `xdsl_onts`, module was not on the branch) |
| ONT `1/1/5/1/4` (free index) | 8 sections: 7 absent, 1 gap (`xdsl_onts`, as above) |

`isam_dhcp_relay` stays a named gap: every read answers the same whether it is set or not
(`ABSENCE_POLICY` `unobservable`). The ONT write path of every family was verified live on
a scratch ONT (docs/live-validation-2026-11-27-ont.md).

## Out of scope for the repository

The read-only absence matrix generator and the live write/refresh drivers stay in the
maintainer's local tooling; they are not part of the collection.
