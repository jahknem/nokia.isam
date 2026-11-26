# Semantic object graph and recursive read coverage

## Authority and scope

`plugins/module_utils/network/isam/topology/` is the collection-owned semantic
layer. It supplements existing metadata rather than copying it:

* `targeted.py`: canonical instance lists, identity fields and scoped-read support.
* Resource argspecs and templates: values, validation, parsing and CLI rendering.
* `facts/facts_base.py`: CLI-family ownership in a full configuration snapshot.
* `config_grammar.py` / `config_tree_metadata.py`: explicit CLI syntax paths.

These are different kinds of structure. A CLI child is not necessarily a physical
child: ONT interfaces and ONT slots are sibling commands, while the slots belong
to the ONT. Profiles are references, not subscriber descendants.

The graph implementation is **read-only and experimental**. It exposes
observed relationships, fresh child enumeration and known instance reads, but
cannot yet certify a complete recursive configuration refresh. NOC's existing
refresh jobs, timestamps and plan-read scheduling are not changed by this work.

## Direct-neighbor catalogs

`catalogs/equipment.py`, `catalogs/access.py` and `catalogs/services.py` declare
direct neighbors and resource-to-object bindings. `export_catalog()` derives
reverse parent links; do not maintain transitive ancestors/descendants or a second
copy of identity fields. Resource identity fields are taken from `TARGETED_GATHER`.

`identity.py` implements explicit identity forms and immediate physical parents.
In particular:

* An LT card has identity `lt:rack/shelf/slot`; a virtual LT retains `vlt:`.
* `nt-a` and `nt-b` do not encode their shelf. Their parent is the device until
  authoritative inventory supplies a more precise relationship. Do not assume 1/1.
* PON, ONT, ONT-slot and UNI addresses have explicit, distinct component counts.
* A bare four-component service port is ambiguous without typed resource evidence.
  Resolve it only against exact object identities already observed, and only when
  exactly one object kind claims that address. xDSL lines, Ethernet ports, bonding
  groups and LAG groups can share one numeric address; when more than one exists,
  the configuration is kept as a single canonical instance linked to each
  candidate via `candidate_owner` (an `ambiguous_owner` gap), never assigned to a
  guessed owner. Bridge-port addresses are the exception: the live-verified stack
  attachment rule (`bridge_owner`) resolves them to the LAG when present,
  otherwise the line.
* `ethernet-line:` can describe an Ethernet termination on a DSL line. It must not
  manufacture a separate Ethernet linecard/port from its spelling.
* Transceiver identities are documented cage positions (`lt:r/s/s`, `nt-a`, `nt-b`,
  `ntio-1/2` × `sfp/xfp/qsfp/cfp/sfp1/sfp2/xfp1/xfp2`). The active-NT alias `nt:`,
  `acu:`, `iont:` and `remote-sfp:` forms have no fixed physical owner here and stay
  gaps. Channel pairs (`chpair:` / four-component NGPON2 addresses) belong to their
  LT slot; channel-group membership is a logical association, not containment.
* VLAN-port identities are `(parent kind, parent identity, vlan)` with unstacked
  (`99`) or stacked (`stacked:100:200`) VLAN suffixes; their physical parent is
  the `bridge_port` at the same address, whose parent is the port object. ATM
  `vpi:vci` and NGPON2 identity variants are not decoded yet and remain explicit
  per-instance gaps.
* Unsupported forms produce `unknown_owner`, never a guessed prefix match.

Graph edges are:

| Edge | Direction | Recursive traversal |
| --- | --- | --- |
| `contains` | Physical parent → child | Follow for the selected subtree |
| `owns` | MSAN → device settings or shared definition | Follow only for an explicit full-MSAN request |
| `configures` | Resource instance → object | Include configuration of selected objects |
| `candidate_owner` | Resource instance → possible owner (unresolved) | Include configuration from any candidate; never walk back to other candidates |
| `references` | Configuration → shared profile | Follow forward, deduplicate and handle cycles |
| `member_of` | Ethernet port → link-aggregation group | Association only; never a descendant edge |

Never traverse a profile's incoming consumers or its physical parent. That would
turn a single-ONT refresh into a device-wide refresh. NVT membership remains a
NOC-owned, cross-device relationship; expand its member PON roots in NOC.

