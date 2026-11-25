# Live Validation 2026-11-25: what the device creates, requires and removes

Target: lab ISAM `DS-LIN-TEST-01`, R6.2.04m. One interactive CLI session per run;
every command was followed by an existence read of every object involved
(`info configure <node> detail`: a missing instance prints only the node header,
an existing one prints its node with all values; `flat` prints nothing for an
instance with default values only, so it cannot prove existence).

Scratch objects only: ONT `1/1/6/7/10` (free) on PON `1/1/6/7`, card 6 planned
without a board, fictitious serial `ALCL:F00DCAFE`, VLAN 99 (exists), VLAN 3999
(absent). Each run ended with every scratch instance absent again.

## Creation: what each command creates, and what is refused before it

| Command | Before its parent exists | Creates (read back) |
| --- | --- | --- |
| `equipment ont slot` | refused: GPON MGT error 0, invalid ONT ifIndex | |
| `ntp ont <ont>` | **accepted and does nothing** (silently lost) | |
| `ani ont tca-thresh <ont>` | refused: invalid token | |
| `qos interface ont:<ont> scheduler-node …` | refused: instance can not be configured | |
| `interface port ont:<ont> admin-up` | refused: instance can not be configured | |
| `equipment ont interface <ont> sw-ver-pland auto` | | the ONT, and with it `ntp ont`, `ani ont`, `interface port ont:`, `qos interface ont:` |
| `ethernet ont <uni>` | refused: invalid token | |
| `bridge port <uni>` | refused: specified lower-interface does not exist | |
| `qos interface <uni> upstream-queue …` | refused: invalid token | |
| `equipment ont slot <slot> …` | | the slot, and with it the UNI: `ethernet ont`, `interface port uni:`, `qos interface <uni>` |
| `bridge port <uni>` | | the bridge port |
| `bridge port <uni> vlan-id 3999` (VLAN absent) | refused: VLAN MGT error 81, L2-forwarder not created yet | |
| `bridge port <uni> vlan-id 99` (UNI without upstream bandwidth profile) | refused: VLAN MGT error 277, missing bandwidth profile on queue | |
| `bridge port <uni> vlan-id 99` (after the profile) | | `interface port vlan-port:<uni>:99`, `qos interface vlan:<uni>:99` |

Defaults of the device-created entries (non-default values shown by `detail`):

| Entry | Values at creation |
| --- | --- |
| `interface port ont:` | `no admin-up`, `link-updown-trap`; `admin-up` follows the ONT's admin state (set with `admin-state up`) |
| `qos interface ont:` | `ds-num-queue`, `ds-num-rem-queue`, `gem-sharing` not-applicable; `mc-`/`bc-scheduler-node none` |
| `ntp ont`, `ani ont tca-thresh` | defaults only |
| `ethernet ont` | `cust-info ""`, `auto-detect auto` |
| `interface port uni:` | `no admin-up`, `no link-updown-trap` |
| `qos interface <uni>` | scheduler-node `NGLT_Default`, cac-profile `FD_ONTUniVideo`, queues 0–3 with queue-profile `NGLT_Default` (card default, not a constant) |
| `interface port vlan-port:` | `admin-up`, `no link-updown-trap`, `severity no-value` |
| `qos interface vlan:` | as `ont:`, plus `us-num-queue not-applicable` |

`admin-state up` on an ONT without serial is refused (GPON MGT error 367).

## Removal

Each attempt on a fully built ONT (admin-up, slot, bridge port with VLAN 99):

| Command | Result |
| --- | --- |
| `qos interface <uni> upstream-queue 0 bandwidth-profile none` | refused: QOS MGT error 135, profile in use by the queue |
| `ntp no ont <ont>` | accepted, removes nothing |
| `bridge no port <uni>` (VLAN attached) | accepted; removes the VLAN port's interface and QoS entries too |
| `equipment ont no slot <slot>` (slot admin-up) | refused: Not in admin down state to delete (also on an admin-down ONT) |
| `equipment ont no interface <ont>` (ONT admin-up) | refused: Not in admin down state to delete |
| `equipment ont slot <slot> admin-state down`, then `no slot` | accepted; removes the UNI's ethernet ont, `uni:` interface and QoS entries |
| `equipment ont interface <ont> admin-state down`, then `no interface` | accepted; removes slot, UNI, bridge port, VLAN ports and every device-created entry |

