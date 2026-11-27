# Changelog

## 1.1.0 (unreleased)

Completes targeted gathering for the ONT/access families. No schema changes to
`gathered`, write states, or whole-family reads: without `config` a read does
exactly what 1.0.0 does, and write states are unchanged. The only addition is
the `read_outcomes` return value on targeted reads.

### Read outcomes (`read_outcomes`)

- Every targeted read (`state: gathered` with `config` naming instances) of the
  ONT/access families now reports `read_outcomes`: one sanitized outcome per
  addressed instance naming the config section, the selector (composite
  identities joined by `/`), the command axis (`ok`, `rejected`, `failed`) and
  the instance-existence axis (`present`, `confirmed_absent`, `unknown`), plus
  the resource-level parse axis (`failed`, `unverified`). Outcomes are stable
  enums — raw device text is never recorded, and the failure message of a
  failed targeted read names only the resource, the selectors and the error
  class.
- A named instance the device rejects (`invalid token`) is missing from
  `gathered` like an absent one; the module warns, naming the rejected
  selectors, and `read_outcomes` keeps its existence `unknown`.
- Absence and rejection are recognized only on device message lines, not in
  configuration text (a description reading "instance does not exist" no
  longer marks a present instance absent). "The interface index cannot be
  calculated" is a missing dependency (`dependency_gap: interface-index`,
  existence `unknown`), not a confirmed absence; write states still drop
  such a reply, as before.
- `confirmed_absent` is the only outcome consumers may act on: it is the
  device's explicit "instance does not exist" signal about that instance.
  `unknown` (a header-only reply, an invalid-token rejection, a missing
  dependency, or a failed read) is never treated as absence — keep, do not
  remove, configuration for `unknown` instances.
- An explicit targeted request is never served partially or silently widened:
  a request that cannot be read in full (a named instance without an identity)
  fails before any command is sent, and a failed read fails the module
  carrying the sanitized outcomes.
- The logic is central (`facts_base.get_scoped_config` /
  `get_targeted_config`, attached once in `IsamResourceModule.result`); there
  is no per-family outcome code. Whole reads, write states and `isam_facts`
  carry no `read_outcomes`, as before.

### Whole-node reads

- Two instance lists have no single-instance read on the firmware
  (`interface_alarms`; the `isam_vlan_global` priority-regen profiles, which
  answer "invalid token" when addressed individually). For them a targeted
  request reads the whole node once — the only read the device exposes — and
  reports each named instance from the parsed catalog: `present` when the
  catalog lists it, `unknown` when it does not. Catalog absence is never
  `confirmed_absent` (the parser's catalog completeness is unverified, and an
  unrecognized reply line would make a configured instance vanish from the
  catalog); only the device's own node-absence signal confirms absence.
  `gathered` stays the full catalog, unfiltered — the documented exception to
  the scoped-read contract.
- The per-resource read scope is machine-readable in `TARGETED_READ_SCOPE`
  (`whole_node` for these two families, `instance` for the rest), derived from
  the read commands the facts classes send; a test pins it against the facts
  classes that call the whole-node read path, in both directions.
- A reply the family parser cannot process is classified before the module
  fails: parse axis `failed`, every requested instance `unknown`.

### Module interfaces and documentation

- Documentation matches the argspec of the ONT/access modules: `isam_ntp_onts`
  documented options it does not have; `isam_pon_interfaces` and
  `isam_ani_onts` options were undocumented. The standard resource RETURN
  values (`before`, `after`, `commands`, `rendered`, `gathered`, `parsed`)
  carry a generated, argspec-checked doc block in every module.
- `isam_bridges` moves to the shared resource base: targeted `gathered` reads
  return `read_outcomes` (a missing bridge port is `confirmed_absent`), and
  `running_config` with an action state renders an offline preview, so
  `config` and `running_config` are no longer mutually exclusive. Its
  documentation matches the argspec (`rendered`/`parsed` states, the
  `insert-mirror-vlan` and `filtervlanandpbit` choices; device defaults are no
  longer documented as option defaults).

## 1.0.0 (unreleased)