The graph contains identities, not resource bodies: no descriptions, serials or
credential fields are copied into it. Identity/profile names are still private
inventory data. Implied ancestors have `observed: false` unless configuration
actually identifies them. Their existence is not a child-discovery certificate.
Device-global settings use a family read unit, not credential-valued identities:
SNMP community strings and operator identities are not copied into the graph.

## Interfaces

```python
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.graph import build_graph, plan_known_reads

catalog = export_catalog()                         # JSON-compatible, schema_version=1
graph = build_graph(ansible_network_resources, "MSAN")
requirements = plan_known_reads(graph, "pon", "1/1/5/10")
```

Ansible filter equivalents (offline; these never open a device connection):

```yaml
graph: '{{ resources | nokia.isam.isam_topology(inventory_hostname) }}'
requirements: '{{ graph | nokia.isam.isam_topology_read_requirements("pon", "1/1/5/10") }}'
```

The requirement output uses canonical `resource`, `section`, `ids` records from
`TARGETED_GATHER`, not NOC's older scope aliases. It is intentionally marked
`complete: false` and `executable: false`: these are reads of known instances,
not permission to run a refresh or to mark data fresh. Absent optional configuration
also needs an explicit read recipe before it can be confirmed absent.
The `physical_discovery` field reports the actual discovery manifest, distinct
from configuration-read completeness. `section: all` with `ids: []` denotes the
full-family read unit for device settings; it is not manufactured for a scoped
object. Repeated full-family units are deduplicated.

For an existing private facts capture:

```sh
PYTHONPATH=.tox/py312-core219/collections .tox/py312-core219/bin/python \
  tools/topology_report.py facts.json --msan MSAN --graph private-graph.json
```

The summary prints counts only; graph output is created mode 0600 and must not
overwrite an existing artifact. NOC's schema exporter includes the catalog when
the selected collection contains it. Older EEs export no `topology` field: absence
is an unsupported capability, not an invitation to synthesize a model in NOC.

## Fresh child discovery (read-only, experimental)

`topology/discovery.py` and the `isam_topology_discovery` module enumerate the
direct children of one object. Two candidate scoped forms were rejected by
DS-LIN-TEST-01:

* `show equipment ont interface <pon>` → `invalid token` (the command is
  device-wide only; it takes no PON argument).
* `info configure equipment ont slot <ont> flat` → `invalid token` (slot reads
  require a full `ont-slot-idx`, not an ONT index).

The current verified enumeration sources are listed below. Rejection of these
two forms does not prove that no alternative scoped syntax exists on any ISAM
platform/firmware; narrower alternatives still need separate validation.

| Relation | Enumeration command | `read_scope` |
| --- | --- | --- |
| PON → ONT | `show equipment ont interface` | `device` |
| ONT → ONT slot | `info configure equipment ont flat` | `family` |
| ONT slot → UNI | `info configure ethernet ont flat` | `family` |
| Card → PON | `info configure pon interface flat` | `family` |
| Card → xDSL line | `info configure xdsl line flat` | `family` |
| Card → Ethernet port | `info configure ethernet line flat` | `family` |
| Card → cage | `info configure interface cage flat` | `family` |
| MSAN → rack / controller card / applique | `info configure equipment flat` | `family` |
| Rack → shelf / shelf → LT or virtual card | `info configure equipment flat` | `family` |
| Card → bonding-group interface | `info configure interface port flat` | `family` |
| Card → link-aggregation group | `info configure link-agg flat` | `family` |
| Card → channel pair (NGPON2) | `info configure channel-pair interface flat` | `family` |
| Card / applique → transceiver cage | `show equipment transceiver-inventory` | `device` |
| Controller card / NTIO applique → IHUB optical faceplate port (`uplink`) | `show port` | `device` |
| Port → bridge port / bridge port → VLAN port | `show interface stack` | `device` |

The transceiver source is a physical cage inventory: it lists empty cages too
(`cage-empty`), so it enumerates hardware positions, not only inserted optics.
Its table requires the recognized header and a matching
`transceiver-inventory count : N` footer; an identity form the catalog cannot
decode rejects the whole source. The channel-pair adapter is documented-derived
(Command Syntax 68.4). DS-LIN-TEST-01 rejected `info configure channel-pair
interface flat` as unsupported (non-NGPON2 firmware), so channel-pair discovery
is **not** live-verified; on this device a card subtree cannot be certified
complete until a supported source confirms the absence. It needs verification on
an NGPON2-capable device.