## QoS

Two more runs with the scratch ONT, scratch profiles `NOCTEST_*` (removed again)
and PON `1/1/6/16` on the board-less card 6 (every change reset; read back equal).

**Profiles.** A reference to an absent profile is refused (invalid token): ONT
scheduler-node, UNI upstream-queue bandwidth profile, scheduler-node to shaper. A
profile in use cannot be deleted (QOS MGT error 1 for shaper and scheduler-node,
error 95 for bandwidth); it can be modified in use (all mandatory parameters
again, otherwise "command is not complete"). A scheduler-node whose shaper has the
default type `singletokenbucket` is refused on an ONT (error 71, shaper type not
compatible); the same for a PON's `dsfld-shaper-prof`.

**Settings that must come first, or are frozen later:**

| Setting | Constraint | Error |
| --- | --- | --- |
| ONT `ds-queue-sharing` | only before the ONT slot exists; cannot be enabled or disabled after | 58, 59 |
| ONT `us-queue-sharing` | not while an upstream queue of the ONT is in use | 81 |
| ONT `us-vlanport-queue` | not once VLANs exist on the ONT; excludes `us-queue-sharing` | 119, 143 |
| VLAN-port upstream queues | only with the ONT's `us-vlanport-queue` | 117 |
| UNI `gem-sharing` | not once VLAN ports are attached | 125 |

With `ds-queue-sharing` the downstream queues move from the UNI to the ONT.

**Attributes per interface kind.** Every attribute of the device syntax, set once
on each kind (a value different from the current one), reset, and at the end the
interface's saved configuration replayed: scratch ONT `1/1/6/7/10` with its UNI and
VLAN port 99, PON `1/1/6/16`, DSL line `1/1/3/48`, LAG `1/1/8/6`. PON, DSL line and
LAG read back identical to before. "yes" = accepted, a number = the QOS MGT error.

| Attribute | ONT | UNI | VLAN port | PON | DSL line | LAG |
| --- | --- | --- | --- | --- | --- | --- |
| scheduler-node | yes | 87 | 120 | 49 | 3 | yes |
| cac-profile | 42 | yes | 120 | 44 | 44 | 44 |
| ext-cac | 42 | 42 | 120 | 42 | 42 | 42 |
| ds-queue-sharing | 58 | 46 | 120 | 46 | 46 | 46 |
| us-queue-sharing | 81 | 46 | 120 | 46 | 46 | 46 |
| ds-num-queue | 45 | 45 | 120 | yes | 45 | 45 |
| ds-num-rem-queue | 128 | 114 | 120 | 114 | 114 | 114 |
| us-num-queue | 82 | 48 | 120 | 48 | 48 | 48 |
| queue-stats-on | 70 | yes | 120 | 220 | 84 | 84 |
| autoschedule | 96 | 96 | 120 | yes | 96 | 96 |
| us-vlanport-queue | 119 | 116 | 120 | 116 | 116 | 116 |
| dsfld-shaper-prof | 129 | 129 | 120 | 71 | 129 | 129 |
| bandwidth-profile | 202 | 179 | 120 | 202 | 202 | 202 |
| bandwidth-sharing | 202 | 184 | 120 | 202 | 202 | 202 |
| aggr-usq-profile | 203 | 193 | 120 | 186 | 186 | 186 |
| aggr-dsq-profile | 203 | yes | 120 | 203 | 203 | 203 |
| gem-sharing | 126 | 125 | 120 | 126 | 126 | 126 |
| scheduler-mode | 173 | 173 | 120 | yes | 173 | 173 |
| mc-scheduler-node | 174 | 174 | 120 | 204 | 174 | 174 |
| bc-scheduler-node | 175 | 175 | 120 | 204 | 175 | 175 |
| ds-schedule-tag | 218 | 218 | 120 | yes | 218 | 218 |

Unconditional refusals (the reason is the interface type: errors 42, 45, 46, 48,
49, 96, 114, 116, 120, 126, 129, 173, 174, 175, 202, 203, 218) are recorded as
`refuses` and checked by the module before writing. The DSL line and the LAG
refuse exactly the same set. The others depend on state or content and are not:

