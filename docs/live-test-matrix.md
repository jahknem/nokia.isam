# Live test matrix

What has been verified on the sanitized lab ISAM (R6.2.04m) and what remains.
Update this file with every live run; tests listed as verified are not repeated unless
the module's write path changes. Details and device behaviour:
`live-validation-2026-11-18.md`.

## 1.0 preparation versus published 0.3.14

The entries below record historical feature-branch evidence. They are retained
for provenance, not represented as fresh verification of a 1.0 artifact. No device
writes are part of this major-version integration, no new global operations are
authorized, and NOC is unchanged. The 1.0 tag and release remain unpublished.

The published 0.3.14 patch was isolated from 0.3.13; its exact boundary is retained
in [the patch audit](release-0.3.14-audit.md). Its CI on `2807ce22` passed 1,376
tests, 58 skipped and 2 subtests, plus lint/typecheck/docs and the devcontainer
build. Its archive/checksum were downloaded and verified after publication.
Those patch results must not be counted as 1.0 validation.

### Major-preparation gates (2026-11-19)

- Full unit tree, including connection plugins and offline private-capture replay:
  **2,864 passed, 14 skipped, 247 subtests passed**. `ISAM_ROOT_CAPTURES` selects
  the private capture directory explicitly; captures and logs stay outside the
  distributable collection. This run performs no live device operations.
- All 54 migration/inherited-safety regressions passed, including real Ansible
  action-failure serialization, identifier newline rejection, scoped replacement,
  special-character VLAN names and the documented breaking-schema examples.
- Lint, type checking and all module/connection documentation checks passed.
- The 1.0 candidate archive passed version, content-scope and per-file checksum
  checks. An isolated install validated documentation for all 72 modules and real
  check-mode entrypoints for generic PON, SIP, VLANs and Ethernet statistics.
- Tox now isolates collection/dependency layouts per environment, and release
  branches run CI without requiring a tag or publication.

### Live-apply follow-up (offline, 2026-11-19)

The [handover regression follow-up](live-apply-regressions-2026-11-19.md) covers
standalone slot admin-state, reasserted/bounded-readback shutdown before deletion,
severity/QoS placeholders, and caller-controlled QoS-before-bridge ordering.
The Core 2.19.12 direct-execution lane covers literal/templated single-element
merged lists and flat/block/wrapped-echo device replies in run/check mode. It does
not reproduce the original `config.interfaces.flat` failure. No new live writes
or device cleanup were performed; the new shutdown policy still needs separately
approved live validation. Do not count older evidence below as validation of it.

Final offline gate: Core 2.19.12 and 2.21.6 each passed **2,914 tests, 14 skipped,
247 subtests**, including private-capture replay and connection plugins. All 50
new cases also passed in the existing EE's Python 3.11/Core 2.19.12 runtime with
changed plugin source mounted read-only and networking disabled. Lint/typecheck/
docs passed; the local archive passed 610 file checksums/source equality and
isolated module documentation checks. No EE was rebuilt or deployed by this
follow-up.

## Reads (all families, 2026-11-18)

Every resource module's live `gathered` equals `parsed` of a fresh capture; the root
tree claims every capture line; 55 of 57 targeted reads equal the whole read (the two
differences are the known `flat detail` reads of `bridges` and `pon_interfaces`).
102 check-mode runs with the gathered facts as config produced no commands.

Later fixes, verified live: targeted reads of instances with only default settings
(`traps` managers, `trouble_shooting_pon` interfaces).

## Contract checks (2026-11-18)

Named-field deletion (`deleted` naming one attribute resets only that attribute) and an
explicit `false` in `rendered` were swept over every family with the lab capture
(`test_deleted_regressions.py`). The named-field deletion fixes were verified on the
device on card 6: `isam_interfaces`, `isam_equipment_onts` (GPON); `isam_xdsl_lines`,
`isam_xdsl_inm`, `isam_efm_oam_interface` (xDSL board); `isam_ethernet_line`,
`isam_link_agg`, `isam_xstp` (Ethernet board). `isam_vlan_global` and
`isam_dhcp_server` (global settings) are unit-tested only.

## Writes

Legend: **verified** = set, read back, idempotent, change and/or reset, delete, read
back empty, on the device. Targets: card 6 = linecard 6 (planned, no board; test ONT
`1/1/6/1/1` with bridge port), PON 7/16 = empty PON `1/1/7/16`, test object = a
traffic-free object with its own name (`zztest`, `192.0.2.1`, unused ids).

