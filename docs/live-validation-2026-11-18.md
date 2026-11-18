# Live Validation 2026-11-18

Target: lab ISAM `DS-LIN-TEST-01`, OS version R6.2.04m, production inventory and vault.
Collection: 0.3.14 development branch.

## Read-only and check mode

- Every resource module's live `gathered` equals the `parsed` result of a fresh
  `info configure flat` capture taken at the same time.
- The root tree claims every line of the capture: no unclaimed or unmodelled lines.
- Targeted reads: 55 of 57 equal the whole read. The 2 differences are known and
  unchanged: `bridges` and `pon_interfaces` read with `flat detail`, so they also
  report default values.
- Check mode: 102 `merged`/`replaced`/`overridden` runs used the gathered facts as
  config. None produced commands.
- Offline sweep over the capture: `deleted` naming one instance touched nothing else
  in any of the 57 targetable lists.

## Writes

Scope: traffic-free test objects only. Each change was sent as a dry run first, and
every command had to name a test object. Each change was read back, reverted and read
back again. Before/after captures were compared.

| Module | Verified forms |
|---|---|
| `isam_qos_profiles` | shaper create, two-rate type with EIR (one packed command), `no excess-info-rate`, delete |
| `isam_alarm` | custom profile create/delete |
| `isam_xdsl_profiles` | service profile create/delete |
| `isam_system_security` | SNMP view create/delete; MIB names compared with their OIDs |
| `isam_cfm` | SLM timer set/reset |
| `isam_pppox_relay_global` | global session settings set/reset |
| `isam_mcast_control` / `isam_igmp` | package names set/reset |
| `isam_pon_interfaces` (empty PON) | label/polling/threshold set, idempotent re-run; restricted field (`diff-reach`) wrapped in `admin-state down`/`up`; admin down/up; `replaced` restore, idempotent |
| `isam_interfaces` (PON port) | `no link-updown-trap`, `no admin-up`, `replaced` restore, idempotent |
| `isam_vlans` | create (residential bridge), idempotent, change, `replaced` reset, delete |
| `isam_equipment_onts` | ONT + slot create, idempotent, `desc1` set and `replaced` reset, admin down/up, loop detection set/`deleted` reset, ONT delete (interfaces and slots admin down first) |
| `isam_ethernet_onts` | UNI `auto-detect`, admin up/down, `deleted` |
| `isam_ani_onts` | threshold entry create/`deleted` |
| `isam_ntp_onts` | client manual server set, idempotent, `deleted` |
| `isam_uni_onts` | TC-layer PM set/`deleted` |
| `isam_l2uni_onts` | PM and TC-layer threshold set/`deleted` |

## Device behaviour learned (fixed or documented)

- `admin-state` is rejected on the line that creates an ONT (`invalid token`). It is
  sent as a separate command.
- An ONT and an ONT slot are only deleted when admin down ("Not in admin down state to
  delete").
- `subslocid` has no `no` form; an unset value shows as `WILDCARD`.
- `log-auth-pwd` is always shown as `plain:******`, also when none is set.
- `none`/`not-applicable` QoS interface values cannot be reset where the setting is
  unsupported (`no bc-scheduler-node` on an ONT UNI).
- A shaper profile's type cannot be changed; EIR is only accepted with a two-rate type.
- Rejected out-of-range values, as documented: alarm mnemonic (letters only), CFM SLM
  (10-100 s), NAT aging (60-240 s).
- Bridge VLAN on an ONT UNI needs an upstream-queue bandwidth profile (VLAN MGT error 277).
- The transaction log records every CLI change as `127.0.0.1`. Use `show session` to
  see who is logged in.

## Not verified on the device

- `isam_qos_interfaces` UNI upstream-queue bandwidth profile.
- `isam_bridges` ports on an ONT UNI: create, partial `merged`, `replaced`, `deleted`.
  The test ONT was removed by a concurrent lab cleanup before this phase ran.
- `isam_nat`: needs the CWMP platform enabled.
- Global STP (`isam_xstp`): out of scope on a shared device.
- Families not installed on the target (EPON, NG-PON2 channel groups, channel pairs).