Major-version preparation, not a published release. Schema changes are
intentional. This section lists the ONT/access families of that line.

### ONT and access resource coverage

- New resources `isam_l2uni_onts` (UNI performance monitor incl.
  `pm-collect-ext`, TC-layer thresholds) and `isam_uni_onts` (UNI TC layer),
  keyed by `uni_idx`; defaults are not reported; removal resets to the default.
- New resources for small global settings: `isam_pon_global` (burst-burst and
  ranging mode) and `isam_trouble_shooting_pon` (statistics interfaces and
  thresholds, targeted by name).
- `isam_equipment` models more sub-regions: `diagnostics_sfp`,
  `protection_elements`, `racks`, `external_link_assigns`,
  `external_link_hosts` (lists, targeted by id) and the `envbox`/`isam`
  settings blocks. Previously dropped (detail-only on the lab device).
- Attribute coverage extended for equipment shelf/slot/applique slots read
  `capab_profile` and `operational_mode`; equipment ONT interface docs include
  previously undocumented options. VLAN priority-regen profiles
  (`isam_vlan_global`) and CFM settings extended where ONT access needs them.
- Detail output: every ONT/access family reads `info configure detail flat`
  without failing (unknown keywords are dropped, never fail the read). Fixed:
  `isam_equipment_onts` (sw-ctrl cfgfiles and `delay_act`, ten interface
  sub-nodes such as `tc_layer`, `ethernet`, `cpu_load`; new `loops` and
  `pm_collects` lists).
- `isam_generic_pon` rebuilt on the attribute table: values are read and
  written as values (a bare node line is the default, not a flag), `deleted`
  touches only named sections and settings, and naming a subsection keeps the
  parent attributes.

### ONT write-path fixes (lab-verified)

