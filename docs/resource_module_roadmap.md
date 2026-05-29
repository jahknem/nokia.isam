# Resource Module Roadmap

This roadmap maps live `DS-LIN-TEST-01` command families and Nokia CLI PDF references to future Ansible resource modules.

The first implementation target for configuration modules is generally:

1. `gathered`
2. `parsed`
3. `rendered`
4. mutating states in `--check` mode only: `merged`, `replaced`, `overridden`, `deleted`

Status and management reads should be added to `isam_facts` as structured resources where possible, not mixed into desired-state config modules.

## Branching Model

Use one feature branch per module. `git worktree` is preferred over `git subtree` because these modules belong to the same collection and share common files.

Example layout:

```text
/home/jahknem/Projects/BlueNetworks/nokia.isam
/home/jahknem/Projects/BlueNetworks/nokia.isam.worktrees/isam-pon-interfaces
/home/jahknem/Projects/BlueNetworks/nokia.isam.worktrees/isam-ethernet-onts
/home/jahknem/Projects/BlueNetworks/nokia.isam.worktrees/isam-qos-interfaces
```

Each branch should create final-path files, not temporary `argspec_todo` files:

```text
plugins/modules/isam_<resource>.py
plugins/module_utils/network/isam/argspec/<resource>/<resource>.py
plugins/module_utils/network/isam/config/<resource>/<resource>.py
plugins/module_utils/network/isam/facts/<resource>/<resource>.py
plugins/module_utils/network/isam/rm_templates/<resource>.py
tests/unit/modules/network/isam/test_isam_<resource>.py
rm_models/<resource>.yaml
```

## First 10 Module Branches

| Priority | Branch | Module | Command families | Main PDF references | Type |
| --- | --- | --- | --- | --- | --- |
| 1 | `feature/isam-pon-interfaces` | `isam_pon_interfaces` | `configure pon interface` | `58_-_PonConfigurationCommands.pdf`, `202_-_PonManagementCommands.pdf` | config resource |
| 2 | `feature/isam-ethernet-onts` | `isam_ethernet_onts` | `configure ethernet ont` | `43_-_EthernetUserPortsConfigurationCommands.pdf`, `44_-_ONTEthernetPortConfigurationCommand.pdf`, `218_-_EthernetManagementCommands.pdf` | config resource |
| 3 | `feature/isam-equipment-onts` | `isam_equipment_onts` | `configure equipment ont` | `5_-_EquipmentConfigurationCommands.pdf`, `6_-_GponONTConfigurationCommands.pdf`, `214_-_EquipmentManagementCommands.pdf` | config resource |
| 4 | `feature/isam-qos-interfaces` | `isam_qos_interfaces` | `configure qos interface` | `21_-_QoSConfigurationCommands.pdf` | config resource |
| 5 | `feature/isam-qos-profiles` | `isam_qos_profiles` | `configure qos profiles` | `21_-_QoSConfigurationCommands.pdf` | config resource |
| 6 | `feature/isam-xdsl-lines` | `isam_xdsl_lines` | `configure xdsl line` | `35_-_XDSLBondingConfigurationCommands.pdf`, `37_-_SHDSLConfigurationCommands.pdf` | config resource |
| 7 | `feature/isam-xdsl-profiles` | `isam_xdsl_profiles` | `configure xdsl service-profile`, `spectrum-profile`, `dpbo-profile`, `vect-profile`, `vce-profile` | `35_-_XDSLBondingConfigurationCommands.pdf`, `37_-_SHDSLConfigurationCommands.pdf` | config resource |
| 8 | `feature/isam-link-agg` | `isam_link_agg` | `configure link-agg group`, `configure link-agg port` | `54_-_LACPConfigurationCommands.pdf` | config resource |
| 9 | `feature/isam-xstp` | `isam_xstp` | `configure xstp general`, `configure xstp port` | `55_-_MSTPConfigurationCommands.pdf`, `200_-_MSTPManagementCommands.pdf` | config resource |
| 10 | `feature/isam-equipment` | `isam_equipment` | `configure equipment shelf`, `slot`, `applique`, `protection-group` | `5_-_EquipmentConfigurationCommands.pdf`, `214_-_EquipmentManagementCommands.pdf` | config resource |

## Additional Config Resource Candidates

| Module | Command families | Notes |
| --- | --- | --- |
| `isam_alarm` | `configure alarm custom-profile`, `delta-log`, `entry`, `filter`, `log-sev-level` | Likely useful but lower provisioning priority. |
| `isam_traps` | `configure trap definition`, `trap manager` | Could be separate from alarm because identities and operations differ. |
| `isam_dhcp_server` | `configure dhcp-server` | Singleton config. |
| `isam_generic_pon` | `configure generic-pon` | Singleton/global PON config. |
| `isam_interface_cages` | `configure interface cage` | Could also be folded into interfaces if schema stays small. |
| `isam_interface_alarms` | `configure interface alarm` | Could also be folded into interfaces. |
| `isam_iphost` | `configure iphost` | Needs PDF review before module boundary is final. |
| `isam_li_vlan` | `configure li_vlan` | Small singleton or VLAN extension. |
| `isam_multicast` | `configure igmp`, `mcast`, `mcast-control` | Keep together unless schemas diverge. |
| `isam_ntp_onts` | `configure ntp ont` | ONT-specific management/config resource. |
| `isam_qos_maps` | `configure qos tc-map-dot1p`, `dscp-map-dot1p`, `up-ctrl-pkt`, `dn-ctrl-pkt` | Separate from interface bindings and profiles. |
| `isam_software_mngt` | `configure software-mngt` | High operational risk; implement late and carefully. |
| `isam_system` | `configure system id`, `security`, `sntp`, `sync-if-timing`, `syslog`, `transaction` | High risk/global; implement late. |
| `isam_vlan_global` | `configure vlan broadcast-frames`, `priority-regen`, `tpid`, `vmac-address-format` | Separate from per-VLAN `isam_vlans`. |
| `isam_voice_sip` | `configure voice sip` | Needs voice PDF review and careful schema design. |
| `isam_xdsl_bonding` | `configure xdsl-bonding` | Small but related to XDSL line/profile work. |

## Status And Management Data

Do not create desired-state resource modules for status-only data. Add these as structured `isam_facts` resources first.

Candidate `gather_network_resources` values:

```text
equipment_status
ont_status
pon_status
xdsl_status
alarm_status
software_status
link_agg_status
xstp_status
qos_status
system_status
```

Dedicated read-only `*_info` modules can be added later only for highly parameterized lookups where `isam_facts` becomes awkward.

## Module Boundary Rules

Use these rules when reading the PDFs and live command output:

| CLI shape | Module shape |
| --- | --- |
| `configure <family> <resource> <id> ...` | list resource keyed by `id`/`name` |
| `configure <family> <global-section> ...` | singleton dict or nested dict under one module |
| profile/template objects | list resource keyed by profile id/name |
| relationship/binding commands | nested list under the parent resource |
| status/show/management-only commands | `isam_facts` resource, not config module |

## Live MSAN Safety Rules

Feature branches may query `DS-LIN-TEST-01`, but only with read-only commands.

Allowed examples:

```text
info configure <family>
info configure <family> flat
info configure <family> detail
show <family>
```

Disallowed during discovery:

```text
configure
clear
admin
test
debug
```

Mutating resource states must be validated with Ansible `--check` first.
