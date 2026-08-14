# Resource Module Work Packages

Last reviewed: 2026-08-10

This document is the per-resource work plan for the 52 concrete resource
modules in `plugins/modules`. It separates implementation status from test and
live-evidence status. No package authorizes live mutation.

## Status Definitions

- **Implemented**: no specific parser or renderer defect is currently proven.
- **Hardening**: a concrete parser, schema, renderer, or state-semantic gap is known.
- **Evidence**: implementation appears complete, but resource-specific fixture or live state proof is incomplete.
- **Blocked**: the target lacks the feature, returns no usable command path, or the module intentionally has no normal facts query.
- **Contract only**: the generic six-state/check-mode test passes; this does not prove device-specific deletion or reconciliation semantics.

## Cross-Cutting Acceptance Criteria

Every package that changes code must satisfy the following unless its row says
otherwise:

1. Argspec, facts parser, resource template, renderer, and reconciliation use the same field names and identity key.
2. Positive, negative, empty, packed, hierarchical, and noisy output forms supported by the device are covered by fixtures.
3. `gathered`, `parsed`, and `rendered` behavior is tested, plus `merged`, `replaced`, `overridden`, and `deleted` in check mode.
4. Re-running a converged configuration produces no commands, and deletion does not delete unrelated siblings.
5. The module passes the repository test, compile, lint, type, documentation, and diff gates.
6. Live validation is read-only or check mode only; unsupported-command handling must not hide transport, authentication, or device errors.

## Priority Order

## Optical Pass Progress

The 2026-08-10 optical pass uses `detail` only to discover possible vocabulary.
Normal gathered parsing remains on the resource-specific `flat` commands.

- ANI ONT threshold fields are implemented and the stale ANI model metadata is corrected.
- Generic PON now parses packed supported flags and the documented utilization-threshold branch; power-shed and GIS are separate model branches and remain outside this RM.
- PON interface packed base fields and documented per-interface PM/TCA branches are normalized before parsing; display-only status and obsolete/profile families remain outside this resource.
- Ethernet ONT power-control, PSE, power-override, and LPT fields are implemented; `oper-state` remains display-only.
- Equipment ONT facts now merge repeated flat records by identity and the documented interface field set is represented; PM/operational words remain excluded from desired-state rendering.
- EPON, NG-PON2 channel groups, and channel-pair PM use narrow `invalid token` suppression, argspec-backed facts, normalized IDs, and empty gathered results on the target because those features are not installed.
- Voice SIP replacement/deletion is now section- and target-scoped; statistics positive/negative parsing and quoted string rendering are covered.
- QoS profiles now preserve queue units, scheduler `ext-shaper`, shaper `autoshape`, aggregate queue assignments, policer/session/bandwidth fields, ingress per-P-bit mappings, and rate-limit protocol fields; observed negative forms are ignored or represented as false without becoming attributes.
- XDSL lines now preserve `rtx-profile` and `sos-profile`; XDSL board flat parsing merges repeated identities and handles `no admin-state`.
- NTP ONT now follows the documented `client-state`, `config-mode`, three-server, operation-mode, key-identifier, and key grammar.
- System SNTP now parses the device-native `server-ip-addr`, `polling-rate`, `enable`, and `timezone-offset` fields.
- Interface cages now reconcile documented `operational-mode`; DHCP packed parsing no longer invents an enabled restart when the token is absent.

