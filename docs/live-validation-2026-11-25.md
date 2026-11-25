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

## Read-only findings

* A QoS interface index is "the physical port or la-group of a user-port" (device
  help) and only the bare form is accepted (`xdsl-line:`, `bonding:`, `la-group:`
  are invalid tokens). A bare QoS address on a DSL card is the line, never its
  bonding group. On an Ethernet card the port and the LAG the device keeps at
  the same index stay ambiguous.
* `link-agg group` has no create/delete form: the device keeps one group per
  Ethernet port at its index (with 2026-11-18: the port is the group's default
  member, `no port` refused with error 22).
* The ONT `1/1/6/7/1` left by the 2026-11-19 apply has a `uni:` interface with
  default values (`show interface port` counts it), absent from `flat` reads.

## Where this is recorded

`relations/<family>.py` (`created_with`, `requires` with evidence), the removal
facts of ONT, ONT slot and bridge port in `topology/objects.py`, and the bare QoS
address rule in `topology/identity.py`. The dependency graph and the write order
follow from them (`docs/resource-topology.md`).
