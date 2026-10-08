# Changelog

## 0.3.6

- Consolidate bridge VLAN mapping onto the single canonical `l2fwder_vlan`
  attribute. `network_vlan` is accepted as the obsolete CLI alias and is
  normalized at one entry point, so alias input, legacy device output,
  validation, comparison and rendering all share the same field.
  - Rendered commands always use `l2fwder-vlan`; the module never emits the
    obsolete `network-vlan` form.
  - Supplying both names with different values now fails instead of writing
    two conflicting mappings.
  - The VLAN/PVID ordering guard applies to alias input as well, so
    `network_vlan` cannot bypass the bootstrap requirement.
  - Gathered and parsed `l2fwder_vlan` values are strings, matching the
    resource argspec.
  - Bridge VLAN removal against a device configured with `network-vlan` is
    rendered as `no l2fwder-vlan`, which clears the same setting.

## 0.3.5

- Preserve `network_vlan` as the backwards-compatible alias for
  `l2fwder_vlan`. The CLI guide marks `network-vlan` obsolete-and-replaced,
  and specifies that obsolete-and-replaced parameters remain executable even
  though `info` reports the replacement. Do not reject an alias-only request.

## 0.3.4

- Added the `ont_serials` `isam_facts` operational subset, which reads
  `show equipment ont interface` and returns an MSAN-wide `ont-idx` to `sernum`
  index under `ansible_net_ont_serials`. This is substantially cheaper than
  expanding the whole `info configure equipment ont flat` tree and is
  sufficient for ONT-serial reuse detection and per-PON population counting.
  A device that rejects the command omits the key rather than reporting an
  empty index, so callers can distinguish "unsupported" from "no ONTs".

## 0.3.3

- Allow bridge network VLANs without an l2fwder VLAN.
- Fixed `isam_bridges` rendering `tag`/`l2fwder-vlan`/`vlan-scope`/`qos` as
  separate commands. Live devices require these to be issued together on a
  single `configure bridge port <id> vlan-id <id> ...` command; issuing
  `vlan-scope`/`qos` as separate trailing commands after `tag`+`l2fwder-vlan`
  is rejected with `VLAN MGT error 149: Such configuration mode of VLAN
  port is not permitted`. Confirmed and fixed against a live device.

## 0.3.2

- Treat missing lower interfaces as absent during scoped resource reads.

## 0.3.1

- Fixed scoped QoS interface fact parsing when compact device output includes trailing separator or echo lines.

## 0.3.0

- Made operational facts use explicit `gather_subset` values and `ansible_net_*` output names.
- Restricted `cli_config` to supported text configuration.
- Made external-authenticator an explicit action-only module.
- Corrected LineTest deletion and optional-field `no` handling.
- Corrected DHCPv6 statistics probing and optional facts error handling.
- Added migration and read-only live-validation documentation.
