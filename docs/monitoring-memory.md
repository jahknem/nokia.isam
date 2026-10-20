# Memory-bounded operational monitoring

The operational parsing filters are available in **0.3.9**. Pin this release in
the collection requirements and execution environment used by the playbooks.

## Lightweight parsers

- `nokia.isam.parse_unprovisioned_onts`: complete output from
  `show pon unprovision-onu` → rows with snake-case column names. Fixed-width
  blank cells stay blank; they cannot shift subsequent values into the wrong
  field. Incomplete tables fail rather than silently clearing old metrics.
- `nokia.isam.parse_xdsl_operational_lines`: complete output from
  `show xdsl operational-data line` → `if_index`, `adm_state`, `opr_state`,
  `cur_op_mode`, `us_rate`, `ds_rate`. ISAM's stacked state/rate column and the
  header spanning both rate columns are parsed using the separator boundaries.
  Blank/unknown rates return null; numeric zero remains zero. Configuration
  facts (`xdsl_lines`) are not a substitute for these operational statistics.
Prometheus label quoting belongs to the consuming monitoring project, not this
vendor collection. The collection filters return device data only.

All filters are controller-local and read-only; they issue no SSH or HTTP calls.
The parsers require the reported row count to match the parsed rows. There is no
full configuration read, facts-cache population, or Prometheus client dependency.

The shared table parser now lives in `plugins/module_utils/tables.py`. Existing
facts import locations re-export the same function, preserving their API. The
new filters deliberately import outside `network/isam/__init__.py`, so a parser
import does not activate ResourceModule compatibility hooks or import the broad
resource-facts dispatcher. A fresh-process regression test enforces this.

## Playbook execution pattern

1. Disable automatic smart fact gathering when it is not used.
2. Process a bounded host batch with `serial`; a global fork cap alone does not
   bound the number of persistent helpers left by completed hosts.
3. Group necessary SSH reads in a block. Its `always` section uses standard
   `meta: reset_connection`, including for excluded hosts and failures. Do not
   put `end_host` before connection cleanup.
4. Render the metric body once with a collection parser, rather than retaining
   raw output, a parsed dictionary, and a second metrics string as host facts.
5. Delegate HTTP publication explicitly to localhost using its Python and a
   writable temporary directory. Do not inherit a network device's root home.
6. Replace a complete Pushgateway group with one PUT instead of DELETE then POST.
   Rendering/parse errors occur before that request, preserving the last good
   group. Empty results remove stale application samples but leave Pushgateway's
   built-in group health/timestamp series; this differs from deleting the group.
7. Clear registered CLI output in an outer `always` section before the next batch.

This reduces task barriers, helper lifetime and data duplication. It does not
change device configuration, disable error reporting, invent missing rate values,
or introduce a custom SSH transport.

## Validation boundaries

Use sanitized fixtures and test the full `tests/unit` tree through tox. For local
integration tests, use the same EE baseline, inventory, CPU/memory caps and a
fresh connection directory per run. Send publications to a **disposable local
Pushgateway**, never to production while validating parser changes. Compare the
actual accepted metric names, grouping labels and values against the captured
CLI output, including empty groups and parse-error behavior.

Record whole-cgroup `memory.peak` and OOM events, not summed process RSS (which
double-counts shared pages). Only compare runs that complete the same host scope;
an early failing run is not a successful memory optimization.

## Local measured outcome (20 October 2026)

The optimized playbooks completed all 111 target hosts. A controlled ONT comparison
using the same local Pushgateway and CPU/memory caps reduced peak memory from
**5.578 to 2.925 GiB** and runtime from **190.19 to 102.34 s**. The optimized run
kept global forks at 100; the playbook itself bounded host batches to 25.
The final xDSL run completed in **100 s**, peaking at **2.301 GiB**, and published
**23,616 validated metric samples from 5,904 line records**.

These improvements are the combined playbook/session-lifetime changes, not a
claim that parser micro-optimizations alone account for gigabytes of savings.
The collection unit suite (790 tests plus 2 subtests), lint, type checking and
documentation checks passed; EE playbook/HTTP regression tests also passed.
Production was not upgraded or synchronized as part of these local experiments.
