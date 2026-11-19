# Development style for resource modules

The collection follows the netcommon resource module layout known from other network
collections (cisco.ios, arista.eos, ...). What has to be uniform is the structure and
the behaviour of the states; how a template is written may differ where the grammar
differs. Choose the simplest form that fits.

## Layout

```
plugins/modules/isam_<family>.py                 documentation and entry point
module_utils/network/isam/argspec/<family>/      argument spec
module_utils/network/isam/facts/<family>/        read: device text -> facts
module_utils/network/isam/rm_templates/<family>  parsers
module_utils/network/isam/config/<family>/       write: want + have -> commands
module_utils/network/isam/resource_module.py     IsamResourceModule (base of every config class)
module_utils/network/isam/action_module.py       IsamActionModule (base of operational action modules)
module_utils/network/isam/common.py              shared helpers (parsing, state semantics)
```

Every config class derives from `IsamResourceModule`. It adds the ISAM CLI rules to
netcommon's `ResourceModule`: removal forms (`remval`, `no_remval`, `read_only`),
explicit `False` in `rendered`, and packing commands per node
(`COMPACT_COMMAND_SCOPES`). Nothing patches netcommon.

## State semantics (the same in every family)

| State | Behaviour |
|---|---|
| `merged` | Sets what is given; leaves everything else. Lists of entries merge by identity. |
| `replaced` | The named instances end up exactly as given; unnamed attributes return to the device default. |
| `overridden` | As replaced, and instances not given are reset or removed. |
| `deleted` | Without config: every instance. With config: the named instances; an identity alone resets/removes the instance, named attributes reset only themselves. With a dict config only the named sections are touched (`requested_sections`). |
| `rendered` | Renders exactly what is given, an explicit `False` as its `no` form. No device. |
| `parsed`, `gathered` | Facts; unset/default values are not reported. |

Shared helpers implement these rules; use them instead of local variants:
`deleted_targets` (what an instance keeps on `deleted`), `covers_entry` (whether a
removable object is removed as a whole), `requested_sections`.

A value equal to the device default counts as unset when comparing (the device omits
it in `flat` and prints `no <kw>` in `detail`). Attributes without a `no` form are
kept when a request does not name them (`no_remval`, warning on reset).

Device defaults are reconciliation knowledge (one dict per node in the config class or
in the template's attribute table), not argspec defaults: an argspec default would be
injected into every request and overwrite what the user did not name. Argspec defaults
are fine for module controls such as `state`.

## Templates

A `NetworkTemplate`. Pick per node:

- **Explicit `PARSERS` entries** (netcommon format: `name`, `getval`, `setval`,
  `remval`, `result`, `compval`) for small or irregular grammars. Familiar and easy to
  inspect.
- **Small factory functions** generating such entries from one attribute table when a
  node has many attributes of the same kind (flags, values, thresholds). Reference:
  `isam_vlans` -- `VLAN_ATTRS` (option, CLI keyword, kind, device default) generates the
  parsers, drives the facts' line splitting and holds the defaults; options are
  snake_case with the CLI spelling as alias; a test keeps table, argspec and
  documentation in step, and parse -> render reproduces the device's lines.
  `rm_templates/ethernet_line.py` follows the same idea for a node with sub-nodes.
- **`SettingsBlockTemplate`** for singleton settings nodes whose attributes are all
  `[no] <kw> <value>` with known defaults (`nat`, `error`, `cwmp_plt`, ...): one table
  `(option, keyword, kind, default)`.

The device prints all attributes of a node on one line. Facts split such lines into
one attribute per line (`iter_cli_fields`) where per-attribute parsers read them.

## Config classes

Use `compare(parsers=...)` where its field comparison fits, and explicit code where it
is clearer. Code beyond the state semantics is for device rules only, each with a short
comment naming the device evidence, for example:

```python
# A board has no removal command ("configure xdsl no board" is an invalid token,
# lab ISAM); deleted resets its attributes instead.
```

Typical device rules: ordering between nodes (an ONT slot before its ONT), attributes
accepted only at creation (fail early with a clear message), objects without a removal
command (reset their attributes), values shown for unset (`none`, `not-applicable`).

Compare typed values (ints as ints); do not paper over type differences with `str()`.

## Action modules (operational commands)

Some device commands are one-shot **operations**, not persistent configuration: clearing
counters, rebooting an ONT or linecard, triggering a line test, a protection switchover,
a diagnostic ping. These are usually `admin ...` commands. They get an **action module**
on `IsamActionModule` (`module_utils/network/isam/action_module.py`), not on
`IsamResourceModule`. Reference: `isam_security_ext_authenticator`.

Three things that are easy to confuse:

- An **Ansible action plugin** (`plugins/action/`) is a controller-side execution helper;
  it does not implement device operations. `IsamActionModule` is *not* one of these.
- A **resource module** manages declarative persistent configuration with the states
  above and idempotence.
- An **action module** writes to the device but performs an event: no resource states, no
  facts to gather, not idempotent. `changed` means "an operation was sent".

The base keeps only the execution mechanics (check mode, sending, collecting responses,
propagating failures). Device behaviour belongs to the module:

- `build_commands` must require an **explicit operation**. A bare resource identifier
  without an operation only navigates the ISAM admin hierarchy (CLI guide, global
  commands) and is not an action -- reject it, do not report a change.
- `verify` (optional) checks completion from the responses; override it for operations
  needing a confirmation, a reconnect or a follow-up read. Never assume success just
  because a command was sent.

Not every `admin` command is a stateless one-shot (e.g. an Ethernet loopback is temporary
operational state), and some `configure` commands execute actions (e.g. `configure
linetest single ltsession ... session-cmd create|destroy`). Model those by what they do,
not by their verb. The cliconf resets the CLI context (`exit all`) before both `configure`
and `admin` commands, since both are absolute paths from the root.

## Tests

- Per module: the states above, idempotence, sibling preservation.
- Contract tests across families (`test_deleted_regressions.py`): named-field
  deletion, explicit `False` in `rendered`, empty `gathered` matching the config type.
- Device behaviour from live captures (`tests/fixtures/`, see AGENTS.md); write
  scenarios in `tests/fixtures/live_scenarios/` replay accepted commands offline.
  A test expecting a command the device refuses is a bug in the test.

Existing modules move to this when they are changed; behaviour must stay as pinned by
their tests and scenarios.
