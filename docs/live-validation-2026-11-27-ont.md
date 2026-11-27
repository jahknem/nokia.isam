# Live validation 2026-11-27: ONT read and write path

Lab ISAM DS-LIN-TEST-01 (R6.2.04m), collection at `feat/onts-access` on the
core read contract (`feat/core-read-contract`). Writes only on card 6, which
was replanned from NELT-B to FGLT-B for the test and back to NELT-B afterwards.

## Read path (read-only)

Targeted `gathered` per family for ONT `1/1/5/1/3` (existing) and `1/1/5/1/4`
(free index on the same PON):

| Family / section | ONT 3 | ONT 4 |
| --- | --- | --- |
| `equipment_onts` interfaces, slots, loops, pm_collects | present | confirmed absent |
| `ani_onts`, `ntp_onts` | present | confirmed absent |
| `ethernet_onts`, `uni_onts`, `l2uni_onts` (both sections) | present | confirmed absent |
| `pon_interfaces` `1/1/5/1` | present | – |
| `trouble_shooting_pon` interfaces / threshold `1/1/5/1` | confirmed absent / present (defaults) | – |

A bridge port or QoS entry of a missing UNI answers "specified
lower-interface does not exist": `unknown` with `dependency_gap:
lower-interface`. The UNI's own absence decides it.

## Write path (scratch ONT `1/1/6/1/1`, UNI `1/1/6/1/1/1/1`, PON `1/1/6/1`)

Every write was first run in check mode, and its commands had to match an
expected list and address only card 6. Per family: set, read back, repeat
(no commands), reset or delete, read again, delete again (no commands).

| Family | Result |
| --- | --- |
| `equipment_onts` interface, slot, loop | create, idempotent; loop default-only before and after; ONT delete (admin down, `no interface`) removes the slot and UNI too |
| `ethernet_onts` | `cust-info` set and reset; the UNI stays (identity only) |
| `ani_onts` | **fixed**: thresholds of the existing entry were never compared; the entry lives as long as its ONT (`no tca-thresh` only resets it); upper must not be below lower (GPON MGT error 238) |
| `ntp_onts` | **fixed**: the entry lives as long as its ONT; `configure ntp no ont` is accepted with no effect; `deleted` resets attributes |
| `uni_onts`, `l2uni_onts` | PM / TC-layer nodes exist with the UNI; set, reset, idempotent |
| `qos_interfaces` | upstream queues 0, 4, 5 set and reset |
| `bridges` | port with PVID 99 and VLAN 20 on forwarder 699; `replaced` removes VLAN 20, `deleted` removes the port (confirmed absent) |
| `trouble_shooting_pon` | statistics interface created, idempotent, deleted (confirmed absent) |

A VLAN port needs bandwidth profiles on the UNI's upstream queues first:
without them, `bridge port <uni> vlan-id <v>` is refused (VLAN MGT error 277).
VLAN 99 needed queue 0, VLAN 20 on forwarder 699 queues 4 and 5. The order
spans two families and belongs to the write-order planner.

Final full `info configure flat` and `info configure flat detail` matched the
preflight capture with zero differing lines.

## Open

- A failed `isam_bridges` write reports only the device error, not which
  earlier commands were accepted (here: the port creation before the refused
  VLAN).
- `qos_interfaces` returns no `read_outcomes` on this branch
  (`IsamResourceModule` comes with #13).
- `pm_collects` writes need an XGS ONT and were not tested.