### WP-01: Voice SIP

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_voice_sip` | Hardening | Validate packed detail-flat parsing for every represented section. Prove positive value grammar for `domain-name`, timers, string fields, and all negative booleans. Harden replacement, override, delete, and multi-instance reconciliation. | `tests/fixtures/voice_sip/r6.2.04m/output.txt`; `/tmp/opencode/detail_matrix_1878_info_configure_voice_sip_detail_flat.out`; `facts/voice_sip/voice_sip.py`; `config/voice_sip/voice_sip.py` | Resource template parsed state equals gathered state for the fixture; all schema fields have positive/negative tests; state-specific command tests cover every section and no unrelated section is removed. |

### WP-02: Core Provisioning Gaps

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_ani_onts` | Hardening | Add dedicated regression coverage for `tca-thresh`, `lower-optical-th`, `upper-optical-th`, `rssi-profile`, and each documented `no` form. Verify deletion semantics separately from generic contract coverage. | `rm_models/configure/ani/ont/tca-thresh/help.txt`; `/tmp/opencode/detail_matrix_2_info_configure_ani_ont_detail_flat.out`; `tests/fixtures/ani_onts` | Typed values and documented ranges are preserved; packed lines round-trip; deleting one threshold does not delete the ONT or sibling thresholds. |
| `isam_generic_pon` | Hardening | Complete resource-specific deletion and packed-subsection tests. Confirm the modeled utilization, ONT, alarmflag, and DP-integrity fields against live detail output; classify any unknown fields as facts-only or unsupported rather than silently dropping them. | `/tmp/opencode/detail_matrix_10_info_configure_generic-pon_detail_flat.out`; `rm_templates/generic_pon.py`; `tests/unit/modules/network/isam/test_isam_generic_pon.py` | Every modeled subsection has positive/negative render and parse tests; absent feature and empty output remain distinguishable from command failure. |
| `isam_software_mngt` | Hardening | Fixture all database, OSWP, and software-replacement fields, including packed `activate`, `auto-verify`, `on-schedule-time`, and negative forms. Verify high-risk replacement/deletion ordering. | `/tmp/opencode/detail_matrix_33_info_configure_software-mngt_detail_flat.out`; `tests/unit/modules/network/isam/test_software_mngt_parser.py` | No OSWP sibling is removed during replacement/override; packed flags preserve false values; database no-forms are either implemented or explicitly documented as unsupported. |
| `isam_pon_interfaces` | Hardening | Cover the documented normal-flat vocabulary plus `tc-layer-threshold`, `mcast-tc-layer`, `phy-layer`, `fec-tc-layer`, `xg-tc-layer`, `otdr`, `utilization`, and `deact-ont-tca` branches. Keep `oper-state` display-only and obsolete PON profile families separate. | Nokia R6.2.04ng PON command guide; `tests/unit/modules/network/isam/test_isam_pon_interfaces.py` | Nested branches, technology-aware reset values, identity/value constraints, and restricted-field admin-state ordering are covered; add versioned live fixtures and remaining negative-form tests. |
| `isam_equipment_onts` | Hardening | Audit emitted interface PM, threshold, loop, policing, multicast, and power fields against the typed schema. Preserve unknown words only where they are proven configuration-owned. | `/tmp/opencode/detail_matrix_1605_info_configure-equipment_ont_detail_flat.out`; `argspec/equipment_onts/equipment_onts.py`; `facts/equipment_onts/equipment_onts.py` | Schema/parser/config agreement is demonstrated by a live fixture; operational values are not rendered as configuration commands; ONT identity and sibling reconciliation remain stable. |
| `isam_system` | Hardening | Split global detail vocabulary into desired-state configuration and facts-only output. Review banner, zero-touch, loop/relay syntax, max LT speed, security subfields, SNTP, syslog, timing, and transaction fields. | `/tmp/opencode/detail_matrix_168_info_configure_system_detail_flat.out`; `argspec/system/system.py`; `rm_models/configure/system` | Each retained field has documented CLI grammar and state semantics; omitted global fields are explicitly facts-only or unsupported; global replacement cannot issue unsafe broad deletion. |

