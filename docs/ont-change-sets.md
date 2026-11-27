# ONT configuration change sets

Resource modules accept the canonical configuration returned by `state: gathered`
or `isam_facts` as input. Callers do not need to trim full entries to identities
before passing them to `state: deleted`.

Use **check mode** while reviewing a change set. Modules read the current device
state and return `commands`, but do not call `edit_config`. This renders a comparison;
it does not prove that a device will accept every command or emulate the state of
earlier check-mode tasks. No transaction spans the read and the eventual write.

## Creating a bridge port

Pass its PVID, PVID VLAN and service VLANs together. `isam_bridges` orders commands:

1. Create the PVID VLAN (for example VLAN 99).
2. Assign the PVID to the port.
3. Create service VLANs, keeping tag/mapping/scope/QoS fields together.

An extra bootstrap call is not required. A PVID VLAN must either already exist or
be included in the request. Bridge keys returned by facts, such as
`max_unicast_mac`, are accepted alongside the historical hyphenated input names.

## Full-entry deletion

| Resource | Full-entry deletion behavior |
| --- | --- |
| `equipment_onts` | Remove requested slots before their ONT interfaces; bring the ONT interface down before removing it. |
| `ethernet_onts` | Reset removable attributes with `no <attribute>`; the UNI itself belongs to the ONT slot. |
| `interfaces` | Reset interface-port attributes using `configure interface port <name> no <attribute>`. |
| `bridges` | Remove the whole port when the request names every VLAN of the port, or supplies only the port identity. Port settings do not decide it (a `detail` read reports defaults). |
| `qos_interfaces` | Remove requested removable interface/queue attributes; never set values in `deleted`. |
| `ntp_onts` | Remove the NTP ONT object for an identity-only or full-entry request, including a bare object without attributes. |
| `ani_onts` | Reset the entry's set thresholds (`no lower-optical-th`, ...). The entry exists as long as its ONT; `no tca-thresh` does not remove it. |

Partial bridge and NTP requests still remove only the selected settings/VLANs;
unrequested siblings remain. A QoS nested queue identity selects that queue's
removable settings, not every queue on the interface. Deleting an absent target
produces no commands.

### Attributes without a standalone removal form

The included Nokia CLI reference documents set commands, but **no reset/delete
command**, for Ethernet `auto-detect` and downstream `queue` attributes. The modules warn and leave those settings unchanged
until their parent ONT/UNI/VLAN object is removed. This is not a complete standalone
QoS reset; it is deliberately not represented as one. Upstream and remote-downstream
queue attributes that have documented `no` forms are reset normally.

### Derived values

QoS `oper-weight` and `oper-rate` appear in the CLI grammar, but the device derives
them: on DS-LIN-TEST-01 setting them fails with "instance can not be modified", and
`oper-rate` follows the scheduler-node profile (evidence in
`rm_models/configure/qos/interface/_agent_report.json`). Queue `oper-weight` always
equals `weight` in the captures and is treated the same way (inferred, not separately
tested). These fields are parsed for facts and never rendered, neither set nor removed.

Reference: `docs/nokia_docs/21_-_QoSConfigurationCommands.pdf` (interface, queue,
upstream-queue and ds-rem-queue grammar), `24_-_BridgeConfigurationCommands.pdf`,
and `44_-_ONTEthernetPortConfigurationCommand.pdf`; captured command help is also
available under `rm_models/configure/`.

## Masked credentials

Device-displayed values such as `plain:******` are not reusable passwords. Equipment
ONT and NTP modules do not render these as new secrets. Explicit unmasked credentials
remain supported and sensitive through the normal Ansible `no_log` mechanisms.
Callers should continue excluding secrets from stored observations and exported
change sets.

## Validation

`tests/unit/modules/network/isam/test_ont_full_entry.py` exercises real parsers and
modules against synthetic replies. It checks gathered input, full and partial
deletion, sibling isolation, absent targets, create-command parse/merge idempotency,
PVID command ordering and check-mode non-execution. These tests require no device
credentials or NOC code.

## Targeted gathering

Reading a whole resource family is slow on a large MSAN. With `state: gathered` and
`config`, a resource module reads only the instances named in `config`, by their identity
fields; everything else in the entries is ignored:

```yaml
- name: Read only two NTP ONTs
  nokia.isam.isam_ntp_onts:
    config:
      - ont_id: 1/1/5/1/3
      - ont_id: 1/1/5/1/4
    state: gathered
```

Instances that do not exist are not returned, and `read_outcomes` reports them
`confirmed_absent`; other device errors fail the task. An instance with only default
values answers the plain read like a missing one (only a header); the module then reads
it with `flat detail`, which prints every existing instance, and returns it with its
identity only (defaults are not reported as configuration). The rule and its evidence:
`docs/targeted-read-contract.md`. Without `config`, the whole resource is read, as
before. `isam_facts` is unchanged and always reads whole resources.

Every instance list of every resource supports it; the lists and their identity
fields are in `plugins/module_utils/network/isam/targeted.py` (`TARGETED_GATHER`): a
field name, or a list of fields for a composite identity (`qos_profiles`:
`profile_type` and `name`); nested lists are dotted (`system`: `syslog.destinations`).
The file has no imports, so tools outside Ansible can use it to decide which families
to read per instance. Resources without instance lists (`dhcp_server`, `generic_pon`,
`l2cp`, ...) are single settings blocks and always read completely.

Only resources made of instance lists (`TARGETED_WRITES`) also compare
`merged`/`replaced`/`deleted` against just the named instances; all others read the
whole resource for writes.
