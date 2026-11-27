# IHUB configuration: read-only, evidence-gated families

## Verified source boundary

The ISAM CLI reference describes separate access and IHUB parsers. The local
non-detail/detail flat root captures contain no `configure port`, `configure
lag`, or `configure service` entries. A bounded `info configure` read on
DS-LIN-TEST-01 on 2026-11-21 includes their hierarchical sections instead.

Do not use `info configure port` as a port read: on the lab the access parser
expands it to **port-protection**. A scoped-looking `info configure port
nt-a:xfp:3` fails, and `info configure lag` is rejected. These are not empty
families, nor evidence of a supported scoped read. No configure/context-changing
commands are used by the new modules.

## Public modules and schemas

* `isam_ihub_ports`: canonical list keyed by `id`, including observed description,
  shutdown and Ethernet speed/LLDP fields. Its source is device-wide
  `info configure`, filtered to the explicitly labelled Port Configuration section.
* `isam_ihub_lags`: canonical list keyed by `id`, including observed member ports,
  description, shutdown and LACP mode/administrative key. Same root read, LAG section.
* `isam_ihub_services`: `customers` keyed by `id`, and `services` keyed by
  `(service_type, id)`. Includes observed VPLS/V-VPLS VLAN identity, IES interfaces,
  addresses, customer references, STP and SAP configuration. Its verified source
  is family-wide `info configure service`; it can also parse the labelled service
  section of a supplied hierarchical root offline.

Only `gathered` and `parsed` are implemented. No write/render states are exposed.
The argspecs are exported with their actual state choices. These opt-in modules
do not alter `isam_facts` implicit all-resource reads or silently mix hierarchical
sources into the existing shared-flat pipeline.

`config` is an optional output selection using canonical identities: it accepts
only the identity keys (`id`; services `service_type` and `id`). It does not
generate targeted CLI commands. All instance selections require
`allow_broad_read: true`, as do the device-wide port/LAG sources even without
selections. Explicit whole-family service gathering needs no redundant flag.
`source` records the command, true read scope and read completion timestamp.
The modules never change the device, so check mode reads exactly like a normal
run. `parsed` is offline and, unlike `gathered`, does not set `ansible_facts`.

## Parsing and coverage

The parser validates native indentation, matching `exit` closures, quoting,
family markers and final delimiter. It rejects wrong-family/flat/blank/truncated
sources instead of returning a certified empty result. Unknown options, blocks
and service types produce `coverage.unparsed` and `coverage.complete: false`.
Gap records include modeled locations/keywords, not potentially sensitive unknown
values. A complete projection means the observed source-family syntax was
understood, **not** exhaustive platform support or device configuration completeness.

Lab evidence: 27 configured IHUB port nodes, 2 LAG nodes, 1 customer, 45 services
(44 V-VPLS, 1 IES), and 451 SAPs. The standalone and root service projections
match. Counts are observations, not hardcoded parser limits. Raw captures remain
private; public regression fixtures are synthetic.

One live sequence returned a root response without the terminal delimiter on
its second resource read; the module rejected it. Two subsequent bounded raw
root reads were complete and parsed all three families, and live service-family
gathering succeeded. A separate live LAG-module read also returned two LAGs with
`changed: false`. This does not establish the cause of the intermittent
response issue or fleet-wide transport reliability. There is no automatic retry
or partial-success fallback that could turn a malformed source into absence.

## Semantic catalog

These resources have explicit whole-family bindings outside `TARGETED_GATHER`;
they must not advertise a single-instance CLI capability that does not exist.
`configuration_read_capabilities` exports the true source and
`instance_selection: whole_source_filter_only`. Known read plans use deduplicated
`section: all` units and remain non-executable.

Optical IHUB ports map to `uplink` objects, internal LT/NT links to `ihub_port`,
and virtual `nt:vp/mc` ports to device-owned `ihub_virtual_port`. IHUB LAGs,
services and customers are device-owned logical objects. LAG port membership is
`member_of`, not containment. Service read units reference their customer and
SAP endpoint objects (including IHUB LAGs); consumer/sibling traversal is not
introduced. Unsupported endpoint/encapsulation forms remain mapping gaps.
The observed `:0` IHUB SAP encapsulation token is accepted for endpoint references;
it does not manufacture an access VLAN with ID zero.

The three domains now have **partial** configuration models rather than no
model. `configuration_coverage_partial` remains explicit: additional syntax,
platforms, inverse attachment/refresh semantics and read completeness need work.
Internal-port discovery is still a capability gap. IHUB routing, QoS, system/
security and other domains remain unmodeled and block whole-MSAN completeness.
The existing flat root tree is not silently widened or represented as complete.

No NOC/EE/AWX rollout or device writes are part of this increment.
