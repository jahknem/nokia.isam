# Upgrading from 0.3.14 to 1.0

**Status: preparation branch, not a published 1.0 release.** The 0.3.14 patch
preserved legacy schemas; 1.0 intentionally corrects them. The collection remains
under active development: a major version is not a claim that every command or
device/software combination is production-verified.

## Before upgrading

1. Pin the existing collection at 0.3.14 while auditing playbooks and consumers.
2. Save private, access-controlled configuration/fact baselines. Do not commit raw
   device output, passwords, production addresses or unsanitized names.
3. Audit the schema changes below, including consumers of gathered/parsed facts,
   not just configuration inputs. Do not replay old saved facts blindly.
4. Parse representative sanitized captures offline, render candidate changes and
   review check-mode output against the specific device. A check-mode action never
   proves that executing the operation is harmless or authorized.
5. Apply only separately approved, scoped changes. Each write still requires a
   dry run, allow-list, readback and before/after comparison. No new global writes,
   counter clears, LineTest actions or NOC changes are authorized by this upgrade.

The patch history is merged rather than rewritten. Its transport, deletion-scope,
default-handling and review fixes are retained in the major-version frameworks.
`replaced` changes named list instances; `overridden` may remove unnamed ones.
Omitted resettable fields of a named replacement can still reset, so inspect the
actual commands rather than relying on an instance-name match alone.

## VLAN facts and option names

`isam_vlans` now returns snake_case fact keys such as `protocol_filter`,
`new_broadcast`, `dhcpv6_itf_id` and `drly_srv_usr_side`. CLI spellings such as
`protocol-filter` remain accepted as **input aliases**; they are not duplicate
output keys. Update Jinja lookups, stored fact schemas and comparisons.

For example, replace `vlan['protocol-filter']` with `vlan.protocol_filter`.
Names and identifiers remain values; do not mechanically rewrite their contents.
Creating a VLAN requires its mandatory `mode`; mode has no standalone reset form.

Sixteen options previously modelled as booleans actually require values:

| Canonical option(s) | 1.0 value form |
| --- | --- |
| `dhcp_opt82_nni`, `dhcp_opt82_uplink` | `enable`, `disable`, `transparent`, `add-or-replace`, `add-or-forward` |
| `relay_id_dhcp` | `relay-id`, `disable` |
| `dhcp_linerate`, `pppoe_linerate`, `dhcpv6_linerate` | `notadd`, `addactuallinerate`, `addalllineparameters` |
| `pppoe_l2_encaps`, `dhcp_l2_encaps`, `dhcpv6_l2_encaps` | `notadd`, `add` |
| `l2_encaps1` | `not-applicable`, `untagged`, `single-tagged`, `dual-tagged` |
| `pppoer_vlanaware` | Device value as a string; consult device help |
| `dhcpr_vlanaware`, `dhcpv6r_vlanaware` | `upto-1-uservlan`, `upto-2-uservlans`, `upto-untag-uservlan`, `system-default` |
| `drly_srv_usr_side` | `enable`, `disable` |
| `dhcpv6_relay_id` | `disable`, `duid-ll` |
| `dhcpv6_trst_port` | `trusted`, `untrusted` |

Do not convert every `true` to `enable`: several of these options do not accept
that keyword. Render-only example, not an instruction to write:

```yaml
- name: Review VLAN syntax offline
  nokia.isam.isam_vlans:
    state: rendered
    config:
      - id: "3990"
        mode: residential-bridge
        name: "Example VLAN"
        protocol_filter: pass-pppoe
        drly_srv_usr_side: enable
        dhcpv6_trst_port: untrusted
```

## Generic PON values

Replace legacy boolean approximations with the actual values:

| Option | 1.0 type / choices |
| --- | --- |
| `utilization.pon_pmcollect` | string: `none`, `pm-enable`, `tca-enable` |
| `utilization.ont_pmcollect` | string: `enable`, `disable` |
| `ont.slid_mode` | string: `ascii`, `hexa-dec` |
| `ont.sn_bundle_timer` | integer |
| `ont.sw_ver_mis_block`, `ont.sn_autounlock` | string: `enable`, `disable` |
| `alarmflag.ponlos_alarm_ctrl` | string: `enable`, `disable` |

The device default belongs to the resource grammar rather than being injected
into every request. Omission and an explicit default have different intent when
the device currently has a non-default value. `dpinteg_threshold` is set-only;
deletion does not invent a removal command for it.

## SIP values and session timers

