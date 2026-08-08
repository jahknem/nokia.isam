# Remaining Work Packages

Last reviewed: 2026-08-08

This document records the remaining repository work after inspecting the current tree, README, roadmap, tests, and relevant resource modules. It separates completed work from pending work so completed module delivery is not re-listed as outstanding.

## Current Evidence

- Repository has a large pre-existing uncommitted implementation change set. This document intentionally changes documentation only.
- `README.md` and `docs/resource_module_roadmap.md` say all 30 roadmap resource modules plus legacy modules are implemented; the roadmap still has some stale first-priority wording and older unit-test count (`105/105`).
- Local offline checks run during this review:
  - `make setup && make compile && make test`: passed; pytest collected and passed **120 tests**; compileall passed.
  - `python -m flake8 plugins/module_utils/network/isam plugins/modules tests/unit/modules/network/isam --max-line-length=160 --ignore=E501,W503 --statistics`: failed with existing lint debt. Current output includes 12 E126/E127/E128 continuation-indentation findings in `plugins/module_utils/network/isam` (prior context reported 11), plus broader E402/test-style debt.
- Prior context to preserve until live logs are attached: VPN is back; read-only reVPN gathered baselines for `voice_sip`, `multicast`, `xstp`, `xdsl_bonding`, and `system` matched Phase 0; `bridges` was skipped and needs a fresh gathered baseline.
- No live Ansible/device commands were run for this document.

## Completed Work Not Re-listed as Pending

- WP-DONE-01: Initial 30 roadmap resource modules exist in final collection paths, with module, argspec, config, facts, rm_template, and unit test coverage present where expected.
- WP-DONE-02: Offline syntax and unit-test baseline is green at 120 passing tests in the reviewed tree.
- WP-DONE-03: Prior live/read-only reVPN baseline confirmation exists by context for `voice_sip`, `multicast`, `xstp`, `xdsl_bonding`, and `system`; only evidence capture/documentation remains.

## Recommended Execution Sequence

1. WP-01 Bridge gathered baseline refresh.
2. WP-02 Live baseline evidence consolidation.
3. WP-03 Voice SIP parser/template hardening.
4. WP-04 Remaining facts/config parser migration sweep.
5. WP-05 Resource-layer lint cleanup.
6. WP-06 Documentation and roadmap refresh.
7. WP-07 Final verification and release readiness.
8. Optional follow-up: WP-08 Extended live check-mode validation.

## WP-01: Fresh `isam_bridges` Gathered Baseline

**Status:** remaining

**Objective/outcome:** Obtain and compare a fresh read-only `isam_bridges` gathered baseline so bridge parity is not inferred from stale or skipped data.

**Scope:** `plugins/module_utils/network/isam/facts/bridges/bridges.py`, `plugins/module_utils/network/isam/rm_templates/bridges.py`, `plugins/modules/isam_bridges.py`, `tests/unit/modules/network/isam/test_isam_bridges.py`, live evidence files/location chosen by maintainer.

**Prerequisites/dependencies:** VPN/device access to `DS-LIN-TEST-01`; collection symlink via `make setup`; inventory/vault access. Depends on no mutating device state.

**Implementation/verification steps:**
1. Run read-only gathered state for `nokia.isam.isam_bridges` against `DS-LIN-TEST-01`.
2. Capture raw command output and structured gathered result.
3. Compare against Phase 0 bridge baseline or create a new Phase 0 bridge baseline if none is authoritative.
4. Add/adjust unit fixtures only if live output exposes missing parser cases.
5. Re-run `make compile && make test`.

**Acceptance criteria:** Fresh bridge gathered output is saved or referenced; bridge parsed structure matches the live baseline for supported fields; any skipped/unsupported bridge commands are documented explicitly; offline tests still pass.

**Risk/notes:** Requires live VPN/device access but should be read-only (`state=gathered`, `info configure bridge flat`). Do not run merged/replaced/overridden/deleted against live device except in explicit check-mode work.

## WP-02: Live Baseline Evidence Consolidation

**Status:** remaining

**Objective/outcome:** Convert prior reVPN baseline results into durable repository evidence or documentation references.