The interface-stack source requires its recognized header and matching
`stack count : N` footer. Bridge-port and VLAN-port children are accepted only
when the typed lower interface matches the requested parent and the addresses
agree; a mismatch rejects the source. Bonding groups are leaves (no bridge
ports), and VLAN ports are enumerated under their bridge port, never directly
under the raw port.

The IHUB `show port` source is a separate namespace from `show interface port`.
It exposes repeated whitespace tables, including the two-word port state
`Link Up`. The adapter requires recognized section/header/separator structure
and a terminal delimiter; malformed, duplicate, unknown or mis-parented rows
reject the whole source, even outside the requested parent's scope. There is
**no count footer** in these captures: structural validation plus a successful
transport read is weaker evidence than a separately counted inventory, and
cannot detect every omitted section. In particular, a missing section for the
requested controller/applique is rejected, **not** treated as an empty child
set. Do not describe it as count-verified. The adapter enumerates only evidenced NT/NTIO `sfp`/`xfp`
optical faceplate positions, including admin-down and link-down ports. Known
virtual NT ports, internal LT links and NT `eth`/`AI` entries are validated but
not included in that optical subset. Unknown identity variants fail closed.
The kind name `uplink` does **not** imply a configured network/access role.
IHUB ports and equipment transceiver positions remain distinct graph nodes,
even where their identifier strings coincide.

Discovery reads that whole source once and filters by the parent identity. The
true breadth is recorded in `read_scope` so callers know the read also touched
siblings — relevant for per-MSAN locking and freshness. This is the documented
enumeration method, **not** a hidden widening of a scoped request: the module
never claims a scoped read it did not perform.
Broad sources require **explicit `allow_broad_read: true`** in the module call.
Without that authorization the module returns `unsupported` without issuing
enumeration commands. Ansible may still initialize its transport/session. A scope
label in the result alone is not authorization to read more
configuration than requested. A future orchestrator should batch requests and
deduplicate shared enumeration sources instead of issuing the same whole-source
read per child. Device-wide observations do not automatically become fresh just
because their identities were encountered during a sibling's discovery.

The source-driven adapters live in `SOURCES` (child kind → command/scope/CLI
prefix and permitted parent kinds); `enumerate_children()` validates the exact
parent/child relation before filtering identities. The
catalog’s per-child `discovery` map is derived from the actual adapters
(`ENUMERATION` + `SOURCES`), so the catalog and coverage certificate cannot drift.

**Availability is not verification.** A separate per-child `discovery_evidence`
map records each implemented adapter's provenance: `live_verified` (exercised
read-only on DS-LIN-TEST-01) or `documented` (derived from the CLI reference but
not yet verified on a device). Currently only `card → channel_pair` is
`documented` — the non-NGPON2 lab firmware rejects that source. A new adapter
defaults to `documented` unless explicitly listed as live-verified. `coverage()` surfaces the
required relations resting on documented-only adapters in `documented_only`;
this is an informational caveat, not a block — a fresh successful read is real
evidence regardless of the adapter's prior verification. Consumers must not
equate `implemented` with `verified on a device`.

A successful empty filter is confirmed absence of children for that parent
*within the enumerated source*. An unsupported or failed enumeration is reported
as `unsupported`/`error` and must never be interpreted as an empty child list.
(The first implementation swallowed `invalid token` as empty and reported "0
children, ok" for a populated PON; the fail-closed contract and live verification
caught this. Malformed identities in the source are rejected, not filtered.)
Blank or unexpected replies cannot confirm absence. The ONT table requires its
recognized header and matching `interface count` footer. A flat configuration
source (`info configure ... flat`) must end with the device's terminal
`#-----...` delimiter, which it prints even for an empty family; a reply without
it (cut short, or only comments/echo lines) raises instead of reporting `ok`, so
a truncated reply never yields a partial child list or confirmed absence.