Many legacy SIP booleans represented value-taking commands. Audit every configured
section with `ansible-doc nokia.isam.isam_voice_sip`:

- `vsp.admin_status` and `system.admin_status` take `up` / `down`.
- VSP timers, jitter settings and payload types are integers, not flags.
- Domain/URI/prefix/profile values are strings. Enumerated options such as
  `uri_type`, `digit_send_mode`, `signaling_ipmode` and `media_ipmode` have explicit
  choices; their old boolean values have no universal translation.
- Registration delays/intervals and redundancy timers/counters are integers.
  Redundancy enable/disable controls use their documented string values.
- `system.session_timer` is removed. Configure the session-timer fields directly:
  `status` (`enable`, `disable`, `enable-uas`), `min_se_time`, `se_time` and
  `admin_status` (`up`, `down`).
- `redundancy_cmd.geo_fail_over` is removed. `fail_x_type` takes `geo-fail-over`
  or `geo-fail-back`; start/end times are integers.

The module documentation and attribute-table agreement tests are the complete
field-by-field contract. Only actual flags remain boolean. Replacing one VSP
preserves unnamed VSPs; overriding the list can remove them.

## Software management

- `oswp[].auto_verify`: `disabled` / `enabled`, not boolean.
- `oswp[].activate`: `manually`, `after-download`, `on-schedule`, not boolean.
- `oswp[].on_schedule_time`: a device time string, not boolean.
- `sw_replacement_mode.mode` is constrained to `upgrade-via-active`,
  `upgrade-via-standby` or `lt-by-lt`.

Do not infer a schedule or activation operation from an old `true` value.
`replaced` retains unnamed OSWPs; `overridden` can remove them. Software operations
still require a separate operational decision and are not authorized by examples.

## QoS control-packet maps

For `up_ctrl_pkt[]` and `dn_ctrl_pkt[]`, `queue` and `profile` are removed.
Entries are keyed by `protocol` and use the real device parameters `dscp`, `pbit`
and `tc`. There is no lossless mechanical queue/profile conversion: derive the
values from the intended policy and device documentation.

QoS profile options additionally accept snake_case aliases without changing their
existing CLI-spelled fact keys. Do not assume every resource changed output key
style just because VLAN facts did.

## xDSL VP-board links

The scalar `vp_boards[].vp_link` and `vp_boards[].lt_expect` fields are replaced
with a list of link records:

```yaml
vp_boards:
  - vp_board_id: "1/1/6"
    vp_links:
      - link_id: "1"
        lt_expect: "1/1/7"
```

Each link has its own `link_id` and optional `lt_expect`. Preserve all intended
links when translating saved facts; do not collapse multiple device links into
one scalar. This is a structural example, not a recommendation to plan hardware.

## System security and facts

`isam_system_security` is the dedicated security resource. `isam_system` no longer
gathers security into `system.security`; that legacy configuration option remains
write-only and deprecated. Move security gathers/reconciliation to the dedicated
module after reviewing its explicit schema and secret-handling rules.

Masked/redacted credentials are preserve-only, not reusable secrets. Opaque
identities cannot safely select destructive operations. Never replace a redacted
value with a guessed password or account identity to make replay pass.

The new `config_tree` facts subset is an opt-in root-tree diagnostic, not a set
of resource-module options and not an action plan. Device-default/detail output
is selected separately with `config_tree_detail`. Unknown command syntax may
defeat heuristic redaction; review diagnostic output privately before sharing it.

## Operational actions and validation boundaries

Ethernet statistics, DHCP relay port statistics and learned-MAC deletion are new
one-shot action modules. The ext-authenticator action uses the same reviewed base.
Every action requires an explicit operation and validates identifiers; a bare
resource path is not an operation. Check mode never acquires a connection.

An execution failure reports `failed_command`, completed/accepted response context
and pending commands. A verification failure means the command was sent/accepted
but completion is unknown. Commands are never silently retried. Review the result
before deciding whether any follow-up is safe; do not rerun an entire action list
blindly after a partial failure.

`IsamResourceModule`, `IsamActionModule` and `AttributeTable` remain the shared
implementations, with device-specific behavior kept explicit. The published
patch's API-fingerprint tests are intentionally not used to forbid 1.0 changes;
its safety/replay regressions are retained under the migrated schemas.

Historical device evidence and unverified areas remain in
[the live-test matrix](live-test-matrix.md). No new live writes are part of this
preparation. Tagging/publication and any additional device tests require separate
decisions.