### WP-03: VLAN, QoS, and XDSL Vocabulary Sweeps

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_qos_interfaces` | Evidence | Inventory queue, shaper, CAC, control-packet, and PM words before expanding the schema. Add only fields with documented positive grammar. | `/tmp/opencode/detail_matrix_27_info_configure-qos_interface_detail_flat.out` | Field inventory is reviewed; supported fields have fixtures; unknown output is reported without breaking gathered state. |
| `isam_qos_profiles` | Implemented | Preserve the live detail vocabulary across queue, scheduler, aggregate queue, policer, session, shaper, bandwidth, ingress-QoS, and rate-limit profiles. | `/tmp/opencode/detail_matrix_28_info_configure-qos_profiles_detail_flat.out`; `tests/unit/modules/network/isam/test_isam_qos_profiles.py` | Observed fields round-trip; representative packed positive and negative forms are covered; unsupported profile words are not silently parsed as fields. |
| `isam_qos_maps` | Implemented | Retain coverage for `tc-map-dot1p`, `dscp-map-dot1p`, `up-ctrl-pkt`, and `dn-ctrl-pkt`; add live fixture assertions for optional color/profile fields and `dot1p-value`. | `/tmp/opencode/detail_matrix_29_info_configure-qos_tc-map-dot1p_detail_flat.out`; `tests/unit/modules/network/isam/test_isam_qos_maps.py` | All four command families gather and render idempotently, including optional fields and deletion. |
| `isam_xdsl_lines` | Implemented | Preserve the complete documented line command surface: service, spectrum, DPBO, RTX, vectoring, SOS, DSL mode flags, carrier-data mode, transfer mode, impulse-noise sensor, QLN mode, auto-switch, vector fallback, and admin state. Obsolete bonding mode and display-only profile-name/overrule data remain excluded. | Live `help configure xdsl line`, `info configure xdsl line flat`, and detail evidence; `tests/unit/modules/network/isam/test_isam_xdsl_lines.py` | Documented positive/negative forms, packed flat parsing, all four state semantics, idempotence, and sibling isolation are covered. |
| `isam_xdsl_profiles` | Evidence | Audit service, spectrum, and related profile subfamilies for field ownership and typed values. | `/tmp/opencode/detail_matrix_43_info_configure-xdsl_service-profile_detail_flat.out`; `/tmp/opencode/detail_matrix_44_info_configure-xdsl_spectrum-profile_detail_flat.out` | Profile lists preserve identity and sibling entries through replacement/override/delete. |
| `isam_xdsl_boards` | Evidence | Add detail fixtures for board and VP-board negative forms and verify model-specific field normalization. | `/tmp/opencode/detail_matrix_39_info_configure-xdsl_board_detail_flat.out`; `argspec/xdsl_boards/xdsl_boards.py` | Board and VP-board commands parse/render without cross-family collisions. |
| `isam_xdsl_bonding` | Evidence | Add a successful detail fixture and verify the small schema against the bonding help model. | `/tmp/opencode/detail_matrix_41_info_configure-xdsl-bonding_detail_flat.out` | Supported bonding fields and no-forms are covered; empty output is valid. |
| `isam_vlan_global` | Evidence | Preserve global broadcast, priority-regen, TPID, and VMAC ownership; cover reset forms separately from per-VLAN state. | `/tmp/opencode/detail_matrix_36_info_configure-vlan_detail_flat.out`; `/tmp/opencode/detail_matrix_58_info_configure-vlan-global_detail_flat.out`; `tests/unit/modules/network/isam/test_isam_vlan_global.py` | Invalid-token on the target is treated as unsupported feature, global fields do not duplicate per-VLAN ownership, and reset forms parse safely. |
| `isam_vlans` | Implemented | Preserve the complete observed per-VLAN flat vocabulary, including stacked IDs, priorities, aging, secure forwarding, QoS references, DHCP/PPPoE relay identifiers, and valueless flags. | Live `info configure vlan id flat`; `tests/unit/modules/network/isam/test_isam_vlans.py` | Gathered/rendered state, merged/replaced/overridden/deleted reconciliation, idempotence, and sibling isolation are covered. |

### WP-04: Interfaces and Ethernet

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_interfaces` | Evidence | Add interface-type-specific detail fixtures and verify empty output versus unsupported command handling. | `/tmp/opencode/detail_matrix_12_info_configure-interface_port_detail_flat.out` | Interface identity, negative forms, and sibling reconciliation are covered. |
| `isam_interface_cages` | Evidence | Validate cage-specific detail fields and no-forms against interface-port output. | `/tmp/opencode/detail_matrix_13_info_configure-interface_cage_detail_flat.out` | Cage records parse without consuming unrelated interface records. |
| `isam_interface_alarms` | Implemented | Retain positive and `no default-severity` regression coverage; add a fixture-backed gathered assertion. | `/tmp/opencode/detail_matrix_14_info_configure-interface_alarm_detail_flat.out`; `rm_templates/interface_alarms.py` | Severity reset parses as an empty/absent value and does not create a false severity. |
| `isam_ethernet_onts` | Evidence | Review power-control, PSE, LPT, PM, and VLAN fields and separate operational from configuration vocabulary. | `/tmp/opencode/detail_matrix_9_info_configure-ethernet_ont_detail_flat.out` | Configuration-owned fields are typed and rendered; operational fields are facts-only. |
| `isam_ethernet_line` | Evidence | Add resource-specific detail and no-form assertions; preserve line identity under replacement. | `plugins/module_utils/network/isam/{argspec,facts,config}/ethernet_line`; live gathered validation | Line fields round-trip and sibling lines remain intact. |
| `isam_bridges` | Implemented | Maintain existing parser/config coverage and add a live detail fixture if bridge output changes across software versions. | Live gathered validation; `argspec/bridges` | Empty, single, and multiple bridge records are covered. |
| `isam_link_agg` | Implemented | Maintain the first-ten full state package and add member-order/idempotence assertions. | First-ten validation set; `argspec/link_agg` | Member ordering and deletion are deterministic. |