**Scope:** Documentation/evidence area only, plus any affected tests if parser gaps are discovered: `voice_sip`, `multicast`, `xstp`, `xdsl_bonding`, `system`, and `bridges` after WP-01.

**Prerequisites/dependencies:** Completion or availability of prior read-only reVPN logs; WP-01 for bridges.

**Implementation/verification steps:**
1. Locate prior read-only outputs for `voice_sip`, `multicast`, `xstp`, `xdsl_bonding`, and `system`.
2. Document command, date, target, pass/fail status, and where raw evidence is stored.
3. Add bridge result after WP-01.
4. Record assumptions/open questions where raw logs are unavailable.

**Acceptance criteria:** A maintainer can trace each live baseline claim to a command and artifact/reference; `bridges` no longer appears as skipped without follow-up.

**Risk/notes:** Live access is not required if logs already exist; otherwise read-only VPN/device access is required.

## WP-03: `isam_voice_sip` Parser and Template Hardening

**Status:** remaining

**Objective/outcome:** Bring `voice_sip` from smoke-tested coverage to robust handling of all observed live command shapes.

**Scope:** `plugins/module_utils/network/isam/argspec/voice_sip/voice_sip.py`, `plugins/module_utils/network/isam/facts/voice_sip/voice_sip.py`, `plugins/module_utils/network/isam/rm_templates/voice_sip.py`, `plugins/module_utils/network/isam/config/voice_sip/voice_sip.py`, `plugins/modules/isam_voice_sip.py`, `tests/unit/modules/network/isam/test_isam_voice_sip.py`.

**Prerequisites/dependencies:** Prior/live `info configure voice sip flat` sample. Prefer WP-02 evidence first.

**Implementation/verification steps:**
1. Compare current schema/parser fields against live baseline and voice SIP CLI reference.
2. Add fixtures for any missing sections/options and negative/no forms.
3. Ensure gathered, parsed, rendered, and idempotent merged check-mode behavior is covered offline.
4. Run targeted voice SIP tests, then full `make compile && make test`.

**Acceptance criteria:** Unit tests cover all live-observed `configure voice sip` sections; rendered commands round-trip for supported fields; unsupported fields are documented rather than silently misrepresented.

**Risk/notes:** No live access required if baseline evidence exists. Live read-only access is useful for confirmation. Mutating voice SIP on a production-like MSAN is high risk and should be limited to explicit check mode unless separately approved.

## WP-04: Remaining Facts/Config Parser Migration Sweep

**Status:** remaining

**Objective/outcome:** Finish migration of parser/facts handling to the newer shared safe parsing patterns and eliminate inconsistent response handling.

**Scope:** `plugins/module_utils/network/isam/facts/facts_base.py`, all `plugins/module_utils/network/isam/facts/*/*.py`, all `plugins/module_utils/network/isam/config/*/*.py`, and matching `rm_templates`/tests where parser behavior changes.

**Prerequisites/dependencies:** Green offline baseline; prioritized live evidence from WP-02.

**Implementation/verification steps:**
1. Inventory facts classes that still manually unwrap/flatten raw connection output or parse hierarchical output inconsistently.
2. Migrate one resource at a time to shared helpers where safe.
3. Add regression fixtures for hierarchical, flat, empty, and noise/comment cases.
4. Run affected tests after each resource and full `make compile && make test` at the end.

**Acceptance criteria:** No supported module regresses in the 120-test suite; parser behavior is consistent for list/string connection responses; remaining manual parsers are justified by comments or tests.

**Risk/notes:** No live access required for refactoring, but read-only live gathered checks are recommended for high-risk/global resources (`system`, `software_mngt`, `multicast`, `voice_sip`).

## WP-05: Resource-layer Lint Cleanup

**Status:** remaining

**Objective/outcome:** Reduce actionable lint debt without broad generated-doc churn.

**Scope:** First pass: continuation/style findings in `plugins/module_utils/network/isam/**`. Optional second pass: test lint and generated module E402 policy.

**Prerequisites/dependencies:** Green tests before changes.

