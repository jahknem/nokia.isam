# Targeted gathering and read outcomes

Every configuration resource module in this collection supports **targeted
gathering**: with `state: gathered` and `config` naming instances, the module
reads only those instances from the device, one scoped CLI read per instance,
instead of the whole resource family. Without `config`, the whole resource is
read, exactly as before. A few instance lists have no single-instance read on
the device; for them the targeted request reads the whole node once and reports
each named instance from the parsed catalog (see
[Whole-node reads](#whole-node-reads)).

```yaml
- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_vlans:
    state: gathered
    config:
      - id: "100"
      - id: "stacked:200:10"
```

Selection is by identity only (see the table below); other fields in `config`
are ignored for the read. Absent instances are simply missing from `gathered`,
and the read never silently widens or serves a subset: an explicit request that
cannot be read in full -- an instance without a full identity, or no read
command at all -- fails the module with a clear message before anything is
sent, instead of falling back to the whole-family read.

## The `read_outcomes` contract

A targeted `gathered` read returns, next to `gathered`, a sanitized
`read_outcomes` result (documented in every module's return documentation):

```yaml
read_outcomes:
  resource: vlans
  parse: unverified            # parse axis at resource level
  outcomes:
    - section: config          # the config section that named the instance
      selector: "100"          # the instance identity (composite: joined by '/')
      command: ok              # command axis: ok | rejected | failed
      existence: present       # existence axis: present | confirmed_absent | unknown
    - section: config
      selector: "stacked:200:10"
      command: ok
      existence: confirmed_absent
```

Outcomes are per (section, instance): two config sections can name the same
identity value (for example an `equipment_onts` interface and loop sharing one
ONT id), and those are different instances, reported separately via
`section`.

* **Command axis** — did the CLI read run?
  * `ok` — the read ran and answered.
  * `rejected` — the device rejected the addressed node/selector
    (`invalid token`). For a read that means "nothing configured here", it is
    not an error and the module does not fail. Because `gathered` alone cannot
    tell a rejected instance from an absent one, the module also emits a
    warning naming the rejected selectors (`<section> <selector>`; no device
    text). Consumers that act on per-instance results use `read_outcomes`,
    where the existence stays `unknown`.
  * `failed` — the read itself failed (connection lost, timeout, device
    error). The module fails carrying this same sanitized result; the error
    class (`timeout`, `connection_error`, `device_error`) is recorded. The
    failure message is sanitized the same way: it names the resource, the
    selectors and the error class, never the raw device or transport text.
* **Existence axis** — does the addressed instance exist?
  * `present` — the read returned configuration for the instance (including
    the bare instance line for families that re-check attribute-free
    instances, see below).
  * `confirmed_absent` — the device's explicit "instance does not exist"
    signal **about the addressed instance**. This is the only outcome that is
    evidence an instance is gone.
  * `unknown` — anything else: a header-only reply (an instance without
    configured attributes answers like a non-existing one), an
    `invalid token` rejection, a missing *dependency* (e.g. a lower-interface
    does not exist, which says nothing about the addressed instance), or a
    failed read. `unknown` is **never** absence; consumers must keep, not
    remove, configuration for `unknown` instances.
* **Parse axis** — reported at resource level under `parse`
  (`failed` | `unverified`). `failed` means the family parser could not
  process the reply (whole-node reads, see below); `unverified` means no
  parser records its coverage of the reply, so a read never claims a complete
  parse; it says nothing about the device.
* **Sanitization** — outcomes contain stable enums, the selector, and an
  error class only. Raw device text is never recorded, so the result is safe
  to publish in an artifact. A composite identity is recorded joined by `/`
  (e.g. `scheduler-node/SN_Alpha`).

When one instance is addressed by several reads (a `isam_dhcp_relay` port is
read on `port-stats` and `v6-port-stats`), the aggregate for that instance is
conservative: a failed read is reported `failed`, a single present read proves
presence, and `confirmed_absent` holds only when **every** read of the instance
confirmed absence; anything less is `unknown`. `confirmed_absent` is the one
outcome a consumer may act on (it may remove configuration), so it must never
be aggregated from a mix of absence and inconclusive reads.

`read_outcomes` appears only for an explicit targeted `gathered` read.
Whole-family reads, write states (`merged`/`replaced`/`overridden`/`deleted`),
`parsed`, `rendered` and `isam_facts` carry none, and the returned
configuration text is byte-for-byte the legacy read for all of them.

## Supported families

53 resource families support targeted gathering: 51 with one scoped read per
instance, and 2 as whole-node catalog reads (see below).
(`plugins/module_utils/network/isam/targeted.py` is the machine-readable
registry: `TARGETED_GATHER` the per-section identities, and `TARGETED_READ_SCOPE`
the read scope of every resource — `whole_node` for the two catalog families,
`instance` for the rest). Identity: the field(s) in `config` that select the instance.

| Resource | Module | Targeted sections (identity) |
| --- | --- | --- |
| alarm | `isam_alarm` | `custom_profiles[].name`, `entries[].index`, `filters[].fltr_type + filterid`, `hgutr069_custs[].alarm_id` |
| ani_onts | `isam_ani_onts` | `config[].ont_idx` |
| bridges | `isam_bridges` | `port[].port` |
| channel_pair_pm | `isam_channel_pair_pm` | `config[].name` |
| efm_oam_interface | `isam_efm_oam_interface` | `config[].name` |
| epon_interfaces | `isam_epon_interfaces` | `config[].name` |
| equipment_onts | `isam_equipment_onts` | `interfaces[].ont_idx`, `slots[].ont_slot_idx`, `sw_ctrls[].sw_ctrl_id`, `loops[].ont_idx`, `pm_collects[].ont_idx` |
| ethernet_line | `isam_ethernet_line` | `config[].if_index` |
| ethernet_onts | `isam_ethernet_onts` | `config[].uni_idx` |
| igmp | `isam_igmp` | `packages[].index` |
| interface_alarms | `isam_interface_alarms` | `config[].name` (whole-node read) |
| interface_cages | `isam_interface_cages` | `config[].id` |
| interfaces | `isam_interfaces` | `config[].name` |
| isam_arp_relay | `isam_arp_relay` | `config[].name` |
| isam_cfm | `isam_cfm` | `domains[].domain_index`, `y1731pm[].domain_index + association + mep + session_id` |
| isam_dhcp_relay | `isam_dhcp_relay` | `config[].name` |
| isam_dist_service | `isam_dist_service` | `config[].name` |
| isam_equipment | `isam_equipment` | `appliques[].id`, `protection_groups[].id`, `shelves[].id`, `slots[].id`, `diagnostics_sfp[].id`, `protection_elements[].id`, `racks[].id`, `external_link_assigns[].id`, `external_link_hosts[].id` |
| isam_ipv6_antispoofing_slot | `isam_ipv6_antispoofing_slot` | `config[].name` |
| isam_system_security | `isam_system_security` | `operators[].name`, `profiles[].name`, `snmp_communities[].name`, `snmp_views[].name`, `snmp_managers[].name`, `snmp_notify_profiles[].name`, `radius_auth_servers[].name`, `radius_policies[].name`, `radius_dyn_auth_clients[].name`, `snmp_notify_views[].name`, `domains[].name`, `slots[].slot`, `ssh.sftp_users[].name`, `filetransfer.servers[].server`, `peripheral_mgnt.mac_filters[].index`, `pae.ports[].port` |
| isam_traps | `isam_traps` | `definitions[].name`, `managers[].address`, `v6managers[].ipv6address` |
| isam_vlan_global | `isam_vlan_global` | `priority_regen[].id` (whole-node read) |
| l2cp_session | `isam_l2cp_session` | `config[].name` |
| l2cp_user_port | `isam_l2cp_user_port` | `config[].name` |
| l2uni_onts | `isam_l2uni_onts` | `performance_monitor[].uni_idx`, `tc_layer_threshold[].uni_idx` |
| linetest | `isam_linetest` | `parameters[].session_id + test_name`, `sessions[].session_id` |
| link_agg | `isam_link_agg` | `groups[].id`, `ports[].id` |
| mcast_control | `isam_mcast_control` | `packages[].index` |
| multicast | `isam_multicast` | `igmp.packages[].index`, `mcast_control.packages[].index` |
| ngpon2_channel_groups | `isam_ngpon2_channel_groups` | `config[].id` |
| ntp_onts | `isam_ntp_onts` | `config[].ont_id` |
| pon_interfaces | `isam_pon_interfaces` | `config[].name` |
| pppoe_client_interface | `isam_pppoe_client_interface` | `config[].name` |
| pppoe_client_ppp_profile | `isam_pppoe_client_ppp_profile` | `config[].name` |
| pppoel2_statistics | `isam_pppoel2_statistics` | `config[].name` |
| qos_global | `isam_qos_global` | `line_cards[].name` |
| qos_interfaces | `isam_qos_interfaces` | `config[].name` |
| qos_maps | `isam_qos_maps` | `dn_ctrl_pkt[].protocol`, `dscp_map_dot1p[].dscp`, `tc_map_dot1p[].dot1p`, `up_ctrl_pkt[].protocol` |
| qos_profiles | `isam_qos_profiles` | `config[].profile_type + name` |
| qos_tca | `isam_qos_tca` | `config[].name + queue` |
| software_mngt | `isam_software_mngt` | `oswp[].id` |
| system | `isam_system` | `sntp.servers[].ip_address`, `syslog.destinations[].name`, `syslog.routes[].destination`, `sync_if_timing.ssm[].reference`, `sync_if_timing.synce[].reference`, `sync_if_timing.ssmout_synce[].port` |
| trouble_shooting_pon | `isam_trouble_shooting_pon` | `interfaces[].name`, `threshold.interfaces[].name` |
| uni_onts | `isam_uni_onts` | `config[].uni_idx` |
| vlans | `isam_vlans` | `config[].id` |
| voice_sip | `isam_voice_sip` | `cas_nsm_prof[].name`, `lineid_syn_prof[].name`, `redundancy[].name`, `redundancy_cmd[].name`, `register[].name`, `vsp[].name` |
| xdsl_boards | `isam_xdsl_boards` | `boards[].board_id`, `vp_boards[].vp_board_id` |
| xdsl_bonding | `isam_xdsl_bonding` | `groups[].group_id`, `boards[].board_id` |
| xdsl_inm | `isam_xdsl_inm` | `far_end[].name`, `near_end[].name` |
| xdsl_lines | `isam_xdsl_lines` | `config[].name` |
| xdsl_onts | `isam_xdsl_onts` | `config[].ont_idx` |
| xdsl_profiles | `isam_xdsl_profiles` | `dpbo_profiles[].id`, `service_profiles[].id`, `spectrum_profiles[].id`, `vce_profiles[].id`, `vect_profiles[].id` |
| xstp | `isam_xstp` | `ports[].port` |

## Whole-node reads

Two families have instance lists the firmware exposes **without a
single-instance read**: `interface_alarms` (per-interface alarm severity) and
`isam_vlan_global` (the `priority_regen` profiles, which answer `invalid token`
when addressed individually). For them `state: gathered` with `config` naming
instances reads the **whole node once** — the only read the device offers — and
reports each named instance in `read_outcomes` from the parsed catalog:

* `present` — the catalog lists the instance;
* `unknown` — the catalog does not list it, or the node read was rejected
  (`invalid token`), or a dependency is missing. A named instance the parsed
  catalog does not list is **never** `confirmed_absent`: the parser's catalog
  completeness is unverified (the parse axis stays `unverified`), and a reply
  line the parser does not recognize would make a configured instance vanish
  from the catalog. Absence of a whole-node instance is therefore not
  established by a read;
* `confirmed_absent` — only the device's own node-absence signal about the node
  read (nothing under a non-existing node can be configured), the same signal a
  scoped read uses for an instance.

A failed node read fails the module carrying the outcomes, as for any targeted
read; a reply the family parser cannot process is classified the same way with
`parse: failed` (every requested instance `unknown`).

This is the documented exception to the scoped-read contract: no per-instance
command is sent, and `gathered` is the **full catalog, unfiltered** — siblings
of the named instances are in it. An explicit request that cannot be read in
full (a named instance without an identity) still fails before anything is
sent, and a whole-node read without `config` carries no outcomes, as before.

Resources without instance lists at all (`cwmp_plt`, `dhcp_server`,
`equipment_replan`, `generic_pon`, `iphost`, `l2cp`, `li_vlan`,
`mcast_general`, `nat`, `pon_global`, `pppox_relay_global`, `xdsl_system`,
...) are single settings blocks: the whole read **is** the instance, and
targeted gathering does not apply to them.

## Behavior notes

* **Attribute-free instances.** An instance without configured attributes
  answers a scoped read with only the header, exactly like a non-existing
  one. Families whose instances can exist attribute-free re-check with
  `flat detail` and report them `present` with their bare line: `alarm`
  (custom profiles), `isam_dist_service`, `isam_qos_maps` (control-packet
  entries), `isam_traps` (managers) and `isam_trouble_shooting_pon`
  (interfaces). In all other families such an instance is reported
  `unknown` — never `confirmed_absent`, and never `present`.
* **Dependencies.** If the device reports that a *dependency* of the
  addressed instance is missing, the instance's own existence is `unknown`
  with a `dependency_gap`; the read is not an error. `lower-interface`: the
  device says the lower-interface does not exist. `interface-index`:
  dhcp-relay/arp-relay answer "The interface index cannot be calculated" for a
  port the device cannot resolve -- evidence about the port, not about the
  relay instance.
* **Device messages only.** Absence and rejection are recognized only on the
  device's own message lines (`Error : ...`), never inside configuration: a
  present instance whose description reads "instance does not exist" is
  `present`.
* **Instances sharing one read.** Where one read command serves several
  instances (`isam_system_security` `ssh.sftp_users`: the device rejects a
  single-user read, so the ssh node is read once), each instance gets its own
  outcome, decided from its own line in the reply: `present` when the user's
  line is there, else `unknown` (the node read is not the device's absence
  signal for the user).
* **Write states are unchanged.** `merged`/`replaced`/`deleted` with `config`
  already compared only the named instances where that is exact; they report
  no `read_outcomes` and their command sets are unchanged.
* **`isam_facts`** and offline parsing (`parsed`) perform no device read of
  their own and carry no outcomes.

## Limitations

* A `rejected` outcome does not disambiguate "the firmware does not know this
  node on this platform" from "the selector is malformed"; both are
  `unknown` existence by design.
* `parse: unverified` is the norm: the parsers do not record their coverage
  of the reply, so a targeted read never claims a complete parse.
* Outcome evidence is per requested instance. A whole-family read carries no
  outcomes, and `confirmed_absent` is only as good as the device's existence
  signal for that read (verified on R6.2.04m lab devices; see
  [live-test matrix](live-test-matrix.md)).
* For whole-node reads, `confirmed_absent` comes only from the device's
  node-absence signal, never from the parsed catalog: an instance the catalog
  does not list is `unknown`, because the parser's coverage of the reply is
  unverified (see the parse axis above; the parsers of the two whole-node
  families are the same ones that serve every whole read and write-state
  comparison of those families).