| Error | Condition |
| --- | --- |
| 3 | the scheduler-node profile is not supported by the line card's hardware (`NGLT_Default` on a DSL line) |
| 44 | the CAC profile's type does not fit the interface (`FD_Default` on a PON; `FD_GponVideo` is accepted) |
| 58, 59, 81, 82, 119, 128 | ONT queue settings: frozen once the slot, an upstream / remote downstream queue or a VLAN exists |
| 70, 84, 220 | queue statistics: need downstream queues, free statistics capacity, or the PON in `service-flat` mode |
| 87 | a UNI's scheduler-node must have the priority of `NGLT_Default` |
| 179, 184 | a UNI-level bandwidth profile or sharing excludes upstream-queue bandwidth profiles on the same UNI |
| 186, 193 | upstream aggregation profile / sharing not while an upstream queue is in use |
| 204 | multicast / broadcast scheduler on a PON only in `service-hierarchy` mode |
| 125 | UNI GEM sharing frozen once VLAN ports are attached |
| 71 | the shaper's type does not fit the interface |

The LAG shows `ds-num-queue 8` in its configuration, but replaying it is refused
(error 45): recorded as `read_only`, never sent.

A VLAN port's QoS entry takes no top-level attribute at all; it only carries
upstream queues, and only when the ONT has `us-vlanport-queue`. `not-applicable`
is accepted where the device shows it (ONT `ds-num-queue`) but refused elsewhere
(UNI `gem-sharing`, error 17); the module never sends it.

## QoS on the Ethernet card: the LAG, not the port

The QoS index of an Ethernet-card port names both the port and the LAG the
device keeps at the same index, and no QoS read path carries a prefix. Prefixed
read paths exist for the interfaces only (`show interface port la-group:X` /
`ethernet-line:X`, and `show interface stack`: `la-group:X` above
`ethernet-line:X`, `bridge-port:X` above `la-group:X`).

Read: on all 36 ports of card 8, `show qos interface-bandwidth X` reports
1,000,000 kbit/s, the LAG's current bandwidth (1 Gbit/s), while every Ethernet
line reports 0 (no connector).

Write: port `1/1/8/6` (no bridge port) joined LAG `1/1/8/5` and left it again.
While it was a member, the stack showed `la-group:1/1/8/5` above both Ethernet
lines and `la-group:1/1/8/6` above `no-interface`; QoS bandwidth of `1/1/8/5`
became 2,000,000 kbit/s, that of `1/1/8/6` 0; and `configure qos interface
1/1/8/6 queue-stats-on` was refused with "QOS MGT error 216: QoS cannot be
configured on the lag without physical port". Every read of both ports and LAGs
was identical before and after.

So a bare QoS address on an Ethernet card is the LAG. IHUB does not help here:
it models the NT's own ports and LAGs (`lag-N`), not the LT's user ports.

## NTP

The `ntp ont` entry comes and goes with the ONT; its own create and delete forms
do nothing. Its settings work on an existing ONT: `client-state on` is stored
(the values are `on`/`off`; `enable` is an invalid token).

## Read-only findings

* A QoS interface index is "the physical port or la-group of a user-port" (device
  help) and only the bare form is accepted (`xdsl-line:`, `bonding:`, `la-group:`
  are invalid tokens). The QoS status command (`show qos interface-bandwidth`)
  is addressed the same way. A bare QoS address on a DSL card is the line, never
  its bonding group. On an Ethernet card it is the LAG, see below.
* `link-agg group` has no create/delete form: the device keeps one group per
  Ethernet port at its index (with 2026-11-18: the port is the group's default
  member, `no port` refused with error 22).
* The ONT `1/1/6/7/1` left by the 2026-11-19 apply has a `uni:` interface with
  default values (`show interface port` counts it), absent from `flat` reads.

## Where this is recorded

`relations/<family>.py` (`created_with`, `requires` with evidence, the QoS
`refuses` table the module enforces before writing), the removal
facts of ONT, ONT slot and bridge port in `topology/objects.py`, and the bare QoS
address rule in `topology/identity.py`. The dependency graph and the write order
follow from them (`docs/resource-topology.md`).
