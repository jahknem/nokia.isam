# ONT lifecycle acceptance test, 2026-11-28 (DS-LIN-TEST-01)

Release acceptance for the ONT path: a complete customer ONT created, read, changed and
removed through NOC's real change pipeline, with the collection at `main` `24bae523` and
NOC at `main` `3e9b5a7`. Local `ansible-playbook` runs, no AWX.

## Target and safety

- Test ONT `1/1/7/16/1` (UNI `1/1/7/16/1/1/1`) on card 7: planned FGLT-B, no board
  installed, no ONTs, bridge ports or VLAN ports before the test. Dummy serial, test
  customer data; the configuration was copied from an existing ONT's own read.
- Every write command had to match an allow-list naming only the test ONT, its slot,
  UNI and VLAN ports, checked on the check-mode output before anything was written.
  NOC's apply gate additionally refuses to write unless every re-checked step is
  identical to the approved check.
- Full `info configure flat` and `flat detail` captures before and after.

## Phases and result (final run)

| Phase | How | Result |
| --- | --- | --- |
| Plan reads | NOC plan reads (`noc_canonical_read.yaml` → `isam_read`), `change_set.build` | source ONT read completely; target `confirmed_absent` |
| Create | change set `create` → check → apply with approval fingerprints | 11 steps ok; approval gate matched exactly |
| Idempotence | the same check again | 0 commands in all 11 steps |
| Read-back | NOC targeted reads of the test ONT | equal to the change set in every field |
| Refresh | `isam_refresh` of the ONT | 8 objects, 24 sections present, 12 absent, 4 gaps (`isam_dhcp_relay`, not observable by design); 16.6 s |
| Change | direct module runs (bridge partial merge, VLAN removal/restore, UNI customer info, ONT description, UNI admin state, QoS queue weights), each dry-run and allow-listed | all read back as written; the final `replaced` of each family sent 0 commands |
| Delete | NOC `delete` plan → check → apply | all steps ok; `bridge no port` before the ONT; `equipment ont no slot` / `no interface` |
| Absence | NOC targeted reads, `isam_refresh` | every family `confirmed_absent` except the bridge port (see below); refresh complete, 8 sections absent |
| Postflight | captures | 0 of 4119 flat and 0 of 11809 detail lines differ |

## Defects found and fixed

- Command order depended on Python's hash seed (netcommon `dict_merge`); NOC's apply
  gate refused the write because the re-check differed from the approved check (#30).
- NOC passed full source configurations to `deleted`, which nokia.isam reads as "reset
  these fields": the ONT would have been reset field by field instead of removed
  (NOC #3).
- `isam_interfaces` recorded no read outcomes (every port unverified after removal);
  `severity no-value` was reset on VLAN ports, which the device refuses (#31).
- `isam_bridges` turned the TPID table (`vlan-tpid<n>`) into fields the argspec rejects (#31).
- A refused command did not report which commands had already been applied (#32).

## Open

- **Bridge port after its UNI is removed**: the device answers "specified lower-interface
  does not exist". By the read contract that is a dependency gap, not absence, so the
  bridge port stays `unverified` in NOC's reads (the refresh proves it absent through
  the missing ONT). Whether a missing lower interface may prove the absence of the
  bridge port on that same port is a contract decision.
- **QoS owner of a bonded line**: still needs two service-free xDSL lines.
