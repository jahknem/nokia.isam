# Changelog

## 1.1.0 (unreleased)

Completes targeted gathering for the ONT/access families. No schema changes to
`gathered` or whole-family reads: without `config` a read does exactly what
1.0.0 does. Additions: the `read_outcomes` return value on targeted reads, and
for `isam_bridges` the offline preview with `running_config` (see "Module
interfaces and documentation").

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
- `confirmed_absent` is the only outcome consumers may act on: the device's
  explicit "instance does not exist" about that instance, or the header only
  in both `flat` and `flat detail` (docs/targeted-read-contract.md).
  `unknown` (an invalid-token rejection, a missing dependency, another
  instance's line, a section whose reads never show it, or a failed read) is
  never treated as absence — keep, do not remove, configuration for `unknown`
  instances.
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

- `config` and `running_config` are no longer mutually exclusive in any
  resource module that offers the offline preview (an action state with
  `running_config` renders against it), including the grammar-table families,
  `isam_ethernet_line` and the QoS families; their API baseline constraints
  changed accordingly.
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
- `isam_system_security`: option descriptions written from the CLI guide; its docs
  match the argspec (enforced by the contract tests once the module is registered).
- `isam_system_security`: `overridden` fails, before anything is sent, instead of
  removing a RADIUS auth server a kept RADIUS policy references, or a RADIUS policy
  the auth-super-user operator-policy or a kept domain references.
- `isam_security_ext_authenticator`: the undocumented, unused `provider` option is
  removed.

### Review follow-ups

- `isam_software_mngt`: an OSWP slot (1 or 2) is never removed (`no oswp N` is
  not a device form); its resettable attributes (`activate`, `auto-verify`,
  `on-schedule-time`) return to their defaults instead. `admin-state` changes
  only when named; `activate` and `auto-verify enabled` are never sent unless
  named.
- `isam_linetest`: `overridden` fails before any command when it would write a
  parameter to a session it destroys.
- Settings blocks (`isam_pppox_relay_global`, `isam_nat`, `isam_error`,
  `isam_cwmp_plt`, `isam_pon_global`): `deleted` with config resets only the
  named attributes.
- `isam_xdsl_lines`, `isam_ethernet_line`: the docs warn that `overridden` and an
  identity-only `deleted` send `no admin-up` (the line goes down).

### Topology refresh

- New module `isam_read`: several isolated reads on one MSAN in one task (whole
  families, named instances of one instance list, or operational subsets), each with
  its own outcome: `returned_ids`, `confirmed_absent_ids`, `unverified_ids`, and
  `dependency_gaps` for unverified instances whose read named a missing object they
  depend on. Credentials are removed (argspec `no_log` fields and known secret names);
  warnings are reduced to stable categories.
- `topology.refresh`: the complete refresh of an ONT, PON or card in rounds (context,
  discovery, configuration reads, referenced definitions) and its evaluation: every
  applicable (object, section) is present, confirmed absent or a named gap.
  - An entry the device creates with its object is present with defaults only when
    the object exists, and absent when it is proven absent.
  - A dependency gap ("lower-interface does not exist") is absent when the object it
    hangs on, or an ancestor, is proven absent; otherwise a labelled gap.
  - Card-type rules (`topology/cards.py`): child kinds per card type, sections that
    do not apply, entries created with the card; from a read-only fleet survey.
- The topology catalog is derived from one relations file per family
  (`relations/`): identity, object kind, `creates`, `created_with`, `references`,
  `requires`, observability, with their evidence. `export_catalog()` is unchanged
  for every existing key and adds `creates`, `created_with` and `requires`.
- Write order and dependency graph (`topology/write_order.py`, `dependencies.py`) with
  the filters `isam_write_steps` and `isam_dependency_graph`.
- Behaviour change in owner resolution: a bare QoS index belongs to the LAG where one
  exists (QOS MGT error 216, lab 2026-11-25) and is never a bonding group (the device
  accepts only the bare form for QoS); before, both were reported as ambiguous.
- Test: every `created_with` section is reset, never removed, by its module in
  `deleted` and `overridden`.

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
- `isam_ani_onts`: a changed threshold of an existing entry is sent (the
  compare only looked at `tca_thresh`). The entry exists as long as its ONT,
  so `deleted`, `overridden` and `tca_thresh: false` reset its thresholds
  instead of sending `no tca-thresh`, which left it in place and made
  `deleted` never idempotent. The upper threshold must not be below the lower
  one (GPON MGT error 238).
- `isam_ntp_onts`: the NTP ONT entry also exists as long as its ONT, and
  `configure ntp no ont` is accepted without any effect; `deleted` and
  `overridden` reset the set attributes instead.
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

### QoS: new resources

- New resource `isam_qos_tca`: per-port/queue QoS threshold crossing alarms
  (`configure qos tca <port> queue <n>`), composite identity (`name`, `queue`), targeted
  gathering, all seven states. Queues always exist on the device and reset in place:
  `deleted`/`overridden` reset attributes (named attributes only themselves), and
  `tca_enable=false` equals the device default when comparing.
- New resource `isam_qos_global`: the bare `configure qos` settings (`general`),
  per line card `qos global <lt>` (`line_cards`, targeted by name), the
  DSL/NNI/protocol ctrl-pkt policers, `pbit_scheduling` and `upstr_prot_dsl`. Reading
  `general` needs `info configure qos flat` (the node has no own `info` path), so it is
  only read when in scope; per-node reads replace absent nodes with empty settings.
- `isam_qos_global` and `isam_qos_maps` `overridden` act only on the named sections
  (an empty dict or list names a section): overriding `general` no longer resets line
  cards, policers or pbit scheduling nor removes ctrl-pkt policers, and overriding
  `tc_map_dot1p` no longer removes the dscp and ctrl-pkt entries. Within a named list
  section, entries not given are still removed or reset.

### QoS: profile and map rework

- `isam_qos_profiles` is rebuilt: every parameter of the eleven profile types parses
  (flat and `detail` forms incl. `no X` defaults), dependent parameters go in one packed
  command per profile (the device rejects `excess-info-rate` before `type`), changing a
  shaper's type fails before anything is sent, mandatory parameters are kept instead of
  invalid `no` resets (warned), profile deletion emits no trailing field resets, and
  `use-dei` renders as a bare flag. Options keep their historical CLI spelling; the
  snake_case spelling of every CLI-named option is accepted as an alias, and all options
  are documented. The packed command names each parameter once (a request omitting a
  mandatory parameter sent the changed one twice), and the documentation states that
  `overridden`/`deleted` remove profiles without checking whether they are in use.
- Breaking: `isam_qos_maps` models `up-ctrl-pkt`/`dn-ctrl-pkt` in the real device form
  (`<protocol> [dscp <n>] [pbit <n>] [tc <n>]`; was `queue`/`profile`), requires the
  fields the device needs to set an entry, and renders `dscp-map-dot1p ... dot1p-value`
  (was `dot1p`). `deleted` removes only the named entries, not whole map families.
  `replaced`/`overridden` reset the ctrl-pkt parameters an entry omits with the inline
  `no dscp`/`no pbit`/`no tc` form (they never converged before), and device defaults
  (`dscp -1`, `pbit 7`, `tc -1`) count as unset when comparing.

### QoS: interfaces

- `isam_qos_interfaces` runs on `IsamResourceModule` (offline action states, command
  safety). Detail placeholders (`none`, `not-applicable`) no longer become removal
  commands: `not-applicable` is never sent (a real target value is kept), unset
  `none`/`not-applicable` top-level and queue settings render no resets, and an explicit
  `none` still clears a configured profile. `deleted`, `replaced` and `overridden`
  keep the `scheduler_node` an interface with downstream queues requires (warned; the
  device rejects its removal, QOS MGT error 52). Facts read targeted (`state:
  gathered` with `config` reads only the named interfaces); the module documents the
  QoS-before-bridge prerequisites (QOS MGT error 41, VLAN MGT error 277).

### Grammar-table families: major-release integration

- VLAN facts use snake_case keys (CLI spellings remain option aliases);
  documented value options in VLANs, SIP and software management replace
  legacy boolean approximations. Preserve the 0.3.14 safety regressions under
  the migrated schemas, including escaping embedded quotes in VLAN names.

### Shared infrastructure, state semantics and safety

- The compiled CLI grammar ships
  (`plugins/module_utils/network/isam/config_grammar.py`, generated from the
  rm_models syntaxes by `tools/compile_config_grammar.py`; rm_models itself is
  not shipped. Run the tool after CLI model changes). It records, per CLI
  node path, the attribute keywords with their value/negatable/required
  forms; the root config tree consumes it in its own PR.
- Table-driven `replaced` preserves unnamed list instances (SIP VSPs and
  software OSWPs); only `overridden` removes them. Named-instance omitted
  attributes still reset where the device supports it. LineTest `overridden`
  now permits removing a session together with its parameters, while
  rejecting unsupported parameter-only deletion on retained sessions.
- Attribute-table parsing retains known clauses after unknown leading
  attributes on explicit leaf nodes; a synthetic forward-compatibility fixture
  (`voice_sip/unknown-leading-attribute`) and parser regressions pin the case.
- Fixed configured LineTest replay: `replaced` no longer resends an unchanged
  parameter, and Ansible-injected unset options no longer cause spurious
  resets in merged/rendered. Replaced/overridden reset supported omitted
  options only when currently configured.
- Focused LineTest parser tests cover hierarchical/scoped output, duplicate
  identities, every declared session/parameter field and reset round-trips.
  Fixed trailing-`no` resets (`group-opt no`, `busy-overwrite no`,
  `force-measure no`) parsing as the string `"no"` instead of unset. No
  LineTest action is invoked by parsing or rendering.
- `isam_vlans` rebuilt as the collection's reference module: one attribute
  table (`VLAN_ATTRS`) generates the parsers, drives the facts and holds the
  device defaults; every state goes through the template and `compare()`.
  **Facts now use snake_case keys** (`protocol_filter`, `new_broadcast`, ...);
  the CLI spellings (`protocol-filter`, ...) stay accepted as option aliases.
  Fixed on the way (verified on the device with VLANs 3990/3991):
  `rendered`/`merged` dropped `dhcpv6-itf-id` and `dhcpv6-remote-id`; names
  with spaces were sent in single quotes (invalid token; now double quotes, as
  the device prints them); `replaced` sent `no mode` (mode is mandatory, no
  removal form); a new VLAN without `mode` now fails before sending. Parse ->
  render of all 47 lab VLANs reproduces the device's lines exactly (fixture
  `vlans/r6.2.04m-all-vlans`). Attribute kinds taken from the CLI guide and
  probed on the device: 16 options modelled as on/off flags are value options
  (the bare keyword is "not complete"): `dhcp_opt82_nni`, `dhcp_opt82_uplink`,
  `relay_id_dhcp`, the `*_linerate`, `*_l2_encaps`, `l2_encaps1`,
  `*_vlanaware`, `drly_srv_usr_side`, `dhcpv6_relay_id`, `dhcpv6_trst_port` --
  they are now strings with the guide's choices and defaults (setting any of
  them never worked before). Commands are packed like the device's two printed
  lines; a bare flag at the end of a command was sent separately before.