### WP-05: Multicast, Alarms, and Protocol Services

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_mcast_general` | Evidence | Inventory all global multicast fields and add typed fixture coverage beyond `fast-change` and `package-member`. | `/tmp/opencode/detail_matrix_23_info_configure-mcast_general_detail_flat.out` | Supported global fields and no-forms round-trip. |
| `isam_mcast_control` | Evidence | Audit multicast-control limits and admin state against the shared flat facts parser. | `/tmp/opencode/detail_matrix_24_info_configure-mcast-control_detail_flat.out` | Shared facts aliases do not change the resource schema unexpectedly. |
| `isam_igmp` | Evidence | Validate snooping, querier, context, and query parameter ownership with representative detail lines. | `/tmp/opencode/detail_matrix_11_info_configure-igmp_detail_flat.out` | IGMP and multicast contexts reconcile independently. |
| `isam_multicast` | Evidence | Verify shared IGMP/mcast-control aliases and ensure this module does not duplicate dedicated module commands. | Shared multicast facts/config; matrix `11`, `23`, `24` | Ownership and command output are documented and tested. |
| `isam_alarm` | Evidence | Add representative custom-profile, delta-log, entry, filter, log-severity, and negative-form fixtures before expanding desired-state schema. | `/tmp/opencode/detail_matrix_1_info_configure-alarm_detail_flat.out`; `rm_models/configure/alarm` | Unknown alarm words do not disappear silently; supported alarm identities reconcile independently. |
| `isam_traps` | Evidence | Inventory trap definitions and managers; add fixtures for identity, destination, and deletion semantics. | `/tmp/opencode/detail_matrix_35_info_configure-trap_detail_flat.out` | Trap definitions and managers do not collide during replacement. |
| `isam_ntp_onts` | Evidence | Add detail fixture and explicit `no server`, `no port`, `no poll-interval`, and `no enable` assertions. | `/tmp/opencode/detail_matrix_25_info_configure-ntp-ont_detail_flat.out`; `argspec/ntp_onts` | ONT identity and all documented optional fields round-trip. |
| `isam_cfm` | Evidence | Add field-level assertions for domains, services, and maintenance endpoints; preserve nested identity. | `/tmp/opencode/detail_matrix_49_info_configure-cfm_detail_flat.out` | Nested CFM records reconcile without cross-domain deletion. |
| `isam_efm_oam_interface` | Evidence | Add detail fixture and verify interface identity/no-form handling. | `/tmp/opencode/detail_matrix_52_info_configure-efm-oam-interface_detail_flat.out` | OAM fields round-trip and empty output is handled. |
| `isam_dhcp_server` | Implemented | Maintain packed address/lease parser coverage and add fixture assertions for all observed server options. | `/tmp/opencode/detail_matrix_119_info_configure-dhcp-server_detail_flat.out` | `stop_addr` and packed negative lease forms remain stable. |
| `isam_dhcp_relay` | Implemented | Preserve conditional IPv6 probing behavior and add empty-output/error taxonomy tests. | Live empty detail result; `facts/dhcp_relay` | Configured IPv4/IPv6 counters query correctly; unsupported counters are not treated as transport failures. |
| `isam_arp_relay` | Evidence | Add representative gathered/detail and replacement/deletion assertions. | Live empty detail result; `rm_templates/arp_relay.py` | Empty success and command failure remain distinct. |

### WP-06: Equipment and Operations

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_equipment` | Implemented | Maintain first-ten full state coverage and add nested shelf/slot/applique/protection-group ordering assertions. | First-ten validation set | Nested resources are independently reconciled. |
| `isam_equipment_replan` | Evidence | Add detail fixture and verify high-risk replan command ordering and deletion behavior. | `/tmp/opencode/detail_matrix_7_info_configure-equipment-replan_detail_flat.out` | No replan command is replayed or issued for unrelated equipment. |
| `isam_equipment_onts` | Hardening | See WP-02; do not merge this work into generic equipment until ONT field ownership is proven. | Matrix `1605` | See WP-02. |
| `isam_ethernet_onts` | Evidence | See WP-04; separate config PM fields from operational power/loop data. | Matrix `9` | See WP-04. |
| `isam_linetest` | Implemented | Maintain documented session-destroy semantics and add command-order assertions for multi-session deletion. | `tests/fixtures/linetest`; `docs/work_packages.md` | Parameter deletion never emits an undocumented command. |
| `isam_ipv6_antispoofing_slot` | Evidence | Add detail and negative-form fixture coverage for slot identity and anti-spoof settings. | Live gathered validation; `argspec/ipv6_antispoofing_slot` | Slot records remain isolated. |