**Implementation/verification steps:**
1. Fix E126/E127/E128 continuation indentation in resource-layer files reported by flake8.
2. Re-run flake8 on `plugins/module_utils/network/isam`.
3. Decide whether module-level E402 in generated `plugins/modules/isam_*.py` should be fixed or ignored by configuration.
4. Run `make compile && make test`.

**Acceptance criteria:** Resource-layer continuation indentation findings are zero or documented as intentionally deferred; test suite remains green; lint policy for generated module imports is explicit.

**Risk/notes:** No live access required. Current verification found 12 E126/E127/E128 findings in `plugins/module_utils/network/isam`; prior context reported 11, so use fresh flake8 output as the source of truth.

## WP-06: Documentation and Roadmap Refresh

**Status:** remaining

**Objective/outcome:** Align public docs with the current implementation/test status and remaining work.

**Scope:** `README.md`, `docs/resource_module_roadmap.md`, `docs/command_tree.md`, this file, and any evidence index created in WP-02.

**Prerequisites/dependencies:** WP-01/WP-02 for live baseline status; WP-03/WP-04 if parser support changes.

**Implementation/verification steps:**
1. Update stale counts/status statements (`105/105`, first-priority wording, roadmap vs all-30 modules).
2. Link to live baseline evidence and this work-package list.
3. Ensure completed and remaining sections stay separate.
4. Review markdown rendering/readability.

**Acceptance criteria:** README and roadmap no longer conflict with the current module/test state; remaining work links to individual package IDs.

**Risk/notes:** No live access required once evidence is available.

## WP-07: Final Verification and Release Readiness

**Status:** remaining

**Objective/outcome:** Establish a clean release candidate signal after implementation and documentation work.

**Scope:** Whole repository excluding site-packages; build/test/lint/doc commands; release notes if used by maintainers.

**Prerequisites/dependencies:** WP-01 through WP-06 complete or explicitly deferred.

**Implementation/verification steps:**
1. Inspect `git status` and verify only intended files are changed.
2. Run `make compile`, `make test`, selected flake8/lint command(s), and `make doc` if collection dependencies are available.
3. Run read-only gathered checks for the high-priority live resources if VPN/device access is available.
4. Produce release notes with known limitations and live-access caveats.

**Acceptance criteria:** Offline checks are green or documented with accepted lint exceptions; live read-only checks are green or explicitly deferred; release notes identify unsupported/risky areas.

**Risk/notes:** Offline release verification requires no live access. Live gathered verification requires VPN/device access but should remain read-only.

## WP-08: Extended Live Check-mode Validation

**Status:** optional

**Objective/outcome:** Increase confidence in mutating-state command generation without changing device configuration.

**Scope:** Resource modules with only `merged/--check` or smoke coverage in the roadmap, especially global/high-risk modules: `system`, `software_mngt`, `multicast`, `voice_sip`, `dhcp_server`, `generic_pon`, and `bridges`.

**Prerequisites/dependencies:** Stable gathered baselines; explicit approval to run Ansible check-mode tasks against `DS-LIN-TEST-01`.

**Implementation/verification steps:**
1. Build minimal safe configs from gathered baselines.
2. Run `merged`, `replaced`, `overridden`, and `deleted` only in `--check` where appropriate.
3. Verify generated commands are safe and expected; do not apply changes live.
4. Add unit tests for any command-generation defects found.

**Acceptance criteria:** Check-mode command output is reviewed and documented for each selected resource; no live configuration changes are made.

**Risk/notes:** Requires VPN/device access. Even check-mode validation against global services should be treated as operationally sensitive.

## Open Questions / Assumptions

- The prior reVPN baseline match claims are accepted as context, but raw evidence files were not located during this quick documentation pass.
- The discrepancy between prior lint debt (11 continuation indentation issues) and current flake8 output (12 E126/E127/E128 findings in `plugins/module_utils/network/isam`) should be resolved by saving the exact lint command/output used for release gating.
- Generated module import placement (`E402`) may be intentional because Ansible modules keep large `DOCUMENTATION`/`EXAMPLES` blocks before imports; decide whether to configure flake8 accordingly instead of editing all generated modules.