`attach_discovery(graph, results)` attaches fresh evidence; `coverage(graph, kind,
identity)` returns a recursive certificate. A root is `complete` only when every
required direct-neighbor relation in its subtree has a successful fresh result.
The manifest distinguishes `ok`, `failed`, `missing` (adapter exists, not yet
read) and `unimplemented` (no adapter yet — a capability gap). IHUB optical
ports are physical leaves in this catalog: no access-side bridge/VLAN layer is
invented for them. Their configuration now has a read-only whole-source
projection, explicitly `partial`; read planning reports
`configuration_coverage_partial`. Configuration-read completeness is
tracked separately by the caller; this certificate covers physical child
discovery only.
Evidence expires after five minutes by default. `coverage()` accepts a stricter
`collected_since` refresh-job boundary; old, future-dated and timezone-less
records cannot satisfy fresh discovery. Successful enumeration replaces only
that direct-neighbor edge set; failed enumeration preserves the old visible
children but blocks coverage. Detached historical data is not deleted. Successive
discovery batches preserve unrelated evidence, and newly discovered children gain
real `contains` edges before their own relations are assessed.

Live verification on DS-LIN-TEST-01 (read-only): PON `1/1/5/1` → 6 ONTs, PON
`1/1/5/10` → 1 ONT, ONT `1/1/5/1/3` → 1 slot; card `lt:1/1/2` → 16 PONs and 16
cages, card `lt:1/1/3` → 48 xDSL lines, card `lt:1/1/8` → 36 Ethernet ports, slot
`1/1/5/1/3/1` → 1 UNI — each with its true `read_scope`. No device writes were
performed.
The equipment/bonding extension was also verified read-only: 1 rack, 1 shelf,
2 directly attached controller cards, 10 shelf cards, 1 applique, 48 bonding
groups on the DSL card and 36 link-aggregation groups on the Ethernet card.
Rack identities can be established by explicit rack entries or by the enclosing
rack in a shelf address. No assumed rack 1/shelf 1/1 is introduced for NT cards.
The gap-filling extension was verified read-only as well: card `lt:1/1/8` → 36
transceiver cages, card `nt-a` → 4 cages, applique `ntio-1` → 6 cages (device-wide
inventory, 120 rows matching the footer). The bridge-port layer was verified
through the typed interface stack: UNI `1/1/5/1/3/1/1` → 1 bridge port → 5 VLAN
ports; LAG `1/1/8/1` → 1 bridge port → 4 VLAN ports; xDSL line `1/1/3/1` → 1
bridge port (stacking on its `ethernet-line:` EFM facet). The full-device stack
capture (1103 rows) confirmed the attachment rules for all 140 bridge ports and
359 VLAN ports. The channel-pair source was rejected as unsupported on this
firmware and is recorded as such, not as absence.

## Bridge-port layer and address attribution (live-resolved)

A port address is not unique across interface types: `ethernet-line:1/1/8/1`,
`la-group:1/1/8/1`, `bridge-port:1/1/8/1` and `vlan-port:1/1/8/1:99` are separate
interfaces (distinct ifIndexes) sharing one numeric address. The device's
`show interface stack` table makes the layering explicit, and a full-device
capture (1103 rows, matching footer) established the attachment rules:

* Every `vlan-port:X:V` stacks on `bridge-port:X` — same address, always
  (359/359 rows). VLAN ports are children of the bridge port, not of the raw
  port.
* `bridge-port:X` stacks on `la-group:X` when a LAG exists at the address
  (35/35 on the Ethernet card), otherwise on the line's `ethernet-line:` EFM
  facet (96/96 on the DSL cards), and on `uni:` for UNIs (9/9).
* Bonding groups **never** carry bridge ports: all 96 `bonding:` interfaces
  show `no-interface` as their stack lower. They have no VLAN-port descendants.
* `la-group:X` stacks on its member `ethernet-line:X`, corroborating the
  config-derived `member_of` association.

The graph therefore models `port → bridge_port → vlan_port`. A `bridge_port`
identity is `(port kind, port identity)`; the module accepts the encoding
`<port kind>:<port identity>` (e.g. `lag:1/1/8/1`). `bridge_owner()` applies the
verified attachment rule to bare bridge addresses: LAG if present, otherwise the
single line object; ambiguous or unknown addresses stay gaps. Discovery uses the
typed stack table for both port → bridge_port and bridge_port → vlan_port, so
attachment is evidenced by the device, never guessed from the address alone.

Two corrections came from live counterexamples rather than assumption:

* MSTP port config belongs to the **port object**, not the bridge port: xstp
  `1/1/8/6` is configured with a LAG present but no `bridge-port:1/1/8/6`
  interface exists. The documented index ("interface index of the lag") and the
  stack table agree; the `port_layer` decoder resolves it to the LAG.
* A typed `ethernet-line:` name is the physical line's ethernet facet, never an
  aggregate (aggregates have their own `bonding:`/`la-group:` names), so it
  resolves against line objects only.

