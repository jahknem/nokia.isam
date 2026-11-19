# Live-test evidence for 0.3.14

This patch is isolated from `0.3.13`. Earlier device testing used the feature
branch, not this release checkout. It informed the backports but does **not**
certify this artifact. No release-specific device writes have been performed.

| Area | Earlier feature-branch evidence | Release-specific coverage |
| --- | --- | --- |
| ONT, bridge, UNI QoS | Scoped card-6/traffic-free create, change, readback, delete and restoration tests | Offline module-entrypoint regressions and existing fixtures |
| Ethernet, EFM OAM, xDSL, equipment planning | Scoped card-6 tests and supported/reset-form checks | Existing-schema reconciliation and parser regressions |
| QoS profiles, alarm, xDSL profiles, traps | Isolated object changes/readback/restoration | Deletion scope, packed commands and default handling regressions |
| PON/interface replay | Read-only/check-mode capture replay identified unnecessary default resets | Default normalization and state-contract tests |
| CFM | Domain creation blocked by the global VMAC HostID prerequisite; prerequisite was not changed | Synthetic scoped SLM/domain, immutability and replay coverage; no configured-domain write claim |
| LineTest | Empty read-only gather; no action/write authorization | Configured offline parser/state/replay tests only |
| Generic PON/system/global settings | Read-only evidence only; no new global writes authorized | Compatible parsing/scope fixes only; incompatible value schemas deferred |
| New feature-only resources | Including isolated PON troubleshooting tests | Not shipped in 0.3.14; no validation claim for this patch |
| Ext-authenticator action | No action execution authorized | Check mode, identifier validation and real serialized partial-failure tests; no live counter clear |

Raw device captures remain private and outside the repository. Tests use existing
sanitized fixtures or synthetic examples. No global STP changes, VMAC HostID
enablement, CWMP activation, NAT changes, LineTest actions or NOC changes were
made while preparing this patch. Future writes still require an individual scope
decision, dry run, allow-list and before/after comparison.

## Release-checkout gates

- Full `tests/unit` run (including connection plugins): 1,373 passed,
  58 skipped, 2 subtests passed. Skips include unavailable private captures.
- After adding the final CFM replay and alarm quoting cases, all 24 focused
  compatibility/safety regressions passed; lint was rerun successfully.
- Lint, type checking and all module/connection documentation checks passed.
- Built collection manifest, file checksums, version and excluded-content checks
  passed. An isolated artifact installation passed `ansible-doc` and real
  check-mode module entrypoints for Ethernet-line, VLANs and ext-authenticator.
- CI now includes connection-plugin tests and type checking as well as the
  existing unit/lint/docs jobs. Its result must be checked on the release commit.