- `isam_equipment_onts`: `admin-state` is sent on its own line (the device
  rejects it packed into the ONT creation command). `deleted` admin-downs ONT
  slots as well as ONTs before removing them, removes the removed ONT's
  unnamed slots, and keeps sibling ONTs untouched. `replaced` no longer sends
  `no subslocid` (which does not exist); `WILDCARD` (the device's unset value)
  counts as unset and a set value is kept. A `log-auth-pwd` shown masked no
  longer counts as configured.
- `isam_ethernet_onts` `deleted`: a UNI named by `uni_idx` alone resets the
  UNI, and a UNI named with settings resets only the named settings.
- Whole-entry `equipment_onts` deletion reasserts shutdown even for
  gathered-down interfaces/slots, waits for propagation and verifies each
  targeted detail read before sending any removal. Readiness checks are
  bounded; read errors/timeouts stop the operation. No write is retried, and
  failures report accepted, failed and pending commands with an unknown
  outcome. Check mode neither waits nor sends shutdown/removal commands.
- Targeted `gathered` no longer misses `isam_trouble_shooting_pon` interfaces
  with only default settings: their detail read prints nothing either; the
  instance exists when that read does not fail with "instance does not exist".

## 0.3.14 — A slice of π, without the breaking crust

Patch release based on 0.3.13. Existing module names, option names, types,
choices and aliases are preserved. New resources, root-config-tree support and
incompatible schema corrections remain on the feature branch for a major release.
See [the release audit](docs/release-0.3.14-audit.md) for the boundary and
[the validation matrix](docs/live-test-matrix.md) for evidence limitations.

### Fixes

- Keep libssh transport options after writes and failed connections so reconnects
  do not fail with `Hostname required`. Reset CLI context before `admin` as well
  as `configure` commands.
- Scope explicit deletion to named sections/instances in equipment, xDSL profiles,
  QoS maps, link aggregation, traps, system, xSTP and VLAN-global settings. Named
  field deletion preserves other attributes in interfaces, xDSL lines, Ethernet
  ONTs, equipment ONTs, EFM OAM and link-aggregation ports.
- ONT creation sends `admin-state` separately. Deletion admin-downs slots and
  interfaces before removing them, removes slots first, and handles an omitted
  config correctly. Keep unset `subslocid` and masked authentication passwords;
  recognize Ansible-redacted secrets as placeholders, not usable credentials.
- Bridge partial VLAN merges preserve unnamed attributes. Replacement removes stale
  VLAN membership after switching PVID instead of sending invalid field resets.
  Default-off detail flags remain off; priority flags render as bare keywords and
  TPIDs retain string types and their supported reset form.
- QoS interface deletion keeps scheduler nodes required by downstream queues and
  skips unset `none`/`not-applicable` settings. Profile `none` equals unset on replay.
  QoS profiles use packed dependent parameters, reject immutable type changes,
  remove profiles without trailing resets, and keep mandatory parameters.
- Ethernet-line parsing/rendering handles MAU power, flags, admin state and TCA
  thresholds consistently. Comparison is idempotent, resets use supported forms,
  and set-only attributes are retained. Empty Ethernet resources return lists.
- EFM OAM compares with current configuration, preserves omitted merged settings
  and understands interval defaults. Gathering never generates write commands.
  xDSL boards reset attributes instead of sending invalid `no board` commands;
  unknown board attributes do not make facts fail. Equipment slot type changes
  fail before sending and unplanning sends only `no planned-type`.
- L2CP session updates use the short update form and reject creation-only changes
  before sending. Remove injected device defaults from L2CP, L2CP sessions, VLANs,
  distribution services, IPv6 anti-spoofing and Ethernet TCA requests so partial
  merges do not reset unnamed settings. Facts omit those injected defaults.
- VLAN deletion resets named settings, removes identity/full-entry targets and
  skips absent VLANs. Preserve mandatory mode on replacement; creating a VLAN
  requires mode. Render DHCPv6 identifiers and use double quotes for spaced names.
  Distribution-service deletion removes the service, including bare instances.
- Deduplicate targeted reads, strip wrapped command echoes and recheck default-only
  ANI/NTP/alarm/QoS/trap instances with detail reads before treating them as absent.
  Fix PON-variant deletion crashes and ignore unrelated configuration lines.
- Preserve device defaults during PON/interface replay, avoiding unnecessary PON
  shutdown/restart commands. Fix xDSL-bonding overridden idempotence, multicast
  fast-change resets, system SNTP/syslog parsing and generic-PON section scope.
- CFM SLM/domain requests no longer affect each other's sections. Domain identity
  is its index; immutable name/level changes fail safely. Unchanged SLM, remote-MEP
  and Y.1731 PM settings no longer generate redundant commands.
- LineTest replay does not resend unchanged parameters or interpret Ansible-injected
  unset fields as resets. Supported omission resets remain explicit, trailing-`no`
  forms parse as unset, and removing a session can remove its parameters with it.
- SIP `replaced` preserves unnamed list instances in every existing SIP list;
  only `overridden` removes them. Software-management replacement already had
  this behavior in 0.3.13 and is now pinned by a regression test.
- Render explicit false flags instead of dropping their `no` commands. The existing
  ext-authenticator action requires an explicit operation, validates identifiers,
  sends one operation per transaction and reports partial failure with
  `failed_command` (not Ansible's reserved `failed` boolean), without retrying.

### Upgrade notes

Corrected deletion/reset behavior intentionally changes generated commands. Review
check-mode output before applying changes. The legacy bool/value schemas of generic
PON, SIP, software management and VLAN flags, and the legacy QoS-map `queue`/`profile`
options, are not migrated by this patch. Their schema corrections require the major
release. Historical feature-branch lab tests are not release-specific validation.

## 0.3.13

- Targeted gathering for every resource with instance lists: with `state: gathered`
  and `config`, a resource module reads only the instances named in `config` (one or
  several, by their identity fields) instead of the whole resource; absent instances
  are not returned, other device errors fail. An instance with nothing configured
  answers like an absent one (only a header) and is not returned either. Echoed
  command text is stripped from single-instance replies. Without `config` nothing
  changes.
  `TARGETED_GATHER` in `plugins/module_utils/network/isam/targeted.py`
  (dependency-free) lists every instance list and its identity, including nested lists
  (`system` `syslog.destinations`) and composite identities (`qos_profiles` by
  `profile_type` and `name`). Resources without instance lists (`dhcp_server`,
  `generic_pon`, `l2cp`, ...) are single settings blocks and read completely;
  `isam_security_ext_authenticator` only runs an action and gathers nothing.
- Writes: `merged`/`replaced`/`deleted` compare against only the named instances for
  the resources made of instance lists (`TARGETED_WRITES`: as before, plus `ntp_onts`,
  `ani_onts`, `isam_dhcp_relay`, `isam_arp_relay`, `efm_oam_interface`). All other
  resources keep reading the whole resource for writes.
- Modules that never read the device in the module path now do for `gathered`:
  `isam_efm_oam_interface` (also `merged`/`deleted`), `isam_l2cp`, `isam_l2cp_session`,
  `isam_l2cp_user_port`, `isam_pppoe_client_interface`, `isam_pppoe_client_ppp_profile`,
  `isam_pppoel2_statistics` (their `gathered` always returned nothing).
- Device errors fail with `fail_json` instead of a traceback in the module path of
  EFM OAM, ARP/DHCP relay, CFM, PON variants, linetest, xDSL profiles, dist-service,
  IPv6 anti-spoofing, L2CP and PPPoE modules.
- Parsing fixes (lines that were silently dropped or misread):
  - `isam_interface_alarms`: the unindented one-line-per-alarm output was nested into
    one line; each alarm is now parsed on its own.
  - `isam_alarm`: `custom_profiles` and `hgutr069_custs` are parsed (`visibleN`/
    `audibleN` enable/disable map to bool).
  - `isam_traps`: a `configure trap` header with indented children is parsed;
    attributes are found by indentation relative to their resource line.
  - `isam_linetest`: attributes indented under `ltsession`/`ltparm` lines.
  - `isam_qos_profiles`: flat `configure qos profiles marker d1p` lines.
  - `isam_dist_service`: flat lines with several attributes.
  - `isam_ipv6_antispoofing_slot`: a single-slot block.
- Bug fixes (writes; check the command differences before upgrading playbooks):
  - `isam_alarm`: merged/replaced/overridden/deleted/rendered crashed for every list
    section; rewritten per section with the removal forms of the CLI help. Entries,
    filters and suppressions cannot be removed on the device: their resettable
    attributes are reset (`no severity`, `no status no threshold no window`), the rest
    is left with a warning. Custom profiles and hgutr069 entries are removed
    (`configure alarm no custom-profile|hgutr069-cust <id>`). Log/delta-log send only
    known or changed values.
  - `isam_alarm` parsing: the device's one-line entry form (`entry door severity
    critical service-affecting reporting logging`) was dropped; `no severity` means
    the default (unset), not `indeterminate`; filter/suppression `status` is
    `used`/`not-used` (string, was int); `no threshold`/`no window` read as the CLI
    defaults; suppressions without their temporal filter line keep their identity.
    `entries[].index` and `filters[].alarmid` no longer restrict `choices` (open sets
    that change per release; the device validates); entry `severity` gains `ignore`.
  - `isam_vlan_global` `priority_regen` used a form the device does not know
    (`priority-regen dot1p N regen-dot1p M`). It now models the device form
    `priority-regen <id> profile-name <name> pbit0..pbit7` (identity `id`; argspec
    `dot1p`/`regen_dot1p` replaced by `id`, `profile_name`, `pbit0`-`pbit7`); removal
    `configure vlan no priority-regen <id>`.
  - `isam_l2cp`, `isam_l2cp_session`, `isam_l2cp_user_port`,
    `isam_pppoe_client_interface`, `isam_pppoe_client_ppp_profile`,
    `isam_pppoel2_statistics` never read the device for writes (deleted/overridden did
    nothing, merged always resent). All states read the device now; invalid removal
    forms fixed (`no ppp-profile`, `no interface <port> client-id <id>`,
    `no user-port <port> partition-id <id>`); replaced/overridden change in place
    instead of delete and recreate. PPPoE client interfaces are keyed by port and
    client id. The PPPoE password is never compared (the device hides it).
  - `isam_ipv6_antispoofing_slot`: `bit_len` 64-128 is enforced (argspec `min`/`max`
    are not supported by AnsibleModule).
- Bug fixes (parsing): `isam_xstp` (all options of a line, option-less ports,
  validation), `isam_interface_alarms` (`default_severity` was never parsed), PON
  variants (module path and `isam_facts` share one typed parser),
  `isam_interface_cages` (tuple replies), `isam_cfm` (short y1731pm lines raised).
  `isam_xdsl_profiles` gathers through the normal facts path.
- Documentation: `state` describes targeted gathering with an example in every
  targetable module; full option docs, examples and return values for the modules that
  only had stubs (EFM OAM, ARP/DHCP relay, CFM, PON variants, L2CP, PPPoE, linetest,
  dist-service, IPv6 anti-spoofing).
- Tests: a shared harness (`targeted_harness.py`, cases in `targeted_cases_*.py`)
  checks every instance list: only the named instances, several at once, absence,
  device errors, whole resource without config; a coverage test fails when an
  instance list has no case. Test classes now stop their patchers (25 files stopped
  the mock instead, leaking patches into later tests).

## 0.3.12

- QoS interface facts: parse the flat configuration directly instead of one
  template regex/Jinja pass per field and line. Same facts (verified field by field
  against the template on the full DS-LIN-TEST-01 capture and the fixtures); a full
  family read on a 452-ONT MSAN no longer spends many minutes in the parser
  (lab capture: 48 s -> 0.04 s for 9,982 lines).

## 0.3.11

- Accept full gathered ONT entries as deletion input. Fix interface-port negation,
  QoS nested deletion (never reapply requested queue values), bare NTP ONT creation
  and object deletion, and equipment ONT slot-before-interface removal ordering.
- Create a complete bridge port in one call: bootstrap the requested PVID VLAN,
  assign the PVID, then create service VLANs. Full-entry deletion removes the bridge
  port; partial deletion preserves other ports/VLANs and handles both named port
  attributes and VLANs. Keep structural VLAN/PVID removals out of CLI compaction.
- Accept underscore bridge fact keys as input aliases, correct committed-MAC and
  VLAN max-unicast-MAC spelling mismatches, and normalize keys before merging.
- Never invent `no auto-detect` or downstream queue reset syntax: these fields have
  no standalone removal form in the Nokia reference. Warn and retain them until the
  parent object is removed.
- QoS `oper-weight`, `oper-rate` and queue `oper-weight` are derived by the device
  (live: "instance can not be modified"; `oper-rate` follows the scheduler-node
  profile). They are still parsed, but never rendered (`read_only` parser flag).
- Parse scoped QoS replies that carry non-configuration lines (they produced no
  entries, so deletion rendered nothing on a live device).
- Bridge full-entry deletion is decided by the VLANs: a request naming every VLAN of
  the port removes the port, even when a `detail` read reports extra defaults.
- Do not copy masked equipment ONT passwords or NTP keys. Quote interface customer
  labels when needed, and parse compact multi-attribute NTP ONT replies.
- Safety net for every resource: a parser without a removal form now fails the
  module with a clear message instead of rendering netcommon's `no configure ...`,
  which the ISAM never accepts. `xdsl_lines` `admin-up` gets its documented
  `no admin-up` form (it rendered `no configure xdsl line X admin-up` before).
- Add offline full-entry gather/merge/delete, command round-trip, sibling isolation,
  absent-target and check-mode regressions, plus a synthetic compact NTP fixture.

## 0.3.10

- Fix `isam_equipment` parsing of compact multi-property equipment lines, including
  scoped linecard `flat detail` output. Preserve the existing native resource
  schema, negated `unlock` values, and rendering behavior.
- Accept scoped hierarchical dumps headed by `configure equipment` or a complete
  equipment object path. Both `state: parsed` and `isam_facts` use the corrected
  input normalization. Add sanitized live fixtures and parser, module,
  idempotency and round-trip regressions.

## 0.3.9

- Add lightweight, strict monitoring table filters for unprovisioned ONTs and
  xDSL operational line data. Preserve blank
  fixed-width cells and verify row counts before callers replace metrics.
- Share the status-table parser through a dependency-light utility while retaining
  existing facts import paths. Monitoring filter imports no longer need the ISAM
  resource-module initialization path.
- Document bounded-batch monitoring, explicit connection cleanup and local-only
  publication validation in `docs/monitoring-memory.md`.

## 0.3.8

- Canonicalize the second bridge VLAN alias documented by the device. The
  `vlan-scope` value `network` is described in the device help as an "obsolete
  alternative replaced by l2fwder", so it is normalized to `l2fwder` for module
  input, parsed configuration and rendered commands. `local` is passed through
  unchanged and no caller has to migrate.
  - Rendered commands only ever contain `vlan-scope l2fwder`.
  - A device already configured with `vlan-scope network` compares as
    unchanged instead of triggering a rewrite.

## 0.3.7

- Fix creation of bare bridge VLANs. A requested VLAN without attributes, such
  as a PVID VLAN, must still emit its `configure bridge port <port> vlan-id
  <id>` bootstrap command. The 0.3.6 emptiness check ran after normalization,
  which always stamps addressing keys, so the command was silently dropped.

## 0.3.6

- Consolidate bridge VLAN mapping onto the single canonical `l2fwder_vlan`
  attribute. `network_vlan` is accepted as the obsolete CLI alias and is
  normalized at one entry point, so alias input, legacy device output,
  validation, comparison and rendering all share the same field.
  - Rendered commands always use `l2fwder-vlan`; the module never emits the
    obsolete `network-vlan` form.
  - Supplying both names with different values now fails instead of writing
    two conflicting mappings.
  - The VLAN/PVID ordering guard applies to alias input as well, so
    `network_vlan` cannot bypass the bootstrap requirement.
  - Gathered and parsed `l2fwder_vlan` values are strings, matching the
    resource argspec.
  - Bridge VLAN removal against a device configured with `network-vlan` is
    rendered as `no l2fwder-vlan`, which clears the same setting.

## 0.3.5

- Preserve `network_vlan` as the backwards-compatible alias for
  `l2fwder_vlan`. The CLI guide marks `network-vlan` obsolete-and-replaced,
  and specifies that obsolete-and-replaced parameters remain executable even
  though `info` reports the replacement. Do not reject an alias-only request.

## 0.3.4

- Added the `ont_serials` `isam_facts` operational subset, which reads
  `show equipment ont interface` and returns an MSAN-wide `ont-idx` to `sernum`
  index under `ansible_net_ont_serials`. This is substantially cheaper than
  expanding the whole `info configure equipment ont flat` tree and is
  sufficient for ONT-serial reuse detection and per-PON population counting.
  A device that rejects the command omits the key rather than reporting an
  empty index, so callers can distinguish "unsupported" from "no ONTs".

## 0.3.3

- Allow bridge network VLANs without an l2fwder VLAN.
- Fixed `isam_bridges` rendering `tag`/`l2fwder-vlan`/`vlan-scope`/`qos` as
  separate commands. Live devices require these to be issued together on a
  single `configure bridge port <id> vlan-id <id> ...` command; issuing
  `vlan-scope`/`qos` as separate trailing commands after `tag`+`l2fwder-vlan`
  is rejected with `VLAN MGT error 149: Such configuration mode of VLAN
  port is not permitted`. Confirmed and fixed against a live device.

## 0.3.2

- Treat missing lower interfaces as absent during scoped resource reads.

## 0.3.1

- Fixed scoped QoS interface fact parsing when compact device output includes trailing separator or echo lines.

## 0.3.0

- Made operational facts use explicit `gather_subset` values and `ansible_net_*` output names.
- Restricted `cli_config` to supported text configuration.
- Made external-authenticator an explicit action-only module.
- Corrected LineTest deletion and optional-field `no` handling.
- Corrected DHCPv6 statistics probing and optional facts error handling.
- Added migration and read-only live-validation documentation.
