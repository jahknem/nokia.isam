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
| `isam_equipment` | verified (part) | card 6: slot lock/unlock, replaced restore | diagnostics SFP, protection elements |
| `isam_equipment_onts` | verified | card 6: interface, slot, loops, sw-ctrl (test id 200), admin down/up, delete with shutdown | `pm_collects` (XGS ONTs only), sw-ctrl config files (need a real file) |
| `isam_ethernet_onts` | verified | card 6: UNI settings, phy/l2/cfm sub-nodes, identity and named-field deleted | – |
| `isam_igmp` | verified (part) | package names set/reset | other settings (global) |
| `isam_interface_alarms` | verified | test object `epon` (no EPON hardware): severity set/restore | – |
| `isam_interface_cages` | read only | card 6: operational-mode idempotent | `description`/`apply_qos` do not exist on R6.2.04m |
| `isam_interfaces` | verified | card 6 / PON 7/16: pon, ont, uni, vlan-port ports | – |
| `isam_l2cp_session` | verified | test session 200: create, alive-timer change, delete | – |
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
| `isam_vlans` | verified | VLANs 3990/3991: create, change, replaced reset, delete | – |
| `isam_xdsl_profiles` | verified (part) | service profile create/delete | spectrum, DPBO, vectoring, VCE profiles |

### Not testable on this device (device or hardware limit)

| Family | Reason (device answer) |
|---|---|
| `isam_arp_relay`, `isam_pppoel2_statistics` | accepted on an ONT VLAN port, but shown in no read (flat or detail): not verifiable |
| `isam_dhcp_relay` | `port-stats` invalid for ONT VLAN ports; needs a DSL/Ethernet LT port |
| `isam_efm_oam_interface` | invalid for ONT UNIs; needs an EFM (LT Ethernet) port |
| `isam_ipv6_antispoofing_slot` | "not supported on this board" (FGLT-B) |
| `isam_qos_global` | line card settings need a plugged board (error 84) |
| `isam_dist_service` | every service type invalid (no MPLS/drouter). **Open bug:** a refused create still leaves a bare `configure dist-service <id>`; the device removes it with `configure no dist-service <id>` (verified), but `deleted` only resets attributes and the parser ignores the bare line |
| `isam_xdsl_onts` | DPBO profiles not active; needs an xDSL ONT |
| `isam_l2cp_user_port` | DSL ports only |
| `isam_nat` | needs the CWMP platform enabled |
| `isam_epon_interfaces`, `isam_ngpon2_channel_groups`, `isam_channel_pair_pm` | hardware not installed |

### Not written: global settings (read and check-mode idempotence only)

Writing these changes the whole device (also Marc's card 5 and the NT); they need an
explicit decision per family: `isam_cwmp_plt`, `isam_dhcp_server`,
`isam_equipment_replan`, `isam_error`, `isam_generic_pon`, `isam_li_vlan`,
`isam_mcast_general`, `isam_multicast`, `isam_pon_global`, `isam_qos_maps`,
`isam_software_mngt`, `isam_system`, `isam_vlan_global`, `isam_voice_sip`,
`isam_xdsl_system`, `isam_xstp`, `isam_iphost`, `isam_linetest`.

Not on card 6 and carrying configuration of other cards: `isam_ethernet_line` and
`isam_link_agg` (NNI uplink ports, card 8), `isam_xdsl_lines`, `isam_xdsl_boards`,
`isam_xdsl_bonding`, `isam_xdsl_inm` (xDSL card 3).

`isam_security_ext_authenticator` is action-only, `isam_facts` read-only.

## How the live tests run

Generators (outside the repository, `pon-migration-planner/.local/`): every write step
runs as a dry run first and is only sent when all its commands pass an allow-list of
the test objects; cleanup runs at the end; before/after captures are compared.

- `live-write-lc6-gen.py`: full customer ONT on card 6, card slot, PON.
- `live-write-families-gen.py`: the remaining families, one phase each; a phase list
  as fourth argument runs only those phases.
- `live-probe-gen.py`: raw command sequences (accepted/refused probes).
