# Resource Module Live-Validation Prompt (General)

This prompt is a reusable playbook for validating any CLI command subtree on a live Nokia ISAM device, generating authoritative examples for all Ansible-like states, and modeling the command in a resource module YAML. It captures device quirks, evidence, and safety guardrails.

## Inputs to set (fill these before running)
- COMMAND_PATH: e.g., `configure qos interface`
- TARGETS (safe to change): e.g., `ont:...`, `1/1/5/...`
- FORBIDDEN_PATHS (read-only): e.g., `1/1/5/1/15`
- MODULE_DIR: e.g., `rm_models/configure/qos/interface`
- MODULE_YAML: e.g., `isam_qos_interface.yml`

## Objectives
- Validate the full command tree for COMMAND_PATH using live help and info.
- Create single-command, live-captured examples for states: merged, replaced, overridden, deleted, gathered, rendered, parsed.
- Capture Before/After for any changes; revert to baseline.
- Update the module YAML to cover the entire tree (including nested stanzas).
- Record all operations and device feedback in `_agent_report.json` and document in `README.md`.

## Safety guardrails
- Only operate on TARGETS; treat FORBIDDEN_PATHS as read-only.
- Prefer minimal, reversible changes. After every change: verify with `info` then revert and re-verify.
- Capture explicit device errors for non-applicable/immutable parameters; treat them as facts.
- Include CLI prompts in transcripts; strip inventory banners where possible.

## Device quirks discovery (do this first)
- Run `help COMMAND_PATH` and save to `MODULE_DIR/help.txt`.
- Learn whether `info COMMAND_PATH` is global vs per-resource; use fully-qualified targets to narrow sections.
- Expect that some parameters can appear as `not-applicable`; treat that as authoritative.
- If a nested stanza has no direct help topic, rely on its presence/shape in `info`.

## Workflow
1) Help and baselines
- Save `help COMMAND_PATH` → `MODULE_DIR/help.txt`.
- For each TARGET, save `info COMMAND_PATH <target>` → `MODULE_DIR/evidence/baseline_<target>.txt`.

2) Systematic trials (per parameter)
- For every leaf in the command tree:
  - If boolean/toggle: enable → verify → disable → verify.
  - If enumerated/profile: change to a safe alternative → verify → revert → verify.
  - If numeric: nudge minimally within valid range → verify → revert → verify.
  - If rejected: capture exact device error text and do not retry.
- Save Before/After transcripts under `MODULE_DIR/evidence/trials_*`. Keep names descriptive (e.g., `trials_<param>_<target>.txt`).

3) States examples (single-command evidence)
- merged_example_01.txt: Change a single safe parameter (e.g., toggle on). Include Before/After snippets and the exact configure command.
- replaced_example_01.txt: Set multiple parameters for the same resource to demonstrate replacement semantics (without orphaning unrelated config).
- overridden_example_01.txt: Demonstrate a full override for the resource subtree (limit to safe parameters). Show that unspecified items are removed/disabled.
- deleted_example_01.txt: Demonstrate removing a previously set parameter or child stanza safely; include the `no ...` command and After state.
- gathered_example_01.txt: Capture `info COMMAND_PATH` (global and/or per-target) with minimal noise.
- rendered_example_01.txt: Show the CLI that would be generated for a given structured config (no device change). If tooling generates this, paste the rendered lines.
- parsed.json: Parse the help and/or info into structured fields (names, choices, ranges). This backs the YAML schema.

4) Update module YAML (MODULE_YAML)
- Cover every top-level and nested node from the command tree.
- Keep schema shape consistent:
  - `options.config` (list of dicts), each with `name` (resource identifier) and parameters.
  - Nested stanzas modeled as lists (e.g., `queue`, `upstream_queue`, `ds_rem_queue`) with `id` and suboptions.
- Add defaults, choices, ranges based on help; annotate platform-specific behavior from live outputs (e.g., values printed by `info`).
- Add short applicability notes for parameters that errored on this platform (immutable/not-applicable).

5) Update _agent_report.json
- verified_commands_run: every `help`, `info`, `configure`, and revert command executed.
- attempt_results: per attempt
  - command, result (success/error and exact text), note (context), and whether reverted.
- safety: a one-liner summarizing change scope and forbidden areas respected.

6) Update README.md (in MODULE_DIR)
- Summarize: what works, what’s not applicable, and quirks observed.
- Link to all evidence files under `evidence/`.
- Point to states examples and parsed.json.

## Evidence naming conventions
- Baseline: `evidence/baseline_<target>.txt`
- Trials: `evidence/trials_<param>_<target>.txt`
- Errors: `evidence/errors_<topic>.txt`
- States: `merged|replaced|overridden|deleted_example_01.txt`, `gathered_example_01.txt`, `rendered_example_01.txt`, `parsed.json`

## Success criteria
- Schema covers the full CLI tree (top-level and nested). No missing nodes.
- Every change example is reversible and has Before/After proof.
- `_agent_report.json` is an exact ledger of actions and outcomes.
- README captures applicability and quirks; evidence files are linked.
- No changes made under FORBIDDEN_PATHS.

## Generic example templates (replace placeholders before use)
- Toggle:
  - set: `COMMAND_PATH <target> <flag>`
  - unset: `COMMAND_PATH <target> no <flag>`
  - verify: `info COMMAND_PATH <target>`
- Numeric nudge:
  - set: `COMMAND_PATH <target> <param> <new_value>`
  - revert: `COMMAND_PATH <target> <param> <baseline>`
  - verify: `info COMMAND_PATH <target>`
- Profile change:
  - set: `COMMAND_PATH <target> <param> name:<profile_b>`
  - revert: `COMMAND_PATH <target> <param> name:<profile_a>`
  - verify: `info COMMAND_PATH <target>`

---

## Appendix A: Notes for Nokia ISAM 6.2.04ng (example)
- `info` may be global; prefer per-resource `info COMMAND_PATH <index>` to scope output.
- Some UNI parameters error with explicit codes (e.g., 46, 96, 116); record them.
- Nested stanzas (like `upstream-queue`) may appear in `info` though lacking separate help topics.
- Values printed by `info` can be platform-specific (e.g., `bandwidth-sharing uni-sharing` in a nested block); annotate the YAML accordingly.