- `isam_voice_sip` rebuilt on one grammar table (`TABLE` in `rm_templates/voice_sip.py`) that
  generates the argspec and documentation and drives the facts and config.
  ~70 options modelled as on/off flags are values per the CLI guide (e.g. vsp
  `ta4`, `tinfo`, `digit_send_mode`, register/redundancy timers and modes,
  statistics `stats_5min_config`/`cdr_config`, cas `version_nbr`/
  `outg_from_no_cgpn`); a set value was read as `true` and `true` rendered a
  bare, incomplete keyword. Device defaults count as unset; `deleted` naming
  an instance removes it, naming attributes resets only those with a removal
  form; creating a vsp/cas profile requires its mandatory values. **Breaking
  schema fixes:** `system.session_timer` (the node name, never settable) is
  now the `enable` flag; `redundancy_cmd.geo_fail_over` (a value of
  `fail_x_type`, not a field) is removed and `start_time`/`end_time` are ints.
  Parse -> render -> parse of the lab capture round-trips; merged/replaced of
  the gathered facts send nothing.
- `isam_software_mngt` rebuilt on one grammar table (`TABLE` in `rm_templates/software_mngt.py`)
  generating the argspec and documentation and driving facts and config (the
  hand-written facts parser and the fragile ordered-regex template are gone).
  oswp `activate`/`auto-verify` (enums), `on-schedule-time` (datetime) and
  database `activate` are values, not bool flags (a set value was read as
  `true`); added the missing oswp `download_set`/`autofetch` and database
  `activate`. Packed attributes share a line; `version`/`url`/`admin-state`
  and the scalar `sw-replacement-mode` keep their own command forms.
  `on-schedule-time` and `backup`/`backupv6` are kept as raw string values.
