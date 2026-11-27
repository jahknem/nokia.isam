# Topology refresh: state and required changes

This records what the complete topology refresh (an ONT, a PON or a card: every part
proven present, confirmed absent, or named as a gap) still needs before it can land on
`main`. It is the hand-over for the topology PR; keep it current until that PR merges.

## Where things are

On `main`: the semantic graph, discovery adapters per (parent kind, child kind), card
ports from `show interface port` (strict port names), owner re-resolution on fresh
evidence, the read-only IHUB families and `isam_topology_discovery` (#16, #19); every
resource family the refresh reads (#11–#15, #17, #18).

With the topology PR (`feat/topology-refresh`), ported from the local branches onto
the core read contract and sanitized:

| Part | Purpose |
| --- | --- |
| `topology/refresh.py` | refresh planner: context round, discovery rounds, configuration reads, reference rounds, `evaluate()` |
| `topology/cards.py` | card-type rules (children per card type, entries created with the card, NT-only parts) |
| `topology/objects.py`, `scopes.py`, `dependencies.py`, `write_order.py` | object model, scopes, part dependency graph, write order |
| `relations/` (one file per family) | identity, object kind, `creates`, `created_with`, `references`, `observable`, write prerequisites with live evidence; replaces `topology/catalogs/` (same exported catalog, plus `creates`, `created_with`, `requires`) |
| `read.py`, `plugins/modules/isam_read.py` | several isolated targeted reads in one task, one outcome each, `dependency_gaps` per unverified id |

The local branches (`model/refresh-contract`, `wip/ont-refresh`) must still never be
pushed: they descend from an unsanitized history. They hold nothing the topology PR
needs any more, except the live drivers, which stay out of the repository.

## Required changes for the topology PR

Done in the topology PR:

1. **Port onto `main`.** `isam_read` reads through the family facts classes, so every
   targeted read uses the shared contract (`get_targeted_config`, `read_outcomes`,
   `ABSENCE_POLICY`). Registered in the contract scope, the API baseline and the 0.3.13
   inventory lock. `discovery.py` and `isam_topology_discovery` stay as on `main`.
2. **Owner existence before `created_with`**: an empty read of an entry the device
   creates with its object is "present with defaults" only when that object exists;
   object absent: the entry is absent; undecided: gap.
3. **`xdsl_onts` is created with every ONT** (relation `created_with`, live read
   2026-11-27).
4. **Dependency gaps of a missing parent**: `isam_read` reports `dependency_gaps`;
   `evaluate()` concludes "absent" when the entry's object or an ancestor is proven
   absent, and keeps the gap otherwise, labelled `dependency_gap:<label>`.
5. **`_resolve_owners` on fresh evidence only** (done in #19).
7. **Relations and module semantics agree**: `test_created_with_semantics.py` runs every
   `created_with` section through its module in `deleted` and `overridden`; none
   removes the entry, `deleted` resets.
8. **Write order: QoS before bridge VLANs**: `relations/bridges.py` `requires`, enforced
   by `write_order.py` (`test_the_uni_upstream_bandwidth_exists_before_its_bridge_port_takes_a_vlan`).
9. **Core follow-ups** (done in #19).

Also in the topology PR: a bare QoS index belongs to the LAG where one exists (QOS MGT
error 216, lab 2026-11-25); a DSL line and its bonding group stay candidates (owner not
verified on a device, open). Conflicting existence evidence is a gap. `relations/` and
`TARGETED_GATHER` are kept in step by a test.

Still open:

6. **Card rules as data, one structure per kind.** Consolidate the keys in `cards.py`;
   move `_ALIASES` (prefixes such as `pon:`, `ont:`, `uni:`, `vlan:`) into the object
   model. Fleet evidence for the rules: read-only fleet survey, 2026-11-26.
10. **Performance**: the card-refresh and partial-query plans below. Step 1 (each
   discovery source once per round: `isam_topology_discovery` `requests`) is done on
   `perf/shared-discovery`, together with step 2 (one session: `isam_refresh`) and
   partial refreshes (`sections`). Lab benchmarks (read-only, DS-LIN-TEST-01,
   2026-11-27):

   | Measurement | Before | After |
   | --- | --- | --- |
   | bridge-port round of 48 lines, NDLT-F `lt:1/1/3` | 48 single calls, 396 s | one `requests` call, 15.6 s (identical results) |
   | ONT `1/1/5/1/3`, complete | 92 s, 6 gaps | `isam_refresh` 28.7 s (19.5 s in the module), 3 source reads, 5 gaps (`isam_dhcp_relay` not observable) |
   | NDLT-F card `lt:1/1/3`, complete | 1100 s (850 s discovery, 99 source reads), 342 gaps | `isam_refresh` 294 s, 3 source reads, 150 gaps: 102 `isam_dhcp_relay` not observable, 48 `xdsl_bonding.groups` unverified (not parsed, see gaps above) |

   The card's remaining time is its 1138 targeted reads (~270 s): step 3.

   Step 3 (family or targeted read per section, `topology/family_reads.py`), measured
   read-only 2026-11-27 on the lab and on one production MSAN with eight LT cards
   (family `flat detail` vs. one targeted read per instance of the card):

   | Section | Targeted, 48-line card | Family, production |
   | --- | --- | --- |
   | `isam_system_security.pae.ports` | 43 s | 2.1 s (17 KB) |
   | `xdsl_inm` near and far end | 29 s | 2.4 s (59 KB, one read) |
   | `pppoe_client_interface` | 32 s | 0.9 s |
   | `efm_oam_interface` | 14 s | 1.5 s (20 KB) |
   | `l2cp_user_port` | 14 s | 0.9 s |
   | `interfaces` (246 ids) | 41 s | 13.5 s (210 KB) |
   | `qos_interfaces` (150 ids) | 47 s | 98.5 s (1 MB): stays targeted |

   Result on the lab (`isam_refresh`, NDLT-F `lt:1/1/3`): 294 s -> 118 s, 7 family reads,
   and all 1282 section outcomes identical to the targeted run; ONT `1/1/5/1/3` 28.7 s ->
   25.1 s, 46 outcomes identical. `isam_dhcp_relay` (not observable) is no longer read.
   Rendering on that production MSAN was 10-15 KB/s, faster than the 4 KB/s assumed
   above; a family read covers the whole MSAN, so the minimum instance counts are per
   section and conservative for larger MSANs.

Gaps found while porting (not topology code; each its own PR):

- ~~`isam_xdsl_bonding` parses only `group_assembly_time`~~: groups and boards are
  read since `fix/xdsl-bonding-sections` (writes still refused). Lab 2026-11-27, partial
  `isam_refresh` of NDLT-F `lt:1/1/3` with `sections: [xdsl_bonding]`: 33 s, complete,
  48 groups and the board present, one discovery request.
- The QoS guard that refuses settings an interface kind never accepts
  (`refused_settings`, `without_read_only`; live 2026-11-25, QOS MGT errors 45, 48, 216)
  exists only on the old `feature/write-order` lineage, not in `isam_qos_interfaces`
  on `main`.
- `isam_interfaces` `deleted` does not restore `admin-up` where the device default is
  up (ONT and VLAN-port interfaces); `isam_link_agg` `deleted` does not reset
  `load-sharing-policy`/`mode`. Reset forms unverified on a device.

## Terms

- **Discovery**: finding which child objects exist under a parent (the ONTs of a PON, the
  UNIs of an ONT slot, the xDSL lines of a card, the bridge ports of a line, the VLAN
  ports of a bridge port). An adapter per (parent kind, child kind) names the source
  (an operational table such as `show interface port` / `show interface stack`, or a
  configuration family read) and its read scope (`device`, `family` or `scoped`, as
  `discovery.result()` accepts; every current adapter is `device` or `family`). Only an
  `ok` result -- source understood completely, footer count and terminator confirmed --
  may say "exactly these children"; a failed (`error`/`unsupported`) or not completely
  understood source never means "none".
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
   time; reuse it within the run's freshness window only. The planner must pass a window
   that covers the whole run (`max_age_seconds` defaults to 300 s; today's card run took
   ~1100 s), otherwise later rounds count as `discovery_stale`.
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
   - Conditions of the probe variant (see `docs/targeted-read-contract.md`):
     - An instance missing from the family read counts as "flat shows nothing" only if
       the family reply is complete (terminator confirmed); otherwise there are no probe
       candidates and the section is a gap.
     - Not for `ABSENCE_POLICY` sections: `silent` ones print nothing in `detail` even
       when the instance exists; `unobservable` ones are never decidable.
     - Families whose single read already is `flat detail` (bridge ports, ONT interfaces
       and slots, equipment slots, PON interfaces) have no smaller `flat` to choose.
     - Whole-family reads do not get the probe automatically; the planner issues it,
       through a detail-only entry point (today's targeted helper sends `flat` first,
       which would repeat it).
     - A probe that hits a missing lower interface stays unknown (`dependency_gap`).
   - The threshold is a measured cost model per section (bytes of the family read vs.
     instance count × targeted read time), recorded as data next to the card rules (local `cards.py`),
     not a constant in code.
4. **Skip what cannot apply.** The card rules (local `cards.py`, not yet on `main`)
   already exclude sections per card type
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

## Terms

- **Discovery**: finding which child objects exist under a parent (the ONTs of a PON, the
  UNIs of an ONT slot, the xDSL lines of a card, the bridge ports of a line, the VLAN
  ports of a bridge port). An adapter per (parent kind, child kind) names the source
  (an operational table such as `show interface port` / `show interface stack`, or a
  configuration family read) and its read scope (`device`, `family` or `scoped`, as
  `discovery.result()` accepts; every current adapter is `device` or `family`). Only an
  `ok` result -- source understood completely, footer count and terminator confirmed --
  may say "exactly these children"; a failed (`error`/`unsupported`) or not completely
  understood source never means "none".
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
   time; reuse it within the run's freshness window only. The planner must pass a window
   that covers the whole run (`max_age_seconds` defaults to 300 s; today's card run took
   ~1100 s), otherwise later rounds count as `discovery_stale`.
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
   - Conditions of the probe variant (see `docs/targeted-read-contract.md`):
     - An instance missing from the family read counts as "flat shows nothing" only if
       the family reply is complete (terminator confirmed); otherwise there are no probe
       candidates and the section is a gap.
     - Not for `ABSENCE_POLICY` sections: `silent` ones print nothing in `detail` even
       when the instance exists; `unobservable` ones are never decidable.
     - Families whose single read already is `flat detail` (bridge ports, ONT interfaces
       and slots, equipment slots, PON interfaces) have no smaller `flat` to choose.
     - Whole-family reads do not get the probe automatically; the planner issues it,
       through a detail-only entry point (today's targeted helper sends `flat` first,
       which would repeat it).
     - A probe that hits a missing lower interface stays unknown (`dependency_gap`).
   - The threshold is a measured cost model per section (bytes of the family read vs.
     instance count × targeted read time), recorded as data next to the card rules (local `cards.py`),
     not a constant in code.
4. **Skip what cannot apply.** The card rules (local `cards.py`, not yet on `main`)
   already exclude sections per card type
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
