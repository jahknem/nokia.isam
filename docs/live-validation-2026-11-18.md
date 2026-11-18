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

## Full customer ONT on linecard 6

Linecard 6 is planned (FGLT-B, GPON) without a board, approved for all tests. A customer
ONT prepared by the lab operator (`1/1/5/10/1`) served as template. Each module's
`parsed` output of the template lines was renamed to `1/1/6/1/1`, given a dummy serial,
and applied with `merged` in dependency order: `isam_equipment_onts`,
`isam_interfaces` (ONT/UNI ports), `isam_qos_interfaces` (UNI queues, `ont:` scheduler),
`isam_ethernet_onts`, `isam_ani_onts`, `isam_ntp_onts`, `isam_bridges` (four VLANs, PVID,
L2 forwarders), `isam_interfaces` (VLAN ports), `isam_qos_interfaces` (`vlan:` entries).

- The read-back equals the template in all 145 configured fields; every module is
  idempotent afterwards.
- The device creates the ANI threshold entry, NTP entry, VLAN ports and their QoS
  entries itself; the UNI gets scheduler node, CAC profile and four downstream queues.
- Verified changes: upstream-queue weight via `replaced` and back; bridge VLAN QoS via
  partial `merged`; `replaced` removing a VLAN (`no vlan-id`) and adding it back;
  Ethernet `cust-info` via `replaced`; ONT `desc1`; UNI port admin down/up.
- Verified `deleted`: bridge port, UNI and ONT QoS, Ethernet UNI, ANI, NTP, ONT; every
  read afterwards is empty.
- Card: slot lock/unlock (`no unlock`), `replaced` restore, cage read. PON `1/1/6/16`:
  set, restricted field, `replaced` restore.

Raw probe on a fresh ONT UNI (accepted / refused):

| Command | Device |
|---|---|
| `no cac-profile`, `no ds-num-rem-queue` | accepted |
| `no scheduler-node` | refused: "Scheduler Profile cannot be removed since queues associated" (error 52) |
| `queue N queue-profile none` | refused: "always requires a valid queue profile" (error 162) |
| `no us-num-queue` | refused: only for ONT (error 48) |
| `no mc-scheduler-node`, `no bc-scheduler-node` | refused: not supported on the UNI |
| upstream-queue `bandwidth-profile`/`no bandwidth-profile`/`no bandwidth-sharing` | accepted (no VLAN attached) |
| `ont:` `scheduler-node` / `no scheduler-node` | accepted |

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
- Upstream-queue parameters cannot be changed while a bridge VLAN uses the queue
  (QOS MGT error 41).
- A service VLAN is removed from a bridge port with `no vlan-id`; resetting its
  attributes is refused (VLAN MGT error 81).
- The transaction log records every CLI change as `127.0.0.1`. Use `show session` to
  see who is logged in.

## Not verified on the device

- `isam_nat`: needs the CWMP platform enabled.
- Global STP (`isam_xstp`): out of scope on a shared device.
- Families not installed on the target (EPON, NG-PON2 channel groups, channel pairs).