- Setting a value back to its device default now resets it (`no <kw>`) instead
  of being a silent no-op, and is a no-op when the device is already at
  default (`isam_voice_sip`, `isam_software_mngt`). Previously the default was
  stripped from the request, so e.g. turning `auto-verify` back to `disabled`
  did nothing.
- `isam_software_mngt` and `isam_voice_sip` use the shared attribute-table
  core (`attribute_table.py`) and config base `TableResourceModule`, replacing
  their per-family copies of the table parser, default stripping, diff/render
  rules, argspec generator and state handling (they had already drifted:
  `software_mngt` did not quote `#` values, `voice_sip` lacked the option-name
  fix). One parsing rule for every table: a line belongs to a node only when
  it is bare or starts with one of its keywords; a `#` starting a word outside
  quotes begins a comment. A shared test checks that each table, its argspec
  and its documentation agree.
- `isam_linetest` migrated onto `IsamResourceModule`, so it shares the
  standard facts gathering, check-mode write path and before/after result. It
  now creates a requested session that does not exist (`session-cmd create`);
  its other device rules are unchanged and pinned by tests across every state:
  sessions are destroyed with `session-cmd destroy` (never rendered as
  configuration), parameters have no delete command (delete their session),
  and `group-opt`/`busy-overwrite`/`force-measure` reset with a trailing `no`.
  Read-only on the lab ISAM (no LineTest configured): gathered returns the
  empty structure, rendered emits declarative commands only.