**Bare QoS names: unresolved ownership, not dropped configuration.** A bare
`qos interface` index at a shared address is genuinely ambiguous. The command
accepts "physical port or la-group" (QoS Commands 21.48) with no typed
`la-group:`/`ethernet-line:` spelling, and the LAG group index intentionally
overlaps its primary port's address (LACP Status 169.3). Read-only investigation
confirmed no command exposes the resolved endpoint:

* `show interface stack` does not list QoS sessions (QoS is not a stack layer).
* `show qos profile-usage …` returns reference counts only.
* `show qos interface-bandwidth`, `show qos statistics queue …` and
  `show [xdsl] config-data-port … qos` all key on the same bare index. On the
  lab, the DSL QoS fact (`cac FD_Default`) matches `show xdsl config-data-port
  1/1/3/1 qos` exactly, and the Ethernet `config-data-port … qos` view is empty
  while the QoS fact is populated — suggestive, but not proof of which object
  owns the session. The bandwidth view equals both a single-member LAG and its
  member, so it does not discriminate.

Rather than guess an owner (which would either miss the configuration in a
scoped refresh or wrongly claim a sibling's), the graph keeps the QoS instance
as a **single canonical configuration object** keyed by its native CLI index and
links it to every plausible owner with `candidate_owner` edges, recording an
`ambiguous_owner` gap that lists the candidates. `plan_known_reads()` includes
that read unit when refreshing **any** candidate (so nothing is missed) and
reports it in `unresolved_ownership`, but never walks back to select the other
candidate objects. This is bounded over-inclusion of one read unit, explicitly
flagged — not a silent widening to the device, and not a completeness claim.

On the lab snapshot this is 132 `ambiguous_owner` instances (96 DSL
line/bonding, 36 Ethernet port/LAG), each with two candidates. Typed QoS names
(`pon:`, `ont:`, `vlan:`, 7-component UNI) still resolve exactly. Note (xDSL
Bonding 35.5): a bonding group takes over the primary line's service and cannot
be created if a service already sits on the secondary line, so for bonded DSL
the service-bearing endpoint may be the bonding group rather than the bare
line; both remain candidates until proven. Definitive ownership needs platform
documentation of the bare-index resolution rule or a controlled write experiment
on the lab; neither is assumed here.

## Configuration scope classification

Not all configuration belongs to a physical descendant subtree.
`catalogs/scopes.py` classifies **every** `TARGETED_GATHER` section into one of
three scopes, exported as `section_scopes`:

| Scope | Meaning | Refresh behavior |
| --- | --- | --- |
| `object_owned` | Instance config owned by a physical object (bound via `BINDINGS`) | Read per descendant in a recursive refresh |
| `device_global` | Device-wide settings, no physical owner (system, security, software, alarms, traps, global QoS maps, VLANs, ...) | Read once for a full-MSAN refresh; a scoped subtree does not claim it |
| `shared_profile` | Named definitions referenced by object config (xDSL/QoS/voice profiles) | Read once, deduplicated; never pull in other consumers |

Classification is not proof that ownership and references are fully modeled.
The current 109 sections comprise 48 object-owned, 48 device-global and 13
shared-profile sections. In particular, QoS profiles remain shared definitions
even though they have a decoder. Per-port QoS thresholds, STP ports, PON
diagnostics, and SFP diagnostics are object-owned, not device-global.

`section_models` separately exports the actual modeling state: decoded object,
device settings, shared definition, or unimplemented binding. All 109 sections
now have a model; `unbound_object_sections` is empty. The former seven pending
sections are bound with documented identity evidence:

* `epon_interfaces.config` → PON (EPON interface index is the PON address,
  Epon Commands 69.2);
* `channel_pair_pm.config` → channel pair on the LT slot (Channel Pair Commands
  68.4);
* `pppoe_client_interface.config`, `pppoel2_statistics.config` → VLAN port
  (PPPoE Commands 32.3 / PPPoEL2STATS 33.2);
* `isam_system_security.slots` → NT card, `nt-a`/`nt-b` only (Security Commands
  16.42);
* `isam_system_security.pae.ports` → user port superset; ONT `voip`/`vuni`/LLId
  and NGPON2 variants remain per-instance gaps;
* `system.sync_if_timing.ssmout_synce` → transceiver cage on `nt-a`/`nt-b`/
  `ntio-1/2` (System Commands 15.35); the active-NT `nt:` alias stays a gap.

A bound section is not a claim that every instance identity decodes: unsupported
identity variants remain explicit `unknown_owner` gaps per instance. Security
debug-USB settings and 802.1X ports must not be treated as global merely
because they share a family with global security settings. SyncE input-reference
definitions, in contrast, belong to the device and may reference a port or be
unbound (`port: none`); they are not physical descendants of a guessed interface.

The graph models device settings with `owns` edges and full-family read units,
and shared definitions with `owns`/`references` edges. Explicit DSL reference
fields link lines/boards to service, spectrum, DPBO, vectoring and VCE profiles,
and PPPoE client interfaces reference their PPP profile; following them never
walks into other subscribers. Link-aggregation membership
uses `member_of`, not `contains`. The catalog also exports `relations`,
`global_resources`, `global_settings` and `typed_references` for consumers.

All sections being classified, or a lab snapshot having zero ownership-mapping
gaps, does **not** make the generalized catalog exhaustive. It explicitly exports
`relationships_exhaustive: false`. Other firmware/platform identities, optional
configuration, and remaining service/profile reference rules still need evidence.
The legacy `unmapped_sections` field lists sections without a dedicated decoder;
use `section_models` to distinguish modeled global/shared ownership from a real
unimplemented object binding.

## No heuristic CLI-tree fallback

The root configuration parser no longer infers node identities, attributes or
subnodes from spelling, repetition, neighboring lines or `no` tokens. Declared
grammar/resource paths are matched directly. Missing paths are retained under
`__unclassified__`; missing attribute syntax is retained in `unparsed` on the
known node. All retained lines still pass through credential redaction first.

`gap_report()` now reports `unparsed` line counts as well as `unclaimed` families
and known-but-unmodelled fields. **No unclaimed families is not the same as no
parser gaps.** Consumers must check all three. Old `source: heuristic` and learned
`+subnode` sources no longer occur. Existing readers must tolerate the additive
`unparsed` field and the new `unclassified` source.

## Live reference and remaining gates

A read-only `info configure flat` capture from DS-LIN-TEST-01 on 2026-11-20 was
parsed once through the existing resource registry. It established observed
relationships across GPON, ONT/UNI, DSL, Ethernet and QoS families. No device writes
were performed. Local raw/facts captures must not be committed. That access-side
capture has no NT uplink interface-port examples. NT cage positions (`nt-a:xfp:N`)
are documented and live-verified as **transceiver inventory** identities. They
are not accepted by the access-side `show interface port`/`stack` commands:

* `show interface port nt-a:xfp:N` and `show interface stack nt-a:xfp:N` return
  `invalid token` (the syntax is not accepted, not merely an absent instance).
* The access-side `configure interface port` (13.2) and `show interface port`
  (126.4) index formats define no NT faceplate-port identity;
  `configure ethernet line` (43.2) is LT-slot `rack/shelf/slot/port` only.
* A successful access-side interface-port capture on production MSAN C (FANT-F +
  FGLT-D) contains pon/ont/uni/vlan-port configuration and no NT port entries.
  production MSAN D has only been checked with `show equipment slot`; that read
  establishes its FANT-F/FGLT-D equipment, not its port configuration.

These are **access-CLI observations, not evidence that configurable NT uplinks
do not exist**. The guide explicitly describes two CLI parsers (ISAM CLI 1.3)
and points to separate IHUB guides. IHUB Commands (chapter 233, pp. 7324–7325)
lists `configure port`, `show port`, `configure lag` and `show lag`. Therefore
access-side interface-port absence cannot establish IHUB port absence. The
read-only `show port` capture on 2026-11-21 confirms the IHUB identities:
DS-LIN-TEST-01 has 14 optical faceplate ports (4 each on `nt-a`/`nt-b`, 6 on
`ntio-1`), while production MSAN C has 8 (4 on each NT). A scoped `show port nt-a:xfp:3`
also succeeds on the lab, reporting an up 10-Gbps Ethernet interface in access
mode with 802.1q encapsulation. `show lag` reports two IHUB LAG IDs on the lab;
these are not the LT `link-agg` groups and no membership/configuration mapping
is inferred yet. Optical-port discovery is now implemented through `show port`.
Do not assume access-side bridge/VLAN-port relationships apply to IHUB services,
or conflate equipment inventory and interface configuration solely because
their identifier strings may coincide.

A bounded read-only legacy comparison on production MSAN A (NetBox platform
`r5-1-02`, NANT-E with NDPS-C/NDLT-F/FGLT-B) also accepts `show port` and
produces 14 optical positions through the same strict parser (4 per NT,
6 on NTIO-1). This is evidence for that observed format, not a guarantee across
all firmware/card variants. No NGPON2/ONT voice identity evidence was obtained
from these reads; checking three devices is not a fleet-wide absence claim.

This also exposes a configuration-coverage boundary: binding **109/109 targeted
sections does not cover the whole MSAN CLI**. IHUB port, LAG and service
configuration now has separate read-only schemas and explicit whole-family
bindings, outside `TARGETED_GATHER` (no scoped CLI promise). See
[IHUB configuration](ihub-configuration.md). These domains are exported as
`partial_configuration_domains` with their real `configuration_read_capabilities`.
IHUB routing, QoS, system/security and other domains remain in
`unmodeled_configuration_domains`. Full-MSAN plans surface those gaps, and
IHUB object plans carry `configuration_coverage_partial`. Physical discovery
or a fully parsed lab projection never closes these configuration gaps.

A second read-only reference attempt on production MSAN C timed out after 180 seconds on
the full snapshot. Smaller reads successfully gathered the two named controller
slots, but the Ethernet-family read failed in the existing parser with
`'NoneType' object has no attribute 'leaves'`. This is a failed read, not proof of
absence. It prevented the remaining reference capture from completing. No
controller-port coverage was established by that attempt and the production
timeout was not extended. The later IHUB reads above independently establish
optical-port inventory, not configuration completeness.

Before enabling recursive refresh:

1. Discovery adapters: PON → ONT, ONT → slots, slot → UNIs, card →
   PON/xDSL/Ethernet/cage, rack/shelf/card, applique, bonding-group,
   link-aggregation, card/applique → transceiver inventory, and port →
   bridge-port → VLAN-port (typed interface stack) are implemented and
   live-verified (whole-source enumeration with honest `read_scope`; see above).
   Controller/NTIO optical-port discovery is live-verified through IHUB `show
   port`; port/LAG/service configuration now has partial, read-only whole-source
   models. Internal IHUB-port discovery and complete configuration/service refresh
   relationships remain open. Still needed:
   NGPON2 channel-pair
   verification on a capable device. A targeted parent configuration read is not
   enough, and where no scoped command exists the whole-source method must be
   recorded as such.
2. Account for all required resource families, optional/absent settings and shared
   references. All 109 sections now have an ownership model, but unsupported
   identity variants (ATM vpi:vci, NGPON2, ONT voip/vuni/LLId, active-NT alias)
   remain explicit per-instance gaps. These identity forms are **firmware-
   dependent**: the reference guide's changelog records EPON prefixes
   (`epon:`/`eont:`/`ellid:`/`euni:`) removed as obsolete in favour of `pon:leg`
   on this NT generation. Do not add decoders for variant forms from documentation
   alone without confirming the target firmware still uses them; model them
   evidence-first like the other adapters. Bare QoS names at shared line/aggregate
   addresses are kept as candidate-owned configuration (132 `ambiguous_owner`
   instances on the lab snapshot): readable from any candidate, flagged
   unresolved, never guessed. Expand remaining profile/service reference rules
   and platform applicability with evidence; existing DSL/QoS references are not
   proof of exhaustive dependency coverage.
3. Return discovery/result manifests with scope, collection/runtime revision,
   successful enumeration, read failures, confirmed absences and timestamps.
   Parser warnings must remain partial outcomes; never count them as success.
4. Compare the recursive scoped projection against a full device snapshot for each
   supported board type, including planned cards, empty scopes and new children.
5. Teach NOC to persist coverage, use the oldest relevant successful observation,
   and retire disappeared descendants only after successful scoped enumeration.
   Preserve per-MSAN exclusion, cross-MSAN concurrency and explicit-refresh behavior.
6. Build and pin the new collection EE and update AWX projects before enabling the
   new API/UI behavior. Do not label a generated catalog as deployed capability.

A scoped recursive *configuration* request must never silently widen to a
device-wide read. Whole-source child enumeration must be explicitly authorized,
and its true breadth recorded in `read_scope` (never disguised as scoped). An
unsupported or unauthorized discovery boundary must be shown as incomplete.
