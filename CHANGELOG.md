# Changelog

## 0.3.14

- Root config tree: `isam_facts` subset `config_tree` reads `info configure flat` once
  and parses the whole configuration into a nested, lossless tree
  (`ansible_net_config_tree`), keyed by CLI path with attributes at the leaves. Every
  line is kept, including parts no resource family models yet. `config_tree_detail:
  true` reads `info configure detail flat` instead (also unset defaults; several times
  larger) to survey the full configurable surface. Secret attribute values (SNMP
  community, passwords) are redacted by name; device-masked (`plain:`) and hashed
  (`encrypted:`) values are kept.
- The path/attribute split uses a compiled CLI grammar
  (`plugins/module_utils/network/isam/config_grammar.py`, generated from the rm_models
  syntaxes by `tools/compile_config_grammar.py`; rm_models itself is not shipped).
  Nodes without a grammar entry are kept losslessly at branch granularity and flagged.
- `config_tree.gap_report` shows what the root contains that the families do not model:
  unclaimed nodes (no family), nodes without a grammar, and unmodelled attributes.
- New resource `isam_system_security` (slice 1): operators, profiles (permissions as a
  dict), SNMP communities/views/managers/notify-profiles, RADIUS auth-servers/policies/
  auth-super-user/dyn-auth-clients. Targeted gathering by name; secret values (operator
  passwords, RADIUS secrets, SNMP community strings) registered for redaction. Derived
  from real device output (this tree is not in rm_models). Remaining: pae, peripheral-mgnt
  and the small settings blocks.
- `isam_equipment` models more sub-regions: `diagnostics_sfp`, `protection_elements`,
  `racks`, `external_link_assigns`, `external_link_hosts` (lists, targeted by id) and the
  `envbox`/`isam` settings blocks. Previously dropped (detail-only on the lab device).
- New resource `isam_qos_tca`: per-port/queue QoS threshold crossing alarms
  (`configure qos tca <port> queue <n>`), composite identity (name, queue), targeted
  gathering, merged/replaced/overridden/deleted/rendered/parsed/gathered. Queues reset
  in place (not individually removable). Previously unmodelled (964 detail lines).
- Bug fixes: `isam_ethernet_line` no longer crashes on a port-type line without a `mau`
  block, and a `mau` block keeps all its attributes (`type` and `power`). `isam_qos_maps`
  models `up-ctrl-pkt`/`dn-ctrl-pkt` in the real device form (`<protocol> [dscp] [pbit]
  [tc]`, was queue/profile) and renders `dscp-map-dot1p ... dot1p-value` (was `dot1p`).

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