- Device defaults out of the argspecs (they were injected into every request):
  `isam_vlans` merged renaming a VLAN reset `protocol-filter`,
  `new-broadcast` and `drly-srv-usr-side`; `deleted` naming a setting deleted
  the whole VLAN and sent `no id` for VLANs that do not exist (verified on the
  device with VLAN 3990). `isam_dist_service` merged reset the service type to
  apipe; `deleted` left the service (now `configure no dist-service <id>`,
  verified), the bare service line was not read. `isam_l2cp` and
  `isam_ipv6_antispoofing_slot` merged reset an unnamed setting;
  `isam_ipv6_antispoofing_slot` replaced reset unlisted slots. Facts of these
  families no longer report device defaults (`isam_dist_service` still reports
  its `service_type`).

### Lab validation

- `isam_l2cp_session`: changing an existing session always failed (the full
  creation command was re-sent; the device only accepts
  `session <index> alive-timer <value>`), and `merged` overwrote unnamed
  attributes with argspec defaults (one of them wrong,
  `dslam-name 00 : 00 : 00`). Defaults are now the device's, kept in the
  module; creation sends the given attributes, changes use the short form, and
  attributes the device only accepts at creation fail the module before any
  change.

### Regression coverage and reconciliation fixes

- Fixture audit: the synthetic L2CP fixture's always-true `len(parsed) >= 0`
  assertion is replaced with a concrete identity/value check
  (`partition_type: fixed-assigned`), with the fixture data corrected against
  the CLI guide.

### New module isam_system_security

- New resource `isam_system_security` (slice 1): operators, profiles (permissions as a
  dict), SNMP communities/views/managers/notify-profiles, RADIUS auth-servers/policies/
  auth-super-user/dyn-auth-clients. Targeted gathering by name; secret values (operator
  passwords, RADIUS secrets, SNMP community strings) registered for redaction. Derived
  from real device output (this tree is not in rm_models).
