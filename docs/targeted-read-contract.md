# Shared targeted-read contract

`facts/facts_base.py` owns transport, selector validation and existence evidence.
Resource families declare command formats and parse configuration; they do not
implement their own transport or absence rules.

## Existence of one addressed instance

A targeted `gathered` read of one instance (`info configure … <id> flat`) ends in
one of three outcomes:

| Reply to `flat` | Reply to `flat detail` (sent only if `flat` shows nothing) | Existence |
| --- | --- | --- |
| the instance's lines | – | present |
| `instance does not exist` | – | confirmed absent |
| header only | the instance's line (with its defaults) | present |
| header only | header only, or `instance does not exist` | confirmed absent |
| header only | a rejection (`invalid token`) | unknown, command rejected |
| header only | a missing dependency (`lower-interface does not exist`) or another instance's line | unknown |
| `invalid token` / other device error | – | unknown, command rejected |

Families whose single read already is `flat detail` (bridge ports, ONT
interfaces and slots, equipment slots, PON interfaces) skip the second read: their
header-only reply is confirmed absence, their instance line is presence.

`flat` prints only values that differ from the default, so an instance with
defaults only answers like a missing one. `flat detail` prints every existing
instance with its defaults; for a default-only instance the helper returns the
bare path to the family parser, never the defaults as configured attributes. The
parser must keep an identity-only instance.

A failed transport fails the read and keeps sanitized per-selector outcomes.

### Evidence

Read-only matrix on DS-LIN-TEST-01 (R6.2.04m), 2026-11-27, generated from
`TARGETED_GATHER`: for each of 104 single-instance sections the read command was
taken from `isam_read` itself, the reference was the whole node read with
`flat detail` (an instance in it but not in the whole `flat` read is default-only):

- 67 of 67 default-only instances (35 sections): `flat` header only, `flat detail`
  the instance line.
- 52 instances missing on an existing parent: 31 `instance does not exist`, 20
  header only in both reads, 1 missing lower interface; all agree with the node's
  `flat detail` list.
- 36 generated identities outside the device's range were refused (`invalid
  token`): those families have an instance for every valid index.
- 16 nodes empty on the lab, read with identities of existing objects: every one
  answered `instance does not exist`, header only, or a refusal for an object that
  cannot exist (EPON on GPON, NG-PON2 on this firmware).

No section broke the rule.

## Exceptions (data, `targeted.ABSENCE_POLICY`)

| Policy | Meaning | Sections |
| --- | --- | --- |
| `silent` | a switch without attributes: present prints nothing, also with `detail`; only `instance does not exist` proves absence, so the header means present | `isam_arp_relay.config`, `trouble_shooting_pon.interfaces` |
| `unobservable` | every read answers the same whether the setting is on or off: never present or absent | `isam_dhcp_relay.config` |

Family branches add their sections to the same table. Each entry needs live evidence of
both states; an entry is never inferred from one capture.

`empty_absent_sections` remains for families whose read never needs the detail
probe (every instance prints mandatory attributes): a header-only `flat` reply is
confirmed absence without the second read.

## Scope

Write-state comparisons (`merged`, `replaced`, `deleted`) do not send automatic
probes; `bare_sections` keeps that behavior for families that need it there.
Whole-family reads, whole-node reads and shared-node reads with
`instance_checks` do not acquire the probe: one command serves several
selectors, and a non-empty whole-node reply is not proof that each requested
selector exists (`instance_checks` decides presence; missing selectors stay
unknown).

Named instances with incomplete identities fail before any command is sent. An
explicit targeted request never silently widens to a whole-family read.
