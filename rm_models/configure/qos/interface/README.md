# QoS Interface live examples

This folder contains live-captured examples for `configure qos interface` on DS-LIN-TEST-01.

Key points
- The device only accepts a subset of attributes on UNI `1/1/5/2/1/1/1`.
- Verified toggle: `queue-stats-on` (present/absent), with Before/After evidence across merged/replaced/overridden/deleted.
- Constraints observed during live runs (see `_agent_report.json` for full details):
  - `ds-queue-sharing` → rejected on UNI; ONT-level attempt rejected because ONT card is provisioned.
  - `autoschedule` → not supported on this interface type (UNI).
  - `us-vlanport-queue` → allowed only on ONT interface; not allowed on UNI.
  - `oper-weight`/`oper-rate` → immutable on this platform for this instance.

Safety
- No changes were performed under `1/1/5/1/15`.
- All changes under `1/1/5/2` were minimal and fully reverted; current state has `queue-stats-on` disabled on `1/1/5/2/1/1/1`.

Artifacts
- gathered_example_01.txt — global `info configure qos interface` excerpt including target interface.
- merged|replaced|overridden|deleted_example_01.txt — `queue-stats-on` Before/After evidence.
- parsed.json — machine-parsed online help for the command.
- _agent_report.json — full command list, device error feedback and safety notes.

## 1/1/5/1/6 and 1/1/5/1/6/1/1 (new)

Validated live on ONT 1/1/5/1/6 and UNI 1/1/5/1/6/1/1. All changes reverted to baseline.

What works (demonstrated):
- ONT: scheduler-node profile change (GPONShaperDN50Mbps ↔ GPONShaperDN600Mbps)
  - Evidence: `evidence/trials_ont_scheduler_node.txt`
- UNI: downstream `queue 0 weight` change (34 ↔ 36)
  - Evidence: `evidence/trials_uni_queue0_weight.txt`
- UNI: `upstream-queue 0 bandwidth-profile` change (GPONqpp100Mbps ↔ GPONqpp200Mbps)
  - Evidence: `evidence/trials_uni_upstream_queue0_profile.txt`
 - UNI: `queue-stats-on` toggle (absent ↔ present)
   - Evidence: `evidence/trials_uni_queue_stats_on_off.txt`
 - UNI: `upstream-queue 4 weight` change (5 ↔ 7)
  - Evidence: `evidence/trials_uni_upstream_queue4_weight.txt`
 - UNI: `upstream-queue 5 bandwidth-profile` change (GPONqpp100Mbps ↔ GPONqpp200Mbps)
  - Evidence: `evidence/trials_uni_upstream_queue5_profile.txt`

Not applicable on UNI (explicit device errors captured):
- ds-queue-sharing, us-queue-sharing, autoschedule, us-vlanport-queue
  - Evidence: `evidence/errors_uni_sharing_autoschedule_vlanport.txt`

Baselines:
- `evidence/baseline_ont_1-1-5-1-6.txt`
- `evidence/baseline_uni_1-1-5-1-6-1-1.txt`

Notes:
- Help text lists generic choices for some params (e.g., `bandwidth-sharing`), but live outputs show platform-specific values (e.g., `uni-sharing`). Live evidence takes precedence.

Next
- Map remaining applicable QoS parameters and add reversible trials where supported (e.g., additional upstream-queue weights/profiles), keeping safety constraints.