- Slice 2: SNMP notify-views, domains, SSH (server profile, access, SFTP users), file
  transfer (servers), TACACS, LI, password policy, default profile, slots,
  peripheral-management MAC filters, PAE (802.1X) port access and per-port
  authenticator / ext-authenticator, and the general settings line. Slice-1 fixes: SNMP
  communities are keyed by name and host-address, views by name and subtree; removals use
  the device form (`snmp no view X subtree S`); `deleted` with config only touches the
  named sections; values with spaces are quoted; replaced/overridden reset omitted
  attributes. All 679 security lines of the lab detail capture parse.
- RADIUS policies preserve multiple servers in `servers[]` (indexed by `index`); legacy
  flat server fields map to server 1. Dynamic authorization clients expose `admin_down`.
- Global value options fixed (`isam_system_security`): password `mixed_case`, ssh access
  `debug`/`debugkernel`, filetransfer `tftp_rollovr` (int) — options modelled as on/off
  flags that take values per the CLI guide; before, a set value was read as `true`.
- Targeted reads: `ssh.sftp_users` uses the ssh node (the device rejects
  `ssh sftp-user <name>` with `invalid token`), keeps only the named users' lines and
  reports each user present or unknown (never confirmed absent).
- `overridden` acts only on the list types and settings blocks named in `config`; an
  unnamed type is left alone (overriding every type would remove all operators, SNMP
  access and RADIUS servers of a request that only tunes, e.g., the password policy).

### Secret handling (isam_system_security)

- Fixed redacted gathered-facts replay in `system_security`: device masks and Ansible's
  `VALUE_SPECIFIED_IN_NO_LOG_PARAMETER` preserve existing secrets rather than generating
  placeholder credential commands. Masked credentials are omitted from unrelated updates
  and rejected when creating/rendering entries; concrete credential updates still work.
  Redacted identities are never guessed: merged/replaced leave those entries unchanged
  with a warning, while destructive states, rendering and targeted gathering reject them.
  Embedded redacted notify-profile communities preserve the existing SNMP version only.
- The SNMP community inside a notify profile's `snmp-version v1:<community>` is
  registered as a no_log value even when a targeted read does not read the community
  list, so it is masked in module output.
- `isam_system_security` SNMP views: the device stores well-known numeric OIDs under
  their MIB names (`1.3.6.1.2.1` -> `mib_2`, ...); merged re-sent them every run. The
  15 verified names are compared as equal to their OIDs.

### isam_security_ext_authenticator on the shared action base

- `isam_security_ext_authenticator` now runs on the shared `IsamActionModule` base
  (check mode, one command per transaction, responses and failure propagation).
  **Bug fix:** with `clear_statistics: false` it sent the bare resource path
  `admin security ext-authenticator <port>` (which only navigates the admin hierarchy,
  CLI guide global commands) and reported `changed: true`; it now rejects an entry
  without the `clear-statistics` operation.
- The unreachable ext-authenticator facts/template (and its synthetic
  command-as-facts fixture) are removed; ext-authenticator remains action-only and
  gathers nothing.

### New xDSL resources

- `isam_xdsl_inm`: impulse noise sensors, near-end and far-end lists keyed by
  name, targeted gathering per sensor.
- `isam_xdsl_onts`: the xDSL ONT interface, keyed by `ont_idx`, targeted
  gathering per ONT.
- `isam_xdsl_system`: the xDSL system settings line (`auto-port-reset`).

### xDSL boards, profiles and lines

- Breaking: `isam_xdsl_boards` `vp_boards[].vp_link`/`lt_expect` (only the
  last link survived) became `vp_boards[].vp_links[]` with `link_id` and
  `lt_expect`. New board fields: vplt/vce/vect-class settings, `vect_fallback`
  and `auto_port_reset`. `deleted`/`overridden` reset the board's attributes
  instead of sending `configure xdsl no board`, which the device refuses;
  `deleted` without config now removes all boards instead of silently doing
  nothing.