| Family | Status | Target, verified forms | Open |
|---|---|---|---|
| `isam_alarm` | verified (part) | custom profile create/delete | entries, filters, log (global) |
| `isam_ani_onts` | verified | card 6 / PON 7/16: entry create/delete | – |
| `isam_bridges` | verified | card 6: port with 4 VLANs, PVID, L2 forwarders; partial merged; replaced removing/adding a VLAN; deleted | `ageing_time` (global) |
| `isam_cfm` | verified (part) | SLM timer set/reset | domain create refused: VMAC HostID prerequisite; not enabled for testing |
| `isam_equipment` | verified (part) | card 6: slot lock/unlock, replaced restore, unplan (`no planned-type` only) and plan as NDLT-F/NELT-B/FGLT-B | diagnostics SFP, protection elements |
| `isam_equipment_onts` | verified | card 6: interface, slot, loops, sw-ctrl (test id 200), admin down/up, delete with shutdown | `pm_collects` (XGS ONTs only), sw-ctrl config files (need a real file) |
| `isam_ethernet_onts` | verified | card 6: UNI settings, phy/l2/cfm sub-nodes, identity and named-field deleted | – |
| `isam_igmp` | verified (part) | package names set/reset | other settings (global) |
| `isam_interface_alarms` | verified | test object `epon` (no EPON hardware): severity set/restore | – |
| `isam_efm_oam_interface` | verified | card 6 as xDSL: admin-up, response interval (default 5 equals unset), deleted | passive mode not allowed on the port |
| `isam_ethernet_line` | verified | card 6 as Ethernet: admin, TCA enable/threshold, MAU type/power/capability/autonegotiate, deleted (type/power kept: no "no" form) | – |
| `isam_interface_cages` | read only | card 6: operational-mode idempotent | `description`/`apply_qos` do not exist on R6.2.04m |
| `isam_interfaces` | verified | card 6 / PON 7/16: pon, ont, uni, vlan-port, xdsl-line ports | – |
| `isam_l2cp_session` | verified | test session 200: create, alive-timer change, delete | – |
| `isam_l2cp_user_port` | verified | card 6 as xDSL: partition id set, deleted | – |
| `isam_link_agg` | verified | card 6 as Ethernet: port priority (deleted returns the CLI defaults, not the board's initial passive/short), group policy and max-active-port | group attributes without "no" form are kept |
| `isam_l2uni_onts` | verified | PON 7/16: PM, TC-layer threshold set/deleted | – |
| `isam_mcast_control` | verified (part) | package names set/reset | other settings (global) |
| `isam_ntp_onts` | verified | PON 7/16: client set, idempotent, deleted | – |
| `isam_pon_interfaces` | verified | PON 7/16 and 6/16: settings, restricted field (admin-down wrap), admin, replaced restore | – |
| `isam_pppoe_client_interface` | verified | card 6 VLAN port: create (masked password), idempotent, delete | – |
| `isam_pppoe_client_ppp_profile` | verified | test profile `zztest`: create, replaced change, delete | `ipversion` is not kept by the device |
| `isam_pppox_relay_global` | verified | session settings set/reset | – |
| `isam_qos_interfaces` | verified | card 6: UNI upstream queues (before bridge VLANs), `ont:` scheduler, `pon:` CAC profile, deleted | – |
| `isam_qos_profiles` | verified (part) | shaper profiles (single/two-rate, EIR) | other profile types |
| `isam_qos_tca` | verified | card 6 UNI queue 0: enable, thresholds, deleted | – |
| `isam_system_security` | verified (part) | SNMP views create/delete | operators, profiles, communities (not written: credentials) |
| `isam_traps` | verified (part) | test manager `192.0.2.1:162`: create, priority change, delete | definitions (global) |
| `isam_trouble_shooting_pon` | verified | card 6 PON 1/1/6/2: statistics interface, threshold, deleted | interval (global) |
| `isam_uni_onts` | verified | PON 7/16: TC-layer PM set/deleted | – |
| `isam_vlans` | verified | VLANs 3990/3991: create, change, replaced reset, delete; rename keeps unnamed settings, named-setting delete, absent VLAN skipped; aliases, quoted names, DHCP option 82 (nni/uplink with dependency, error 657), the value options (relay-id, linerate, l2-encaps, l2-encaps1, dhcpv6 relay/trust), drly-srv-usr-side on a cross-connect VLAN | pppoer-vlanaware (not in residential-bridge mode), dhcpr/dhcpv6r-vlanaware values |
| `isam_xdsl_boards` | verified (part) | card 6 as xDSL: DPBO profile set/change, deleted (reset; a board cannot be removed) | VCE profile (not on NDLT-F), VP boards (active card 1) |
| `isam_xdsl_inm` | verified | card 6 as xDSL: near/far end sensor set, change, deleted (needs the line's impulse noise sensor) | – |
| `isam_xdsl_lines` | verified | card 6 as xDSL: profiles, admin, TCA, impulse noise sensor, deleted | vectoring profile (needs the VP board link on active card 1) |
| `isam_xdsl_profiles` | verified (part) | service profile create/delete | spectrum, DPBO, vectoring, VCE profiles |
| `isam_xstp` | verified (part) | card 6 as Ethernet: port priority, edge port, path cost (no "no" form), deleted | global STP (not written) |

### Not testable on this device (device or hardware limit)

| Family | Reason (device answer) |
|---|---|
| `isam_arp_relay`, `isam_pppoel2_statistics` | accepted on an ONT VLAN port, but shown in no read (flat or detail): not verifiable |
| `isam_dhcp_relay` | accepted on a DSL VLAN port (`vlan:<port>:<vlan>`; `vlan-port:` is refused), shown in no read: not verifiable |
| `isam_ipv6_antispoofing_slot` | "not supported on this board" (FGLT-B) |
| `isam_qos_global` | line card settings need a plugged board (error 84) |
| `isam_dist_service` | every service type invalid (no MPLS/drouter); a bare service (create, targeted read, idempotent, `no dist-service` delete) is verified |
| `isam_xdsl_onts` | DPBO profiles not active; needs an xDSL ONT |
| `isam_xdsl_bonding` | "Bonding is not configured yet" without global bonding profiles |
| `isam_nat` | needs the CWMP platform enabled |
| `isam_epon_interfaces`, `isam_ngpon2_channel_groups`, `isam_channel_pair_pm` | hardware not installed |

### Not written: global settings (read and check-mode idempotence only)

Writing these changes the whole device (also Marc's card 5 and the NT); they need an
explicit decision per family: `isam_cwmp_plt`, `isam_dhcp_server`,
`isam_equipment_replan`, `isam_error`, `isam_generic_pon`, `isam_li_vlan`,
`isam_mcast_general`, `isam_multicast`, `isam_pon_global`, `isam_qos_maps`,
`isam_software_mngt`, `isam_system`, `isam_vlan_global`, `isam_voice_sip`,
`isam_xdsl_system`, `isam_xstp`, `isam_iphost`, `isam_linetest`.

Read-only check after the flag -> value fixes (2026-11-19): `isam_generic_pon`,
`isam_system_security`, `isam_system`, `isam_voice_sip`, `isam_software_mngt` gathered;
merged and replaced of the gathered facts in check mode send nothing except for
system_security's redacted-value replay differences. The sanitation follow-up below
corrects the earlier attribution of those differences to SNMP communities alone.

Shared attribute-table refactor (2026-11-19): offline differential checks against the
previous implementation agree on the lab captures for `software_mngt`, `voice_sip` and
`generic_pon` (voice_sip: 256 render cases). After VPN/DNS recovery, fresh read-only
verification on DS-LIN-TEST-01 passed for all three: gathered succeeded, and merged and
replaced of the gathered configuration in check mode both returned empty command lists
(`changed=0`, no failures). No configuration writes were sent. The earlier attempt had
matched no hosts because NetBox did not resolve; the successful retry clears that blocker.
The `settings_block` compatibility wrapper is checked offline against the previous
implementation and by unit tests; subsequent read-only checks of its users are
recorded below, with empty-resource limitations made explicit.

Sanitation follow-up (2026-11-19), read-only using
`tests/integration/resource_idempotence.yml`: gathered succeeded for all 16 reviewed
resources. Alarm, traps, link aggregation, QoS maps, equipment ONTs, system and mcast
general returned no merged/replaced commands in check mode. System-security returned
15 masked-value commands in each comparison (not configuration writes). A fresh
pre-cleanup checkout of `9b449c2a` generated the identical 15-command merged list;
all 15 commands contain masked values. This affects SNMP communities/notify profiles,
RADIUS, operators, SSH and filetransfer, not just community identities as the earlier
note suggested. CFM, LineTest, NAT, error, CWMP platform,
PON global, PPPoX relay global and trouble-shooting PON were empty: their comparisons
were skipped, so only their gathering was verified. No configuration writes or action
operations were executed. The integration check reports counts only, suppresses values,
and rejects reconciliation commands outside the verified masked-security exception.

Redacted-replay correction (2026-11-19): the security mismatch above is now fixed,
not grandfathered in as an exception. Actual Ansible-redacted gathered facts replay
with zero merged/replaced commands and `changed=0` on DS-LIN-TEST-01. Masked
credentials preserve current values and cannot be rendered/used to create entries.
Redacted identities are not recoverable: merged/replaced leave those entries unchanged
with a warning; rendering, destructive states and targeted gathering reject them.
Concrete identities are required to manage the hidden objects. The integration
assertion now requires empty command lists for security too.

Configured offline replay and parse-render-parse tests cover CFM, LineTest, NAT,
error, CWMP platform, PON global, PPPoX relay global and trouble-shooting PON—the
eight empty lab resources noted above. These tests exposed and now pin fixes for
LineTest's redundant replaced-parameter commands and unset-option resets. Their
configured live write verification remains unavailable without approved changes to
the lab; offline configured coverage and live empty gathering are distinct claims.

Approved isolated CFM domain attempt (2026-11-19): preflight found no CFM configuration
and confirmed domain 200 / `string:zztest` unused. Exact dry-run allow-list passed for
`configure cfm domain 200 name string:zztest level 3`; the device refused it with
`CFM error 16: VMAC HostID must be configured before configuring CFM`. No VMAC setting
was changed. The mixed-transport test harness timed out collecting post-attempt detail
output; its cleanup dry run and apply returned no commands. Lingering local read workers
were stopped, then a fresh read-only session confirmed domain 200 absent and full root
flat and detail configuration identical to preflight (zero differing configuration lines).
The card-6 troubleshooting test was paused for source-review fixes, then completed as
recorded below. No LineTest action or PPPoX global timer change has been attempted.

Review corrections (2026-11-19): fresh read-only gathered and merged/replaced check-mode
runs passed for generic-PON, voice-SIP and software management after the parser and
table-state fixes; all returned empty command lists, `changed=0`, and no failures.
Action failure/verification behavior and LineTest session-with-parameters removal are
covered offline; no operational actions or LineTest sessions were executed for this review.

Fresh approved troubleshooting write verification (2026-11-19): card 6 was planned
GPON with no installed board; PON `1/1/6/2` had no ONTs or operational traffic. Created
its statistics interface and thresholds (`bw-th-up 100000`, `bw-th-dn 200000`), read
back exactly, verified merged/replaced no-ops, changed downstream threshold to 250000,
read back and repeated idempotence checks. Deleted only that statistics interface and
reset only its two thresholds. Every write matched its check-mode dry-run allow-list;
full root flat/detail diffs after each step were confined to the test target. Final
full root flat AND detail configuration matched preflight with zero differing lines.
No global detection interval, PON operating setting, VMAC prerequisite, VLAN/MEP or
subscriber configuration was changed. The separate capture/operation sessions completed
without the earlier harness timeout. Sanitized configured resource lines are pinned in
`tests/fixtures/trouble_shooting_pon/isolated-write-r6.2.04m/`.

Read-only CLI help confirms CFM domain name/level are immutable and required at
creation, and confirms EFM OAM, L2CP, PPPoE-client and PPPoE-L2 synthetic fixture grammar.
Channel-pair, EPON and channel-group help is unsupported on this lab platform; their
corrected synthetic fixtures follow the CLI guide and do not claim live verification.

`isam_linetest` migrated to `IsamResourceModule` (2026-11-19); read-only on the lab ISAM
(no LineTest configured): gathered returns `{sessions: [], parameters: []}`, rendered emits
declarative commands only. Write behaviour (session destroy, parameters no-delete) is pinned
by unit tests, not exercised live (creating a session invokes a test action).

Operational action modules (`IsamActionModule`, not config resources): `isam_security_ext_authenticator`,
`isam_ethernet_statistics`, `isam_dhcp_relay_port_stats`, `isam_bridge_learned_mac`. Check-mode
verified on the lab ISAM (2026-11-19): commands built, identifiers/MAC validated, nothing sent.
The operations (clear counters/statistics, delete a learned MAC, clear 802.1X statistics) are not
executed live without a per-action decision. Execution safety (partial-execution reporting,
expected-disconnect hook, identifier validation) is pinned by unit tests.

Tested on card 6 replanned as xDSL (NDLT-F) and Ethernet (NELT-B) board instead of
the active cards 3 and 8; see the rows above and the offline scenarios in
`tests/fixtures/live_scenarios/`.

`isam_security_ext_authenticator` is action-only, `isam_facts` read-only.

## How the live tests run

Generators (outside the repository, `pon-migration-planner/.local/`): every write step
runs as a dry run first and is only sent when all its commands pass an allow-list of
the test objects; cleanup runs at the end; before/after captures are compared.

- `live-write-lc6-gen.py`: full customer ONT on card 6, card slot, PON.
- `live-write-families-gen.py`: the remaining families, one phase each; a phase list
  as fourth argument runs only those phases.
- `live-probe-gen.py`: raw command sequences (accepted/refused probes).
- `live-write-card6-gen.py`: families on card 6 replanned as another board type, in two
  parts with a capture in between; `build-scenarios.py` turns the results and captures
  into the scenario fixtures.
