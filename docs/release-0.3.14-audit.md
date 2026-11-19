# 0.3.14 compatibility audit

## Release boundary

The patch branch starts at released tag `0.3.13` (`f7075ba4`), not at
`feature/root-config-tree`. Fixes were extracted by file and semantic hunk from
the feature work through `7ab6efbc`, then adapted to the released implementations.
No complete mixed feature commit was cherry-picked.

`test_patch_compatibility.py` fingerprints all 53 released argument specifications
and the complete Python module inventory against `0.3.13`. Names, types, choices,
aliases and required flags must remain identical. Defaults alone are excluded:
the audited removals prevent Ansible from injecting resets into partial requests.
They concern VLANs, distribution services, L2CP, L2CP sessions, IPv6 anti-spoofing
and Ethernet-line TCA thresholds. Existing CLI-spelled VLAN facts are retained.

Safety corrections can change commands: a named-field delete must not delete its
parent, a read must never reconcile, and a bare administrative path is not an
operation. Invalid creation-only changes fail before execution rather than sending
commands known to be refused by the device. Check-mode review remains required.

## Included fix groups

| Area | Included without changing the released schema |
| --- | --- |
| Transport | Retain libssh options across resets/retries; reset absolute admin context |
| Facts | Wrapped echoes, deduplicated reads, default-only instances, empty list shapes, MAU power, unrelated-line filtering |
| Deletion | Named section/instance/field scope; correct object removal and supported attribute resets |
| ONT/bridge/QoS | Ordering, PVID transitions, partial VLAN merge, default-off replay, required scheduler/profile settings, packed profile commands |
| Ethernet/EFM/xDSL | Existing attribute grammar and state fixes, defaults and idempotence; no additional attribute families |
| CFM/LineTest | Scoped safety and configured replay fixes in the existing implementations |
| Existing action | Explicit operation, safe identifier, per-command partial failure, real Ansible failure serialization |

The Ethernet-line parser/config implementation is replaced locally because the
old templates could not render existing thresholds/MAU flags correctly. Its public
schema is unchanged except for removal of injected TCA defaults. The collection's
existing resource lifecycle remains in place; the broad base/table migration is
not a patch-release dependency.

## Reserved for the major release

- Root configuration tree, grammar metadata and gap reporting.
- New resource and operational-action modules, including system security,
  troubleshooting PON and the additional xDSL/UNI/global families.
- New attribute/subnode coverage on existing resources.
- Bool-to-value changes in generic PON, SIP, software management, VLAN flags and
  related global settings; these cannot be backported while preserving types.
- VLAN snake_case fact keys and the associated table migration. CLI-spelled
  options/facts and legacy boolean flags remain in 0.3.14.
- QoS-map control-packet schema replacement (`queue`/`profile` to `dscp`/`pbit`/`tc`).
- Shared `IsamResourceModule`, `AttributeTable`, settings-table and action-base
  refactors. Fixes needed by existing modules are implemented without importing
  the new framework or its modules.

Those exclusions do not imply the legacy schemas describe every device command
correctly. They prevent a patch from silently changing inventory/playbook types.
NOC and the original feature worktree are unchanged.

## Review findings at e84b6e2

All five findings in that source review were fixed on the feature branch in
`85c39714`. Both shared abstractions were retained there. Their patch applicability:

- `failed_command`: covered here on the existing ext-authenticator action, with
  real Ansible JSON serialization and no retry.
- Unrelated list removal in `replaced`: corrected here in every legacy SIP list;
  legacy software OSWP replacement was already scoped and has a regression check.
- LineTest session-owned parameters: corrected here in the existing implementation.
- Unknown-leading attributes: the reviewed `AttributeTable` is not shipped here;
  its feature-branch fixture/tests remain with `85c39714`.
- Verification failure context: the new shared action verification hook is not
  shipped here; its structured failure regression remains with `85c39714`.

## Validation

Release validation runs from this checkout through tox, including connection tests
(`TESTPATH=tests/unit`), lint, type checking and documentation checks. Regression
tests execute real module entrypoints against synthetic fake-device responses;
the action failure test uses real Ansible JSON serialization. Optional private
capture tests skip when the external captures are unavailable.

No device writes are part of this backport validation. See
[the matrix](live-test-matrix.md) before interpreting earlier live evidence.
