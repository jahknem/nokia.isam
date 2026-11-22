# Ansible Nokia ISAM FTTN 7330 Collection

This collection is a fork of https://github.com/Qalthos/linkybook.utils which describes the skeleton of a network device collection. It also uses https://github.com/ansible-network/cli_rm_builder to scaffold the resource module folders and boiler code.

This Ansible Collection contains modules to manage Nokia ISAM FTTN 7330 devices. The Nokia ISAM FTTN Line-up is of the Device Type MSAN. Most of the options available are for different types of OSI Layer 2 protocols. As such it is very different from other Ansible Network Collections which are specialised on routers and switches. This repository is under active development and not yet ready for production use! It is not supported by nor affiliated to Nokia in any way! Use at your own risk!

## Available Modules

**1.0 upgrade preparation:** this branch includes intentional schema changes from
0.3.14. Read [Upgrading to 1.0](docs/upgrade-1.0.0.md) before changing inventories,
playbooks or fact consumers. The 1.0 tag/artifact has not been published yet.

For copying ONT configurations, full-entry deletion and check-mode limitations,
see [ONT configuration change sets](docs/ont-change-sets.md).

### Config Resource Modules
| Module | Command Families | States |
| --- | --- | --- |
| `isam_interfaces` | `configure interface port` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_bridges` | `configure bridge` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_ethernet_line` | `configure ethernet line` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_vlans` | `configure vlan id` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_pon_interfaces` | `configure pon interface` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_ethernet_onts` | `configure ethernet ont` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_equipment_onts` | `configure equipment ont` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_qos_interfaces` | `configure qos interface` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_qos_profiles` | `configure qos profiles` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_xdsl_lines` | `configure xdsl line` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_xdsl_profiles` | `configure xdsl` profiles | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_link_agg` | `configure link-agg` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_xstp` | `configure xstp` | gathered, parsed, rendered, merged, replaced, overridden, deleted |
| `isam_equipment` | `configure equipment` (shelf, slot, applique, protection-group) | gathered, parsed, rendered, merged, replaced, overridden, deleted |

All configuration resource modules support **targeted gathering**: with
`state: gathered` and `config` naming instances, only those instances are
read from the device, one scoped read per instance. Each addressed instance
is reported in `read_outcomes`, per config section and selector, as
`present`, `confirmed_absent` (the device's explicit "instance does not
exist" signal about that instance, aggregated only when every read of the
instance confirmed it) or `unknown` (header-only reply, `invalid token`
rejection, a missing dependency, or a failed read — never absence). The
outcomes are sanitized to stable enums, the section, the selector, and an
error class; raw device text is never recorded. An explicit request that
cannot be read in full (an empty identity, no read command) fails rather
than silently widening to the whole-family read or serving a subset. Without
`config` the whole resource is read, as before, and write states are
unchanged. Two families (`isam_interface_alarms`, `isam_vlan_global`) have no
single-instance read on the device: their targeted request reads the whole
node once and reports each named instance from the parsed catalog, with
`gathered` staying the full catalog — the documented exception to the
scoped-read contract. See [targeted gathering and
read outcomes](docs/targeted-gathering.md).

### Facts Module
| Module | Description |
| --- | --- |
| `isam_facts` | Collects facts and structured network resources from all registered modules |

The major-version line adds an opt-in lossless tree of the captured flat root:

```yaml
- name: Inspect the root configuration tree without applying changes
  nokia.isam.isam_facts:
    gather_subset:
      - "!all"
      - config_tree
```

`config_tree_detail: true` includes device defaults. Root-tree diagnostics are not
a configuration replay format, and unknown syntax can defeat heuristic redaction;
review diagnostic output privately before sharing it.

**Capture boundary:** on evidenced firmware, `info configure [detail] flat`
omits IHUB ports, LAGs and services. Lossless parsing does not make that source a
whole-device configuration capture. `ansible_net_config_tree_source` exposes
these known omissions. The hierarchical `info configure` source includes IHUB.

The tree uses only declared grammar/resource paths: unknown paths are retained
under `__unclassified__`, and unknown attribute tails are reported as `unparsed`,
not guessed into nodes or fields. Check those gaps before claiming coverage.

### Read-only IHUB configuration resources (experimental)

| Module | Verified source | Actual read scope |
| --- | --- | --- |
| `isam_ihub_ports` | `info configure`, Port Configuration section | device |
| `isam_ihub_lags` | `info configure`, LAG Configuration section | device |
| `isam_ihub_services` | `info configure service` | family |

These modules support **`gathered` and `parsed` only**, not mutation or rendering.
They return canonical resources `ihub_ports`, `ihub_lags`, `ihub_services` and
projection coverage. Unknown options/types remain coverage gaps; this is not
exhaustive IHUB support. Ports include internal and virtual ports as well as
optical positions. IHUB LAGs are not access-side `link-agg` groups, and service
SAPs are not access-side bridge/VLAN-port layers.