### WP-07: L2, PPPoE, and Distribution

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_l2cp` | Evidence | Add explicit empty-output fixture and verify global L2CP fields. | Live empty detail result; `argspec/l2cp` | Empty success is gathered as empty and does not mask CLI errors. |
| `isam_l2cp_session` | Evidence | Verify session identity and no-form handling when feature output is present. | Live empty detail result; `argspec/l2cp_session` | Session siblings reconcile independently. |
| `isam_l2cp_user_port` | Evidence | Verify user-port identity and packed options when feature output is present. | Live empty detail result; `argspec/l2cp_user_port` | User-port siblings reconcile independently. |
| `isam_pppoe_client_interface` | Blocked | Add parsed/rendered/check-mode coverage only; do not claim gathered support until a valid read-only facts command is identified. | Roadmap; live empty/unsupported path | Module explicitly reports its no-facts limitation. |
| `isam_pppoe_client_ppp_profile` | Blocked | Same as client interface; document command-path dependency and preserve offline parser behavior. | Roadmap; live empty/unsupported path | No false gathered state is produced. |
| `isam_pppoel2_statistics` | Blocked | Keep as parsed/rendered/check-mode only until a valid `pppoe-l2` detail path exists. | `/tmp/opencode/detail_matrix_56_info_configure_pppoe-l2_detail_flat.out` (`invalid token`) | Invalid token is classified as unsupported, not empty valid configuration. |
| `isam_dist_service` | Evidence | Add service identity and deletion fixture coverage. | Live gathered validation | Distribution-service siblings do not collide. |
| `isam_li_vlan` | Implemented | Maintain underscore command spelling and add a fixture for empty/negative output. | `/tmp/opencode/detail_matrix_16_info_configure-li_vlan_detail_flat.out` | CLI spelling remains consistent in query and renderer. |

### WP-08: Optional Hardware and Explicitly Unsupported Paths

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_epon_interfaces` | Blocked | Keep optional-feature handling; add a test that `invalid token` produces empty gathered state while auth/transport errors fail. | `/tmp/opencode/detail_epon.out`; `docs/command_tree.md` | EPON absence is reported as unsupported/empty, not as a parser defect. |
| `isam_ngpon2_channel_groups` | Blocked | Same optional-feature test for channel groups. | `/tmp/opencode/detail_channel-group.out` | Unsupported installed-feature path is explicit. |
| `isam_channel_pair_pm` | Blocked | Same optional-feature test for channel-pair PM. | `/tmp/opencode/detail_channel-pair.out` | Unsupported installed-feature path is explicit. |
| `isam_iphost` | Blocked | Identify a valid installed-feature command before adding fields; current target returns no usable `configure iphost` detail output. | Live empty detail result | No schema expansion based on absent evidence. |

### WP-09: XSTP and Remaining First-Class RMs

| RM | Status | Work package | Evidence | Exit criteria |
| --- | --- | --- | --- | --- |
| `isam_xstp` | Evidence | Add field-level assertions for general, port, region, and negative forms. | `/tmp/opencode/detail_matrix_48_info_configure-xstp_detail_flat.out` | Region and port identities reconcile independently. |
| `isam_interfaces` | Evidence | See WP-04. | Matrix `12` | Interface-specific detail coverage exists. |
| `isam_ethernet_line` | Evidence | Add resource-specific fixture and no-form tests. | Existing argspec/facts/config; live gathered validation | Line identity and sibling reconciliation are stable. |
| `isam_bridges` | Implemented | Maintain parser and gathered coverage; add versioned fixture only if bridge vocabulary changes. | Live gathered validation | Existing fields remain idempotent. |
| `isam_vlans` | Evidence | See WP-03. | Matrix `36` | Per-VLAN fields remain distinct from global VLAN ownership. |
| `isam_qos_maps` | Implemented | See WP-03. | Matrix `29`; unit tests | Four map families remain covered. |
| `isam_qos_profiles` | Evidence | See WP-03. | Matrix `28` | Profile field inventory is complete or documented. |
| `isam_qos_interfaces` | Evidence | See WP-03. | Matrix `27` | Interface QoS field inventory is complete or documented. |

## Non-RM Modules

- `isam_security_ext_authenticator` is action-only and is not included in the 52-RM count; its package is command execution and failure handling, not resource-state reconciliation.
- `isam_facts` is a facts aggregator; validate each subset independently and do not apply resource-module state criteria to it.
- `cli_config` supports text configuration only because the device has no replace/rollback contract; it is not an RM.

## Shared Release Gates

Before declaring the collection complete:

- Replace the aggregate “all gathered validation passed” claim with an invocation/result table for all concrete RMs.
- Record the exact device/software version and artifact for every live command.
- Keep generic state-contract coverage separate from resource-specific semantic coverage.
- Run the full local test, compile, lint, typecheck, documentation, and artifact gates in a clean environment with the required `ansible.netcommon` collection.
- Do not claim live mutation validation until explicit authorization is provided.