- `isam_xdsl_profiles` models the service/spectrum/DPBO/vectoring/VCE profile
  attributes and indexed PSD/PBO sub-nodes; detail defaults no longer land in
  `commands`, false flags are idempotent, and `deleted` with config touches
  only the named profiles (it used to delete every profile of the other
  types).
- `isam_xdsl_lines`: xDSL line TCA thresholds modelled; targeted gathering by
  line name.

### Ethernet line rebuild

- `isam_ethernet_line` rebuilt in the collection style: `power down` was read
  as `up`, TCA settings were never rendered, MAU flags rendered with
  underscores, `admin-up` was not read, and removal forms like
  `configure ethernet no line <l> port-type` do not exist. One parser per
  attribute, packed lines split on read and packed on write; `overridden`
  resets unnamed lines, `deleted` resets named settings, an empty device
  returns `[]`, and a port-type line without a `mau` block no longer crashes
  the parser.

### New operational action modules

- Tier-1 operational action modules on `IsamActionModule` (one-shot
  counter/MAC operations, guide-verified syntax, an explicit operation is
  required, identifiers validated): `isam_ethernet_statistics`
  (`admin ethernet statistics <index> clear-stats`),
  `isam_dhcp_relay_port_stats` (`admin dhcp-relay port-stats <vlan-port>
  clear-statistics`) and `isam_bridge_learned_mac` (`admin bridge
  learned-unicast-mac <vlan-port> unicast-mac-address <mac> delete`, with
  MAC-address validation). Check-mode verified on the lab ISAM; the
  operations themselves are not executed without a per-action decision.

### New global settings resources

- New resources for small global settings: `isam_nat`, `isam_error`,
  `isam_cwmp_plt` and `isam_pppox_relay_global`, each targeted by its single
  settings node. Reading and writing `isam_nat` requires the CWMP platform to
  be enabled on the device.

### Targeted gathering consistency (Ethernet and xDSL lines)

- A `gathered` read of an Ethernet line uses the same compact `flat` form as
  the complete read, not `flat detail` (which prints every default and parsed
  into a different configuration). Write states keep the detail form.
- For `gathered` reads, a node the firmware does not know (`invalid token`)
  is skipped, not raised; `read_outcomes` reports the instance `rejected` with
  existence `unknown` (never absent). Write states still surface the error.

### New read-only modules (topology and IHUB)

- `isam_topology_discovery`: enumerates the direct children of one object in
  the semantic topology graph, read-only (check mode reads like a normal run).
  Where the ISAM has no scoped "list children" command, the module reads the
  smallest whole source containing the children, records its breadth in
  `read_scope`, and requires explicit `allow_broad_read` consent for a
  device/family-wide source. A failed or unsupported enumeration is reported
  as such (error class and exception type, never raw exception text) and is
  never an empty child list.
- `isam_ihub_ports`, `isam_ihub_lags`, `isam_ihub_services`: read-only IHUB
  configuration families from the evidenced hierarchical CLI sources
  (`info configure`, `info configure service`), which the flat root source
  omits. The device-wide port and LAG sources require explicit
  `allow_broad_read=true`; services have a verified family source. The
  modules never write: they accept only identity keys in their `config`
  selection, check mode reads like a normal run, and `parsed` no longer
  sets `ansible_facts`.
- `plugins/filter/topology.py`: playbook access to the versioned topology
  catalog and the known-read plan (`docs/resource-topology.md`,
  `docs/ihub-configuration.md`, `docs/targeted-gathering.md`,
  `tools/topology_report.py`).

### Discovery and IHUB parsing fixes

- Topology discovery: a flat configuration source (`info configure ... flat`)
  must end with the device's terminal `#-----` delimiter. A truncated or
  comment/echo-only reply was reported `ok` with a partial or empty child list;
  it now fails instead of confirming children or their absence.
- IHUB configuration: lines are tokenized like the device (`"…"` or a blank-free
  run), not by POSIX shell rules: an unquoted apostrophe (`description Bob's`)
  no longer fails the whole read, and backslashes are kept.

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