```yaml
- name: Read IHUB ports through their verified device-wide source
  nokia.isam.isam_ihub_ports:
    state: gathered
    allow_broad_read: true

- name: Explicitly read the whole IHUB service family
  nokia.isam.isam_ihub_services:
    state: gathered
```

The device-wide port/LAG sources require explicit `allow_broad_read: true`.
Instance selections in `config` also require that flag: they filter a whole
source, **not** a scoped CLI read. Without selections, explicitly requesting the
service family already selects that family-wide scope and needs no extra flag.
The modules are not implicitly added to `isam_facts: all` or shared-flat parsing;
existing read breadth is unchanged. See [IHUB configuration](docs/ihub-configuration.md).

### Semantic object graph

The **public** filters `isam_topology` and `isam_topology_read_requirements`
build and query the [semantic object graph](docs/resource-topology.md) from
already-gathered resources: they relate physical descendants, resource
instances and shared-profile references across CLI branches, entirely offline.
They reuse the collection's targeted-read identities, and
`isam_topology_read_requirements` reports what reads a recursive refresh would
need — including its gaps. **Executable recursive refresh is not part of that
contract**: the filters are stable for offline planning, while running a
planned refresh against a device remains experimental and uncertified.
`isam_topology_discovery` performs one read-only direct-neighbor enumeration at a
time; whole-source reads require explicit `allow_broad_read: true`, and an
unsupported or failed enumeration is never reported as an empty child list.

Additional resource modules cover system security, QoS global/TCA settings,
CWMP, error logging, NAT, PON global settings, PPPoX global sessions, PON
troubleshooting, xDSL INM/ONT/system settings and L2UNI/UNI ONTs. Consult
`ansible-doc nokia.isam.<module>` for their complete option/state contracts and
the [live-test matrix](docs/live-test-matrix.md) for verification limits.

### Operational Action Modules

| Module | Explicit operation |
| --- | --- |
| `isam_security_ext_authenticator` | `clear_statistics` |
| `isam_ethernet_statistics` | `clear_stats` |
| `isam_dhcp_relay_port_stats` | `clear_statistics` |
| `isam_bridge_learned_mac` | `delete` |

Actions are one-shot events, not desired-state convergence. Check mode reports
commands without connecting; it does not authorize execution. On partial or
verification failure, inspect accepted/completed/failed_command/pending command context
and do not blindly retry operations with an unknown outcome.

The facts module also provides opt-in shared configuration gathering. It reads
the access-side flat configuration with one `info configure flat` request and
passes that response to each selected resource parser:

```yaml
- name: Read once and reuse for multiple resource parsers
  nokia.isam.isam_facts:
    gather_configuration: true
    gather_network_resources:
      - interfaces
      - pon_interfaces
      - equipment_onts
```

The result contains the normal resource structures under
`ansible_facts.ansible_network_resources`. The bulk result schema is in
`docs/schemas/isam_facts_resources.json`.

Operational subsets are gathered separately through `gather_subset` and are
returned as `ansible_net_*` facts:

```yaml
- name: Gather DHCP relay operational information
  nokia.isam.isam_facts:
    gather_subset:
      - "!all"
      - dhcp_relay
```

Available operational subsets include `active_alarms`, `dhcp_relay`,
`equipment_status`, `interface_status`, `ont_status`,
`ont_ranging_status`, `ont_software_status`, `pon_pm_status`, `pon_status`,
and `software_status`.

### CLI Modules
| Module | Description |
| --- | --- |
| `cli_config` | Apply text configuration |

`nokia.isam.cli_config` supports text configuration only. Replace-file and
rollback operations are not exposed by the ISAM cliconf plugin.

```yaml
- name: Apply configuration text
  nokia.isam.cli_config:
    config: "configure system id name access-node"

```

## Roadmap

The detailed live command tree and resource roadmap are documented in:

* `docs/command_tree.md`
* `docs/resource_module_roadmap.md`
* `docs/ssh-session-failure-analysis.md`

### Current Status

All resource modules listed in the roadmap are present. Mutating states are
validated offline and in check mode only unless explicitly listed as live
validated. The collection is not production-ready for unrestricted mutation;
review each module's CLI coverage and live evidence before use.

| # | Module | Command Families | States |
| --- | --- | --- | --- |
| 1 | `isam_pon_interfaces` | `configure pon interface` | state coverage documented in the roadmap |
| 2 | `isam_ethernet_onts` | `configure ethernet ont` | state coverage documented in the roadmap |
| 3 | `isam_equipment_onts` | `configure equipment ont` | state coverage documented in the roadmap |
| 4 | `isam_qos_interfaces` | `configure qos interface` | state coverage documented in the roadmap |
| 5 | `isam_qos_profiles` | `configure qos profiles` | state coverage documented in the roadmap |
| 6 | `isam_xdsl_lines` | `configure xdsl line` | state coverage documented in the roadmap |
| 7 | `isam_xdsl_profiles` | `configure xdsl profiles` | state coverage documented in the roadmap |
| 8 | `isam_link_agg` | `configure link-agg` | state coverage documented in the roadmap |
| 9 | `isam_xstp` | `configure xstp` | state coverage documented in the roadmap |
| 10 | `isam_equipment` | `configure equipment` (shelf/slot/applique/protection-group) | state coverage documented in the roadmap |

