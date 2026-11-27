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

## Terms

- **Discovery**: finding which child objects exist under a parent (the ONTs of a PON, the
  UNIs of an ONT slot, the xDSL lines of a card, the bridge ports of a line, the VLAN
  ports of a bridge port). An adapter per (parent kind, child kind) names the source
  (an operational table such as `show interface port` / `show interface stack`, or a
  configuration family read) and its read scope (`device`, `family`, `instance`). Only an
  `ok` result -- source understood completely, footer count and terminator confirmed --
  may say "exactly these children"; a failed or partial read never means "none".
  Results carry their collection time, so stale evidence is not used.
- **Configuration read**: what is configured on a known object, one outcome per
  (object, section): present, confirmed absent, or a gap with a reason.
- **Refresh**: discovery rounds (card → lines → bridge ports → VLAN ports), then the
  configuration reads of every applicable section of every discovered object, then the
  shared definitions they reference.

## Performance: where the time goes and what to change

Goal of the model: read only what a question needs, without whole families. Measured
on DS-LIN-TEST-01 (2026-11-26/27) and in NOC (production MSAN, 2026-11-25):

| Scope | Reads | Time | Where the time goes |
| --- | --- | --- | --- |
| one existing ONT, complete (46 sections) | 52 targeted reads | 92 s | 27 s reads, 38 s discovery; ~7 separate playbook runs, each with a new SSH login |
| one missing ONT (8 sections) | 8 | 27 s | mostly overhead |
| NDLT-F card, 48 lines (1282 sections) | 1147 ids | 1100 s | **850 s discovery**, 232 s reads |
| whole lab configuration, `flat` + `flat detail` | 2 | 162 s | one session |
| whole production MSAN refresh (NOC) | families | 578 s | 241 s of it QoS; targeted QoS 0.36 s per port (32 in 11.5 s) |

Read sizes on the lab (`flat` / `flat detail`): xDSL lines 10.6 / 92 KB, bridge ports
47 / 248 KB, QoS interfaces 187 / 277 KB, EFM OAM 0.3 / 17.6 KB. A large production MSAN
renders configuration at about 4 KB/s (NOC), so a 250 KB detail read costs about a
minute there; a targeted read costs 0.05–1 s.

Conclusions:

- For a few objects or a few values (one ONT, some UNIs, one setting across ports),
  targeted reads win clearly; NOC already uses this for QoS.
- The fixed cost per session (playbook start, inventory, SSH login: ~10–15 s) dominates
  small refreshes: rounds must share one session.
- For complete coverage of a large object (a card), 1147 single reads plus repeated
  discovery lose against reading the families once. The planner has to choose per
  section.

### Plan: card refresh

1. **Read each discovery source once per run.** The bridge-port and VLAN-port discovery
   of every line reads the device-wide `show interface stack`: 96 reads of ~8.5 s for one
   NDLT-F card (~820 s). Read it once and enumerate both child kinds for every parent
   from it; likewise `show interface port` (xDSL lines and bonding groups share it).
   Expected: discovery from ~850 s to ~10–20 s. A source result carries its collection
   time; reuse it within the run's freshness window only.
2. **One session for the whole refresh.** Context round, discovery rounds, configuration
   and reference reads run in one module call (or one persistent connection) instead
   of one playbook per round. Expected: ~10–15 s saved per round (7 rounds for an ONT).
3. **Family or targeted read, per section.** For each (resource, section) the planner
   knows how many of the family's instances the refresh needs (e.g. all 48 lines of a
   card). Above a threshold, read the family once and filter by the card's identities;
   below it, read targeted.
   - Absence must stay provable: a family `flat` read omits default-only instances
     (16 of 48 NDLT-F lines on a production MSAN). Either read the family with
     `flat detail` (lists every existing instance; larger, see sizes above), or read
     the family `flat` and probe only the instances missing from it with a targeted
     `flat detail`. Choose by measured size: the probe variant when `flat detail` is
     much larger than `flat` (EFM OAM: 54×), the family detail read otherwise.
   - The threshold is a measured cost model per section (bytes of the family read vs.
     instance count × targeted read time), recorded as data next to the card rules,
     not a constant in code.
4. **Skip what cannot apply.** Card rules already exclude sections per card type
   (`not_applicable`); extend them with the measured "created with the card" entries so
   those are not read just to confirm defaults.
5. **Benchmark before and after**, read-only: the NDLT-F card on the lab (`lt:1/1/3`) and
   one production card of each type (NDLT-F, FGLT-B, NELT-B), each as today's refresh,
   with shared discovery sources, and with per-section family reads. Record wall time,
   bytes read, sessions opened and the evaluation (gaps must not increase).

### Plan: partial queries

A "value query" entry point: given objects and attributes (or sections), plan only the
sections that hold them, plus the discovery needed to identify the objects. The
relations already map each object kind to its applicable (resource, section,
identity); add the attribute → section mapping from the argspecs. Same outcome rules
as the refresh (present / confirmed absent / gap), so a caller can act on the result
without a complete refresh.

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
