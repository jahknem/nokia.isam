# Changelog

## 0.3.14

- Live write verification on the lab ISAM (approved scope: traffic-free test objects;
  every change read back, reverted and read back; before/after captures identical).
  Verified set and reset/delete forms: QoS shaper profiles (create, two-rate EIR,
  `no excess-info-rate`, delete), alarm custom profiles, xDSL service profiles, SNMP
  views, CFM SLM timer, PPPoX relay global session, mcast-control and IGMP package names.
  Fixed:
  - Connection plugin: after any write (edit_config resets the session) and after a
    retried connect, the next connect over libssh failed with "Hostname required" -- the
    rebuilt transport had lost its options. The transport is now closed and kept.
  - `deleted` naming one instance touched other sections or profiles (all present in
    0.3.13): `isam_xdsl_profiles` deleted every spectrum/DPBO/vect/VCE profile when one
    service profile was named; `isam_equipment` unplanned the shelf and every slot;
    `isam_xstp` ran `xstp general no enable-stp`; `isam_qos_maps` deleted every map
    entry (and crashed for tc/dscp maps named by identity); `isam_link_agg`,
    `isam_traps` and `isam_system` (SNTP servers, sync-if-timing references) reset
    other sections. With config, only the named sections and entries are touched; a
    regression test runs this for every targetable list over the lab capture.
  - `isam_qos_profiles` sends one packed command per profile (dependent parameters such
    as a shaper's EIR and type were rejected as separate commands) and fails early when
    asked to change an existing shaper's type (the device refuses).
  - `isam_system_security` SNMP views: the device stores well-known numeric OIDs under
    their MIB names (`1.3.6.1.2.1` -> `mib_2`, ...); merged re-sent them every run. The
    15 verified names are compared as equal to their OIDs.
  - The `state` documentation of the affected modules describes the `deleted` scope,
    the packed QoS profile commands and the default handling. Identical targeted reads
    (several identities sharing one node) are sent once.
  - Not verifiable in scope: `isam_nat` needs the CWMP platform enabled ("CWMP platform
    is disabled"). Test values outside documented ranges were rejected by the device as
    expected (alarm mnemonic letters only, CFM SLM 10-100 s, NAT aging 60-240 s).
- Live write verification on an empty PON of the lab ISAM (PON interface and port,
  test VLANs, a test ONT with slot/UNI/ANI/NTP/PM settings; record in
  `docs/live-validation-2026-11-18.md`). Fixed:
  - `isam_equipment_onts`: `admin-state` was packed into the command that creates an
    ONT; the device rejects it there (`invalid token`). It is sent on its own line.
    `deleted` admin-downs ONT slots as well as ONTs before removing them (the device
    refuses: "Not in admin down state to delete"). `replaced` sent `no subslocid`,
    which does not exist; `WILDCARD` (the device's unset value) counts as unset and a
    set value is kept. A `log-auth-pwd` shown masked no longer counts as configured.
  - `isam_qos_interfaces` `deleted`: settings showing `none`/`not-applicable` are not
    reset (the device rejected `no bc-scheduler-node` on an ONT UNI).
  - `isam_bridges` documents that a VLAN on an ONT UNI bridge port needs an
    upstream-queue bandwidth profile (VLAN MGT error 277).
- Live write verification on linecard 6 (planned, no board): a full customer ONT built
  from the modules' `parsed` output of another ONT, read back equal in all fields,
  changed, and deleted module by module. Fixed (all present in 0.3.13):
  - `isam_bridges` `replaced`/`overridden` reset a no longer wanted VLAN attribute by
    attribute (`vlan-id N no tag no l2fwder-vlan ...`); the device refuses that for
    service VLANs (VLAN MGT error 81). The VLAN is removed with `no vlan-id N`, after a
    new PVID is set.
  - `isam_qos_interfaces` `deleted` sent `no scheduler-node` on interfaces with
    downstream queues (every ONT UNI); the device refuses it (QOS MGT error 52) and the
    queues cannot be removed. The scheduler node is kept, with a warning. `deleted`
    without config now also skips `none`/`not-applicable` values.
  - `isam_ethernet_onts` `deleted`: a UNI named by `uni_idx` alone was not reset at
    all, and a UNI named with settings had every setting reset. Now the identity resets
    the UNI and named settings reset only themselves.
  - `isam_ethernet_onts` and `isam_ethernet_line` returned `{}` instead of `[]` from an
    empty device. (`isam_bridges` returns `[]` for its dict config; unchanged, pinned
    by tests.)
  - `isam_qos_interfaces` documents that upstream-queue parameters cannot change while
    a bridge VLAN uses the queue (QOS MGT error 41).
- Live write tests of the remaining families on linecard 6 and traffic-free test objects
  (status per family: `docs/live-test-matrix.md`). Fixed (all present in 0.3.13):
  - `isam_l2cp_session`: changing an existing session always failed (the full creation
    command was re-sent; the device only accepts `session <index> alive-timer <value>`),
    and `merged` overwrote unnamed attributes with argspec defaults (one of them wrong,
    `dslam-name 00 : 00 : 00`). Defaults are now the device's, kept in the module;
    creation sends the given attributes, changes use the short form, and attributes the
    device only accepts at creation fail the module before any change.
  - Targeted `gathered` missed instances with only default settings: `isam_traps`
    managers (now read flat with the detail re-check) and `isam_trouble_shooting_pon`
    interfaces (their detail read prints nothing either; the instance exists when that
    read does not fail with "instance does not exist").
  - `isam_qos_interfaces`: a profile set to `none` (shown by the device as unset) was
    re-sent by every `merged` run.
  - `isam_interface_cages` documents that R6.2.04m has no cage `description`/`apply_qos`.
- Live write tests on linecard 6 replanned as xDSL (NDLT-F) and Ethernet (NELT-B) board.
  Offline scenario fixtures pin every step whose prior state was captured
  (`tests/fixtures/live_scenarios/`, `test_live_write_scenario`). Fixed (all present in
  0.3.13):
  - `isam_ethernet_line` rebuilt in the collection style (`docs/development-style.md`):
    `power down` was read as `up`, TCA settings were never rendered (broken parser
    templates), MAU flags rendered with underscores, `admin-up` was not read, removal
    forms like `configure ethernet no line <l> port-type` do not exist, TCA argspec
    defaults overwrote unnamed thresholds. Now one parser per attribute, packed lines
    split on read and packed on write; `overridden` resets unnamed lines, `deleted`
    resets named settings (port-type and MAU type/power have no `no` form and are kept).
  - `isam_efm_oam_interface` never compared with the device: every `merged` re-sent the
    port and reset unnamed intervals; `overridden` left other ports. It compares now,
    knows the device defaults (keep-alive 300 s, response 5 s) and sends only changes.
  - `isam_xdsl_boards` `deleted`/`overridden` sent `configure xdsl no board`, which does
    not exist; the board's attributes are reset (only the named ones with config).
  - `isam_equipment`: unplanning a slot also sent `no unlock`/`no capab-profile`, refused
    after `no planned-type`; it sends only `no planned-type`. Changing the type of a
    planned slot fails early (the device needs it unplanned first).
  - `isam_link_agg` removed a group's default member port (refused, error 22).
  - `isam_dhcp_relay` documented the `vlan-port:` form, which the device refuses for
    port statistics; `isam_dhcp_relay`, `isam_arp_relay` and `isam_pppoel2_statistics`
    document that R6.2.04m shows the setting in no read.
- `docs/development-style.md`: the collection's module style: netcommon layout, one
  state contract for every family, templates chosen by grammar (explicit parsers,
  small factories, or the shared settings block), scenario and contract tests.
- `IsamResourceModule` (`module_utils/network/isam/resource_module.py`) is the explicit
  base of every config class. It replaces the monkey-patching of netcommon's
  `ResourceModule` (removal forms, command compaction) and adds: an explicit `False` is
  rendered as its `no` form in `rendered` (dropped before for `isam_equipment`,
  `isam_interfaces`, `isam_xdsl_lines`; fixed locally in `isam_xstp`).
- Named-field deletion, found by a sweep over the lab capture and verified on the device
  (linecard 6 as GPON, xDSL and Ethernet board): `deleted` naming one attribute reset the
  whole instance in `isam_interfaces`, `isam_link_agg` ports, `isam_xdsl_inm`,
  `isam_xdsl_lines`, `isam_xstp` ports, `isam_ethernet_line` MAUs and
  `isam_efm_oam_interface`; `isam_equipment_onts` removed the whole ONT (or slot) when
  one of its settings was named; `isam_vlan_global` deleting a priority-regen entry also
  reset broadcast-frames and tpid. All now use the shared `deleted_targets` /
  `covers_entry` rules. `isam_dhcp_server` sent `no lease-time` twice in merged.
- Device defaults out of the argspecs (they were injected into every request):
  `isam_vlans` merged renaming a VLAN reset `protocol-filter`, `new-broadcast` and
  `drly-srv-usr-side`; `deleted` naming a setting deleted the whole VLAN and sent
  `no id` for VLANs that do not exist (verified on the device with VLAN 3990).
  `isam_dist_service` merged reset the service type to apipe; `deleted` left the service
  (now `configure no dist-service <id>`, verified), the bare service line was not read.
  `isam_l2cp` and `isam_ipv6_antispoofing_slot` merged reset an unnamed setting;
  `isam_ipv6_antispoofing_slot` replaced reset unlisted slots. Facts of these families
  no longer report device defaults.
- Live verification on the lab ISAM (read-only / check mode). Every resource module's
  live `gathered` matches the parse of a fresh capture; 57 targeted reads and 102
  check-mode merged/replaced/overridden runs with the gathered facts as config. Fixed:
  - `replaced` on `isam_pon_interfaces` with config from a plain read "reset" every
    default printed by the `flat detail` comparison read and wrapped it in
    `admin-state down`/`up` (all ONTs of the PON offline). `isam_interfaces` likewise
    re-sent `no admin-up`/`no link-updown-trap`. Values equal to the device default
    (default-off flags: false) count as unset; an explicit default in `merged` is still
    sent when the device differs. Present since before 0.3.13.
  - `isam_ethernet_line` `overridden` re-sent every wanted value (never idempotent);
    `isam_xdsl_bonding` `overridden` reset a wanted `group_assembly_time`.
  - Targeted reads: the terminal wraps the echoed command mid-word for long commands
    (`... 1/1/2/1/100 fl` / `at`); the fragments made an empty reply look non-empty.
    The echo is now removed by prefix match. Instances without configured attributes
    answer a single read with only a header, although the whole read lists them; for
    `ani_onts`, `ntp_onts`, `alarm` custom profiles and `qos_maps` ctrl-pkt entries an
    empty reply is re-checked with `flat detail` and the bare instance returned (as the
    whole read does). Before, `merged` re-created such instances.
  - `isam_system_security` `ssh.sftp_users`: the device rejects `ssh sftp-user <name>`
    (`invalid token`); targeted reads use the ssh node and keep the named users.
  - Secrets: the SNMP community inside a notify profile's `snmp-version v1:<community>`
    was printed in clear text by a targeted read (the community list, whose no_log
    registration masked it, was not read) and stayed unmasked in the root tree. It is
    registered as a no_log value, and the tree masks it (and, as a safety net, any
    secret seen behind a secret keyword wherever it reappears).
  - Known, unchanged: targeted reads of `bridges` and `pon_interfaces` use `flat detail`
    and report default values the whole read omits (same as 0.3.13; NOC consumes
    targeted bridge facts). Writes treat them as unset.
- `state: deleted` against configured devices (new regression test runs every
  resource module's `deleted` without config over a real capture):
  - `isam_epon_interfaces`, `isam_channel_pair_pm`, `isam_ngpon2_channel_groups`:
    deleted/replaced/overridden crashed (`AttributeError`) whenever an instance
    existed. Their parser also turned unrelated `configure` lines into instances
    (visible with `state: parsed` on a full running config); only their own lines
    are read now.
  - `isam_xdsl_boards`: deleted without config silently did nothing (same truthy
    empty-facts cause as `isam_equipment_onts`); it now removes all boards.
  - `isam_mcast_general`: deleted and overridden reset `fast_change` (previously
    only replaced).
  - `isam_interface_cages`: deleted/overridden failed on `operational_mode`, which
    has no CLI removal form; the mode is now kept with a warning.
  - `isam_system` deleted without config remains a no-op by design (it resets only
    the named sections).
- Capture tests locate the lab captures through `ISAM_ROOT_CAPTURES` (default: the
  sibling `pon-migration-planner/.local`) instead of an absolute home path.
- Backlog closeout: `equipment_onts` with `state: deleted` and no config now deletes
  the whole resource instead of silently doing nothing. Interfaces are shut down,
  slots removed before interfaces, and loop/PM settings are not reset after their
  ONT is removed. Explicitly named sections remain scoped.
- Root-tree nesting uses resource-backed CLI metadata for missing security,
  timing, syslog, xDSL profile, trap-manager and multicast nodes. Lowercase names,
  composite SNMP identities and indexed RADIUS/PSD entries no longer depend on
  heuristics or line order. `source: resource` identifies this metadata.
  The password-policy node is no longer mistaken for a password attribute.
- Gap reporting recognises intentional option-name differences and schema-less
  permission dictionaries without suppressing unknown attributes elsewhere.
  Both lab captures now have zero unclaimed lines and zero reported attribute
  gaps (regression-tested). This measures capture coverage, not device verification
  of inferred write syntax. Diagnostic output still needs review before sharing
  because unknown CLI syntax can be misinterpreted by the heuristic fallback.
- Root config tree: `isam_facts` subset `config_tree` reads `info configure flat` once
  and parses the whole configuration into a nested, lossless tree
  (`ansible_net_config_tree`), keyed by CLI path with attributes at the leaves. Every
  line is kept, including parts no resource family models yet. `config_tree_detail:
  true` reads `info configure detail flat` instead (also unset defaults; several times
  larger) to survey the full configurable surface. Secret attribute values (SNMP
  community, passwords) are redacted by name. Hashed (`encrypted:`) credentials are
  stripped before structuring, including at unknown paths and in stored CLI lines;
  only actual device-masked placeholders (`plain:******`) are kept.
- The path/attribute split uses a compiled CLI grammar
  (`plugins/module_utils/network/isam/config_grammar.py`, generated from the rm_models
  syntaxes by `tools/compile_config_grammar.py`; rm_models itself is not shipped).
  Nodes without a grammar entry use heuristic nesting and learned sub-nodes.
- `config_tree.gap_report` shows what the root contains that the families do not model:
  unclaimed nodes (no family) and unmodelled attributes per family. CLI-spelled option
  names and aliases count as modelled; value-like tokens are counted, not printed.
- Attribute cleanup: `xdsl_profiles` models service/spectrum/DPBO/vectoring/VCE
  attributes and indexed PSD/PBO sub-nodes; detail defaults no longer land in
  `commands`, and false flags are idempotent. Existing raw `commands` remain accepted.
- `qos_profiles` accepts snake_case aliases without changing existing fact keys;
  mandatory parameters are not reset with invalid `no` commands, profile deletion
  emits no trailing field resets, and `use-dei` renders as a bare flag. Full option
  documentation added.
- `isam_system_security`: RADIUS policies preserve multiple servers in `servers[]`
  (indexed by `index`); legacy flat server fields map to server 1. Dynamic authorization
  clients expose `admin_down`.
- `bridges`: partial `merged` VLAN entries merge by VLAN identity instead of resetting
  omitted fields. Correct default-off flags, bare `prior-*` rendering, TPID string
  parsing/reset, port TPID sub-nodes, and additional port/VLAN-port attributes.
  `vlans` reads detail `no new-broadcast` as the inherited default.
- `system`: additional ID, syslog, SNTP and global settings; fixed syslog severity and
  SNTP enable parsing. Security reads belong exclusively to `isam_system_security`;
  the legacy `system.security` option remains write-only and is deprecated.
- Attribute coverage extended for equipment shelf/slot/applique, Ethernet ONT PM/CFM
  sub-nodes, xDSL line TCA thresholds, bonding boards/groups and xSTP settings.
  Bonding groups/boards support targeted gathering; deleting a named group preserves
  unrelated settings and boards. Equipment ONT interface docs now include previously
  undocumented options. CFM SLM, VLAN broadcast priority and multicast settings extended.
- Detail output: every family reads `info configure detail flat` without failing (unknown
  keywords are dropped, never fail the read); a test runs all families over a real
  configured and detail capture. Fixed: `isam_equipment_onts` (sw-ctrl cfgfiles and
  `delay_act`, ten interface sub-nodes such as `tc_layer`, `ethernet`, `cpu_load`; new
  `loops` and `pm_collects` lists), `isam_xdsl_boards` (vplt/vce/vect-class fields,
  `vect_fallback`, `auto_port_reset`).
- Breaking: `isam_xdsl_boards` `vp_boards[].vp_link`/`lt_expect` (only the last link
  survived) became `vp_boards[].vp_links[]` with `link_id` and `lt_expect`.
- New resource `isam_qos_global`: the global QoS line, per line card `qos global <lt>`
  (`line_cards`, targeted by name), DSL/NNI/protocol ctrl-pkt policers, pbit scheduling,
  upstream DSL protection. Reading `general` needs `info configure qos flat` (no own node);
  it is only read when requested.
- New resources for small global settings: `isam_nat`, `isam_error`, `isam_cwmp_plt`,
  `isam_pon_global`, `isam_pppox_relay_global`, `isam_trouble_shooting_pon` (statistics
  interfaces and thresholds, targeted by name). `isam_mcast_general` gains `capacity`.
- Root config tree: the grammar compiler reads the help text and repairs terminal line
  wraps (160 nodes, all with a usable syntax; broken names such as `xg-pm-collec` fixed),
  handles create/delete alternations; nodes without a grammar nest by learned sub-nodes
  instead of staying at branch level; secrets are masked before any structuring. Leaves are
  `{attrs, lines, node, source}` (`raw_tokens` removed). `gap_report` is content-based per
  family argspec; `tools/gap_report.py <capture>` prints names and counts only.
- `isam_system_security` slice 2: SNMP notify-views, domains, SSH (server profile,
  access, SFTP users), file transfer (servers), TACACS, LI, password policy, default
  profile, slots, peripheral-management MAC filters, PAE (802.1X) port access and per-port
  authenticator / ext-authenticator, and the general settings line. Slice-1 fixes: SNMP
  communities are keyed by name and host-address, views by name and subtree; removals use
  the device form (`snmp no view X subtree S`); `deleted` with config only touches the
  named sections; values with spaces are quoted; replaced/overridden reset omitted
  attributes. All 679 security lines of the lab detail capture parse.
- `isam_system` models `sync-if-timing` (revert, wait-time, thresholds, BITS, bits-bind,
  force-reference, ref-order, ssm, synce, ssmout-synce).
- `isam_igmp` / `isam_mcast_control` / `isam_multicast`: `packages` (targeted by index)
  and the `system` settings incl. `cdr-type`. Packages cannot be removed, only reset;
  all-default packages are not reported.
- New resources `isam_l2uni_onts` (UNI performance monitor incl. `pm-collect-ext`, TC-layer
  thresholds) and `isam_uni_onts` (UNI TC layer), keyed by `uni_idx`; defaults are not
  reported; removal resets to the default.
- New resources `isam_xdsl_inm` (impulse noise sensors near-end / far-end),
  `isam_xdsl_onts` (xDSL ONT interface, keyed by `ont_idx`) and `isam_xdsl_system`
  (`auto-port-reset`).
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