Status and management data should generally be added as structured `isam_facts` resources before introducing dedicated read-only info modules.

`isam_security_ext_authenticator` is action-only: it requires `config` and
executes the documented `admin security ext-authenticator` command. It does
not expose resource states because the command is not persistent configuration.

Operational facts now use `gather_subset` and return `ansible_net_*` names.
This is a breaking change from the former legacy resource-facts shape; see
`docs/migration-0.3.md`.

## Requirements & Installation

### Requirements
* Ansible 2.15 or higher
* `ansible.netcommon` 8.6.1 through 8.x
* Python 3.10 or higher
* Nokia ISAM FTTN 7330 device running ISAM Release R6.2.04m or higher

### Installation
Install the collection from Github:
```
git clone https://github.com/jahknem/nokia.isam.git
cd nokia.isam
pip3 install -r requirements.txt
ansible-galaxy collection build
ansible-galaxy collection install nokia-isam-*.tar.gz
```

### Usage

To use this collection the following needs to be added to the inventory:
```
ansible_connection: ansible.netcommon.network_cli
ansible_network_os: nokia.isam.isam
```

When using `gather_facts: true`, Ansible's default `smart` resolver does not automatically map `nokia.isam.isam` to this collection's facts module.

Add this to `ansible.cfg`:
```ini
[defaults]
facts_modules = smart, nokia.isam.isam_facts
```

Or set it in inventory/group vars:
```yaml
ansible_facts_modules:
  - smart
  - nokia.isam.isam_facts
```

You can always run facts explicitly as a task:
```yaml
- name: Gather ISAM facts
  nokia.isam.isam_facts:
```

Some modules take a long time to complete due to the slow nature of the device. To increase the timeout for these modules the following can be added to the inventory:
```
ansible_command_timeout : 150
```
150 Seconds should be enough to complete a transmission of the complete configuration. As such it should also be enough for most other commands.

ISAM can reject a successfully authenticated SSH connection before presenting
the CLI prompt with `Max. Sessions Reached.`. Use the optional ISAM connection
wrapper and configure its bounded exponential backoff:

```yaml
ansible_connection: nokia.isam.isam_network_cli
ansible_isam_connect_retries: 3
```

The default is `0`, so ISAM-specific retries are disabled unless requested.
Delays are 2, 4, and 8 seconds. Authentication and command failures are never
replayed. TCP, banner, and key-exchange retries remain controlled separately by
Ansible's standard `ansible_network_cli_retries` option. If the device is known
to report transient authentication failures under overload, those can be
included explicitly with `ansible_isam_retry_authentication: true`; this is off
by default to avoid retrying bad credentials or increasing account-lockout risk.

The separate `nokia.isam.isam_network_cli` connection is intentional and
unusual. Most network collections use `ansible.netcommon.network_cli` directly.
ISAM can accept SSH authentication and then reject `invoke_shell()` with
`Max. Sessions Reached.`; Paramiko exposes that as an empty `EOFError`, which
the standard `network_cli` retry loop does not handle. The wrapper resets the
private failed transport and retries only connection establishment. It does
not replay commands. This workaround can be removed if a future
`ansible.netcommon` release handles this lifecycle upstream.

## Development

[This](https://docs.ansible.com/ansible/latest/network/dev_guide/developing_resource_modules_network.html) is a starting point.

Step 1) Create a resource module model
Step 2) Scaffold it with [resource_module_builder](https://github.com/ansible-network/resource_module_builder) or [cli_rm_builder](https://github.com/ansible-network/cli_rm_builder)

### Testing

```bash
make setup        # Set up local collection symlink
make compile      # Python syntax check
make test         # Run unit tests
make lint         # Run flake8 and ansible-lint
make doc          # Verify ansible-doc for all modules
make gather-all   # Live gathered state validation against target device
```

Or with tox:
```bash
tox               # Run tests
tox -e lint       # Run linting
```

### Branching Model

Use `git worktree` per feature branch. Each branch creates files in final paths:

```text
plugins/modules/isam_<resource>.py
plugins/module_utils/network/isam/argspec/<resource>/<resource>.py
plugins/module_utils/network/isam/config/<resource>/<resource>.py
plugins/module_utils/network/isam/facts/<resource>/<resource>.py
plugins/module_utils/network/isam/rm_templates/<resource>.py
tests/unit/modules/network/isam/test_isam_<resource>.py
```
