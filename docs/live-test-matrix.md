# Live test matrix

What has been verified on the lab ISAM `DS-LIN-TEST-01` (R6.2.04m) and what remains.
Update this file with every live run; tests listed as verified are not repeated unless
the module's write path changes. Details and device behaviour:
`live-validation-2026-11-18.md`.

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
| `isam_cfm` | verified (part) | SLM timer set/reset | domains |
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
merged and replaced of the gathered facts in check mode send nothing (system_security only
differs on SNMP communities, whose names the gathered output redacts, unchanged by the fix).

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
