# Remaining Work Packages

Last reviewed: 2026-08-10

The complete per-RM plan is in [`resource_module_work_packages.md`](resource_module_work_packages.md).
This page records cross-cutting status; the linked plan is authoritative for
individual module gaps, evidence, dependencies, and acceptance criteria.

## Completed

- Read-only gathered validation passed for every resource module on `DS-LIN-TEST-01`; see `docs/live-validation-2026-08-10.md`.
- Operational facts use explicit `gather_subset` and `ansible_net_*` output names.
- DHCP relay parsing no longer probes IPv6 counters unless IPv6 counters are configured.
- External-authenticator is an explicit action-only module.
- `cli_config` is limited to text configuration because ISAM does not expose replace or rollback operations.
- LineTest uses the documented session destroy command and supports documented optional-field `no` forms.
- The 0.3.0 migration notes document the breaking facts and module API changes.
- Parser fixture bundles now carry device and software-version descriptors.
- All 52 resource modules now have canonical-state contract coverage for parsed,
  rendered, merged, replaced, overridden, and deleted check-mode execution.
- Read-only `info ... detail` evidence from `DS-LIN-TEST-01` expanded the live
  vocabulary inventory; notably, ANI ONT exposes `tca-thresh`,
  `lower-optical-th`, `upper-optical-th`, and `rssi-profile`.
- Optional PON gathering now treats device-reported unsupported-command errors
  as an absent feature and returns an empty resource. The Nokia references
  confirm the valid installed-feature paths are `configure epon interface`,
  `configure channel-group`, and `configure channel-pair interface`.
- SSH session-limit behavior was analyzed with synchronized raw SSH,
  Paramiko, and Ansible probes. The opt-in ISAM connection wrapper now retries
  only connection establishment after a fresh transport reset; command replay
  and authentication retry remain disabled by default.
- Voice SIP detail-flat vocabulary now covers all words emitted by the current
  target for VSP and redundancy entries, including the corrected
  `dmpm-intdgt-expid` spelling. Positive value-bearing forms still require
  separate grammar validation before being exposed as typed values.
- Voice SIP replacement now removes unrequested list siblings with valid device
  `no` commands; override/delete and full section-specific state assertions
  remain in the linked per-RM package.
- PON interface packed detail-flat lines are split into documented command
  segments instead of allowing `label` to consume the remaining fields. Base
  and documented PM/TCA interface subtrees are covered by parser and renderer
  tests, with technology-aware reset normalization.
- Equipment ONT interface support now includes documented bridge-map, enable,
  optics, VoIP, and IP-host allowance fields.
- System support now includes quoted welcome banners, maximum LT link speed,
  loop-ID syntax, and relay-ID syntax.
- QoS queue profiles now preserve the documented `unit packet|byte` field.

## Remaining

### RM-specific hardening

See `docs/resource_module_work_packages.md`. The highest-priority packages are
Voice SIP, PON interfaces, equipment ONTs, system, ANI ONTs, generic PON, and
software management.

### Parser consistency sweep

Inventory remaining manual parsers and normalize list/string responses, empty
output, hierarchical output, and noise handling. Add regression fixtures before
changing shared helpers.

### State coverage

The generic state contract now covers all 52 resource modules in offline and
check mode. Continue adding resource-specific assertions for command ordering,
negation semantics, and multi-instance reconciliation where the generic
contract does not capture device grammar details. Live validation remains
check-mode only.

### Lint and type quality

The development tools are now part of the documented gate. Generated Ansible
module imports and legacy style patterns are covered by the explicit flake8
policy in Makefile/tox. Mypy runs with the current collection's legacy dynamic
data model exclusions; stricter annotations remain future cleanup.

### Release verification

The local unit, compile, lint, typecheck, documentation, and artifact gates
pass. The complete tox matrix still requires a clean environment with the
`ansible.netcommon` Galaxy collection installed.

## Explicit Limitations

- `nokia.isam.cli_config` supports `config` only.
- `isam_security_ext_authenticator` is action-only and must be given `config`.
- LineTest parameter deletion has no documented device command; delete the
  containing session instead.
- No live mutating commands are authorized by the collection's validation
  workflow.
