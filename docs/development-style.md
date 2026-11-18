# Development style for resource modules

Every resource module follows the netcommon resource module layout known from other
network collections (cisco.ios, arista.eos, ...). Only two steps are ISAM specific:
packed device lines are split for reading, and per-attribute commands are packed
again for writing. Reference implementation: `isam_ethernet_line`.

Existing modules move to this style when they are changed; modules that already work
this way are left alone.

## Layout

```
plugins/modules/isam_<family>.py                 documentation and entry point
module_utils/network/isam/argspec/<family>/      argument spec (no defaults for config options)
module_utils/network/isam/facts/<family>/        read: device text -> facts
module_utils/network/isam/rm_templates/<family>  parsers: one entry per attribute
module_utils/network/isam/config/<family>/       write: compare want with have -> commands
```

## Facts

Read the `flat` form (`info configure <node> flat`; targeted reads per instance with
`get_targeted_config`). The device prints all attributes of a node on one line:

```
configure ethernet line 1/1/6/1 mau 1 type 100basebx10d power down no autonegotiate
```

Split such lines into one attribute per line with `iter_cli_fields`, using the keyword
tuples of the template, then parse with the template:

```
configure ethernet line 1/1/6/1 mau 1 type 100basebx10d
configure ethernet line 1/1/6/1 mau 1 power down
configure ethernet line 1/1/6/1 mau 1 no autonegotiate
```

## Template

A `NetworkTemplate` with `PARSERS` in the netcommon format (`name`, `getval`, `setval`,
`remval`, `result`, `compval`), one entry per attribute. When a node has several
attributes of the same kind, small factory functions in the same file create the
entries from keyword tuples:

```python
TCA_THRESHOLDS = ("los", "fcs", ...)        # value: "<kw> <n>", reset "no <kw>"
MAU_FLAGS = ("speed-auto-sense", ...)       # flag: "<kw>" / "no <kw>"
TCA_PARSERS = [_value("tca_line_threshold." + _key(kw), ...) for kw in TCA_THRESHOLDS]
```

The keyword tuples are the single place where the CLI grammar of a node lives; the
facts split with them and the parsers are made from them. An attribute without a `no`
form gets `no_remval: True` instead of a `remval`.

No own parse or render functions.

## Config

`ResourceModule` with the standard flow:

- `merged`: want merged onto have (lists of entries by their key), then
  `compare(parsers=...)`.
- `replaced`: `compare` against want; unnamed attributes return to the device default.
- `overridden`: as replaced, and instances not in want are reset.
- `deleted`: without config every instance; with config the named instances, and
  within an instance only the named attributes (an identity alone means all).
- `rendered`/`parsed`: no device; `rendered` renders exactly what is given.

Device defaults live in one dict per node in the config class. Values equal to the
default are removed from want and have before `compare`, so a default counts as unset
(the device omits it in `flat` and prints `no <kw>` in `detail`). Attributes without a
`no` form are kept when a request does not name them.

`COMPACT_COMMAND_SCOPES` packs the per-attribute commands of one node into one
command, the form the device prints.

Code beyond this is only for device rules, each with a short comment naming the
device evidence, for example:

```python
# A board has no removal command ("configure xdsl no board" is an invalid token,
# lab ISAM); deleted resets its attributes instead.
```

Typical rules: ordering between nodes (an ONT slot before its ONT), attributes the
device only accepts at creation (fail early with a clear message), objects without a
removal command (reset their attributes), values the device shows for unset
(`none`, `not-applicable`).

## Tests

Per module the standard states (`merged`, `replaced`, `overridden`, `deleted`,
`rendered`, `parsed`, `gathered`) and idempotence. Device behaviour is pinned with
fixtures from live captures (`tests/fixtures/`, see AGENTS.md): device text in, the
commands the device accepted out. A test that expects a command the device refuses is
a bug in the test.
