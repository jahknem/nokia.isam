# Ansible Nokia ISAM FTTN 7330 Collection

This collection is a fork of https://github.com/Qalthos/linkybook.utils which describes the skeleton of a network device collection. It also uses https://github.com/ansible-network/cli_rm_builder to scaffold the resource module folders and boiler code.

This Ansible Collection contains modules to manage Nokia ISAM FTTN 7330 devices. The Nokia ISAM FTTN Line-up is of the Device Type MSAN. Most of the options available are for different types of OSI Layer 2 protocols. As such it is very different from other Ansible Network Collections which are specialised on routers and switches. This repository is under active development and not yet ready for production use! It is not supported by nor affiliated to Nokia in any way! Use at your own risk!

## Available Modules

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

### Facts Module
| Module | Description |
| --- | --- |
| `isam_facts` | Collects facts and structured network resources from all registered modules |

### Legacy Modules
| Module | Description |
| --- | --- |
| `cli_command` | Run CLI commands on remote devices |
| `cli_config` | Manage CLI configuration on remote devices |

## Roadmap

The detailed live command tree and resource roadmap are documented in:

* `docs/command_tree.md`
* `docs/resource_module_roadmap.md`

### Implemented Modules (Merged to main)

All 10 first-priority resource modules plus 5 legacy modules are implemented and in `main`:

| # | Module | Command Families | States |
| --- | --- | --- | --- |
| 1 | `isam_pon_interfaces` | `configure pon interface` | all 7 canonical states |
| 2 | `isam_ethernet_onts` | `configure ethernet ont` | all 7 canonical states |
| 3 | `isam_equipment_onts` | `configure equipment ont` | all 7 canonical states |
| 4 | `isam_qos_interfaces` | `configure qos interface` | all 7 canonical states |
| 5 | `isam_qos_profiles` | `configure qos profiles` | all 7 canonical states |
| 6 | `isam_xdsl_lines` | `configure xdsl line` | all 7 canonical states |
| 7 | `isam_xdsl_profiles` | `configure xdsl profiles` | all 7 canonical states |
| 8 | `isam_link_agg` | `configure link-agg` | all 7 canonical states |
| 9 | `isam_xstp` | `configure xstp` | all 7 canonical states |
| 10 | `isam_equipment` | `configure equipment` (shelf/slot/applique/protection-group) | all 7 canonical states |

### Next Roadmap Modules

| Priority | Module | Command Families | Live Commands |
| --- | --- | --- | --- |
| 11 | `isam_alarm` | `configure alarm` (filter, entry, custom-profile, delta-log, log-sev-level) | 66 |
| 12 | `isam_traps` | `configure trap` (definition, manager) | 34 |
| 13 | `isam_interface_cages` | `configure interface cage` | 64 |
| 14 | `isam_ntp_onts` | `configure ntp ont` | 48 |
| 15 | `isam_qos_maps` | `configure qos tc-map-dot1p`, `dscp-map-dot1p`, `up-ctrl-pkt`, `dn-ctrl-pkt` | 89 |
| 16 | `isam_system` | `configure system` (security, sntp, sync-if-timing, syslog, id, transaction) | 63 |
| 17 | `isam_vlan_global` | `configure vlan` (broadcast-frames, priority-regen, tpid, vmac-address-format) | 14 |
| 18 | `isam_voice_sip` | `configure voice sip` | 5 |
| 19 | `isam_xdsl_bonding` | `configure xdsl-bonding` | 1 |
| 20 | `isam_dhcp_server` | `configure dhcp-server` | 1 |
| 21+ | More | See `docs/resource_module_roadmap.md` | - |

Status and management data should generally be added as structured `isam_facts` resources before introducing dedicated read-only info modules.

## Requirements & Installation

### Requirements
* Ansible 2.15 or higher
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
