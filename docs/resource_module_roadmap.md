# Resource Module Roadmap

This roadmap maps live `DS-LIN-TEST-01` command families and Nokia CLI PDF references to Ansible resource modules.

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
```

Each branch should create final-path files, not temporary `argspec_todo` files:

```text
plugins/modules/isam_<resource>.py
plugins/module_utils/network/isam/argspec/<resource>/<resource>.py
plugins/module_utils/network/isam/config/<resource>/<resource>.py
plugins/module_utils/network/isam/facts/<resource>/<resource>.py
plugins/module_utils/network/isam/rm_templates/<resource>.py
tests/unit/modules/network/isam/test_isam_<resource>.py
```

## Completed Modules (Merged to main)

All 10 first-priority resource modules are implemented, validated against `DS-LIN-TEST-01`, and merged to `main`.

| Priority | Module | Command families | Live Commands | States Validated |
| --- | --- | --- | --- | --- |
| 1 | `isam_pon_interfaces` | `configure pon interface` | 129 | gathered, rendered, parsed, merged/--check, replaced/--check, overridden/--check, deleted/--check |
| 2 | `isam_ethernet_onts` | `configure ethernet ont` | 88 | same |
| 3 | `isam_equipment_onts` | `configure equipment ont` | 146 | same |
| 4 | `isam_qos_interfaces` | `configure qos interface` | 1394 | same |
| 5 | `isam_qos_profiles` | `configure qos profiles` | 137 | same |
| 6 | `isam_xdsl_lines` | `configure xdsl line` | 96 | same |
| 7 | `isam_xdsl_profiles` | `configure xdsl` profiles | 82 | same |
| 8 | `isam_link_agg` | `configure link-agg` | 108 | same |
| 9 | `isam_xstp` | `configure xstp` | 37 | same |
| 10 | `isam_equipment` | `configure equipment` (shelf/slot/applique/protection-group) | 16 | same |

Unit tests: **105/105 passed** across all 35 modules.

## All Implemented Modules

All 30 roadmap modules plus 5 legacy modules are implemented and merged to `main`.

| Priority | Module | Command families | States Validated |
| --- | --- | --- | --- |
| 1-10 | First 10 | See completed table above | all 7 canonical states |
| 11 | `isam_alarm` | `configure alarm` | gathered, rendered, parsed, merged/--check |
| 12 | `isam_traps` | `configure trap` | gathered, rendered, parsed, merged/--check |
| 13 | `isam_interface_cages` | `configure interface cage` | gathered, rendered, parsed, merged/--check |
| 14 | `isam_ntp_onts` | `configure ntp ont` | gathered, rendered, parsed, merged/--check |
| 15 | `isam_qos_maps` | `configure qos tc-map-dot1p`, `dscp-map-dot1p` | gathered, rendered, parsed, merged/--check |
| 16 | `isam_system` | `configure system` | gathered, rendered, parsed, merged/--check |
| 17 | `isam_vlan_global` | `configure vlan` global settings | gathered, rendered, parsed, merged/--check |
| 18 | `isam_voice_sip` | `configure voice sip` | gathered, rendered, parsed, merged/--check |
| 19 | `isam_xdsl_bonding` | `configure xdsl-bonding` | gathered, rendered, parsed, merged/--check |
| 20 | `isam_dhcp_server` | `configure dhcp-server` | gathered, rendered, parsed, merged/--check |
| 21 | `isam_generic_pon` | `configure generic-pon` | gathered, rendered, parsed, merged/--check |
| 22 | `isam_iphost` | `configure iphost` | gathered, rendered, parsed, merged/--check |
| 23 | `isam_li_vlan` | `configure li_vlan` | gathered, rendered, parsed, merged/--check |
| 24 | `isam_igmp` | `configure igmp` | gathered, rendered, parsed, merged/--check |
| 25 | `isam_mcast_control` | `configure mcast-control` | gathered, rendered, parsed, merged/--check |
| 26 | `isam_software_mngt` | `configure software-mngt` | gathered, rendered, parsed, merged/--check |
| 27 | `isam_ani_onts` | `configure ani ont` | gathered, rendered, parsed, merged/--check |
| 28 | `isam_mcast_general` | `configure mcast general` | gathered, rendered, parsed, merged/--check |
| 29 | `isam_xdsl_boards` | `configure xdsl board`, `vp-board` | gathered, rendered, parsed, merged/--check |
| 30 | `isam_equipment_replan` | `configure equipment replan` | gathered, rendered, parsed, merged/--check |
| 31 | `isam_interface_alarms` | `configure interface alarm` | gathered, rendered, parsed, merged/--check |

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
| `isam_igmp` | `configure igmp` | Owns IGMP snooping, querier, and query parameters. |
| `isam_mcast_control` | `configure mcast-control` | Owns multicast-control limits and administrative state. |
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

Initial operational fact subsets are now available through `isam_facts`:

| Resource | Read-only command |
| --- | --- |
| `equipment_status` | `show equipment slot` |
| `ont_status` | `show equipment ont status pon` |
| `pon_status` | `show pon interface` |
| `interface_status` | `show interface port` |
| `active_alarms` | `show alarm current table` |
| `software_status` | `show software-mngt oswp` |
| `ont_ranging_status` | `show equipment ont ranging-status channel-pair` |
| `ont_software_status` | `show equipment ont sw-version`, `sw-download` |
| `pon_pm_status` | `show pon interface tc-layer current-interval` |

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
