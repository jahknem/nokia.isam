# Live-apply follow-up: offline regressions

Scope: the command-generation issues reported against 0.3.13 by the NOC
live-apply handover on 2026-11-19. This follow-up changes the collection only.
It does not run AWX jobs, change NOC, clean up device objects or refresh an EE.
The earlier device evidence is not fresh verification of these changes.

## Findings and changes

| Report | Candidate finding | Follow-up |
|---|---|---|
| Combined ONT admin-state | Interface creation was already split; slot creation and compaction still combined it. | Slot admin-state is standalone for creation and updates too. |
| Single-element `merged` fails with `config.interfaces.flat` | Not reproduced through real netcommon direct execution on Core 2.19.12. | Retain literal/templated list, flat/block/wrapped-echo reply and run/check regressions. No speculative argument rewriting. |
| Deletion skips already-down objects; shutdown propagation | Confirmed: shutdown was conditional on gathered state, followed immediately by removals. | Reassert each removed interface/slot down, settle, and require targeted readback before any removal. |
| Bridge VLAN lacks upstream bandwidth profile | Prerequisite spans independent module calls. | Document and test caller order: upstream QoS first, bridge VLAN attachment second. Do not make bridge code issue implicit QoS writes. |
| Severity and QoS invalid placeholders/reset forms | Confirmed in rendering, replacement and nested queue deletion paths. | Treat severity `no-value` as unset/reset; normalize QoS placeholders at both comparison boundaries. |

## Deletion contract

For whole-entry `state: deleted`, only identities selected by the existing
deletion contract are shut down. Named-setting deletion is unchanged and does
not shut down the ONT. An absent entry generates no shutdown or removal.

1. Issue separate `admin-state down` commands for the interfaces and slots that
   will be removed, regardless of their gathered admin state.
2. Wait one second, then read each pending identity with
   `info configure equipment ont <interface|slot> <identity> flat detail`.
3. Require the exact identity and explicit `admin-state down`. Missing output,
   header-only replies, other identities and an up state are not confirmation.
   Poll at most five rounds, with a one-second settling interval per round.
   Individual connection/read timeouts still follow the connection configuration.
4. Only after all targets confirm down, send the planned removals: slots before
   interfaces. A removed ONT interface takes its own slots with it (they are shut
   down and removed first; the device refuses to delete an ONT that still has
   slots). Other ONTs and their slots are never included.

`state: overridden` removes the ONT interfaces and slots it does not keep through
the same sequence (shutdown, readback, slots before interfaces); before 2026-11-26
it sent the bare removals, interface first, which the device refuses.

Only reads are polled. Shutdown and removal commands are sent once, one command
per transaction. Read errors, readiness exhaustion and write failures stop the
sequence. Failure results distinguish accepted commands, the failed command (if
any), and never-sent pending commands. An attempted write reports changed, even
if its outcome is unknown. A clean transport return does not certify completion.
Read back actual state before deciding on any retry.

Check mode reports the shutdown/removal plan without writes, settling waits or
readiness polls. Ordinary baseline facts reads still occur.

## Placeholder and ordering contract

- Gathered severity `no-value` counts as unset. An explicit request to clear a
  real severity uses `no severity`, not the invalid `severity no-value`.
- QoS detail `not-applicable` is not a settable value. Omitted/unset fields must
  not cause unsupported resets such as `no bc-scheduler-node`.
- Queue entries receive the same normalization as top-level QoS fields. Preserve
  actual bindings and supported explicit `none` profile resets; do not turn an
  unsupported placeholder into removal of a real target binding.
- Provision referenced profiles and upstream queues before attaching bridge
  VLANs. Updating in-use upstream queues can require a separately approved VLAN
  detach/re-attach sequence (device error 41). Module calls cannot reorder other
  tasks; no implicit detach or prerequisite creation is added here.

## Regression locations

- `tests/unit/modules/network/isam/test_live_apply_regressions.py`: slot creation,
  already-down deletion, settling/readiness, fail-closed reads, partial failures,
  no retries, check mode, named-setting safety, placeholders and caller ordering.
- `tests/unit/modules/network/isam/test_resource_direct_execution.py`: the real
  action/direct-execution/AnsibleModule path with stubbed device connections.
- Existing ONT and full-entry tests retain sibling preservation, deletion order,
  absent-object idempotence and replay coverage.
- `tox -e py312-core219` pins Core 2.19.12. CI runs the full unit tree on this core
  and on the current supported core, including connection-plugin tests.

## Exact EE runtime check

All **50 new regression cases** passed inside the existing `89cd292` EE runtime
(Python 3.11, Ansible Core 2.19.12, ansible.netcommon 8.6.1), as UID 1000 with
networking disabled. Only collection plugin source and tests were mounted
read-only; pytest was installed from predownloaded wheels into an ephemeral
temporary directory. Device connections were stubbed. No host inventory,
credentials or private captures were mounted.

This validates the changed source against the actual runtime stack, not a newly
built collection artifact. It does not change the installed image or the EE used
by AWX: those still contain the earlier candidate until separately rebuilt.

Lint, type checking and documentation validation for all 72 modules and the
connection plugin also passed.

## Full offline gate

The final full unit tree, including connection plugins and private-capture replay,
passed on both Ansible Core **2.19.12** and **2.21.6**: **2,914 passed, 14 skipped,
247 subtests passed per core** (point-in-time result for this 2026-11-19 follow-up,
`TESTPATH=tests/unit` with `ISAM_ROOT_CAPTURES` set; later commits add tests, and
without the private captures their tests skip, so the totals are not expected to
reproduce on a later checkout). The 50 new regression cases are included in these
totals, not additional tests to add again. Private captures were selected with
`ISAM_ROOT_CAPTURES`; no capture content was added to the repository.

The local unpublished candidate archive passed all **610 file checksums** and
source-equality/content-scope checks. An isolated archive install loaded all 72
module documentation entries from the installed artifact, not the source symlink.

## Remaining live evidence

The original `.flat` report remains unconfirmed without its exact failing input
and sanitized reply/runtime reproducer. Passing synthetic direct-execution cases
is not proof that every AWX path is fixed. The settling/readback policy and the
complete ONT lifecycle still need separately approved device validation. No
global changes, customer writes or automatic cleanup are authorized by this file.
