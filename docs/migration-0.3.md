# 0.3 Migration Notes

## Operational Facts

Use `gather_subset` for operational data. Results are exposed as
`ansible_net_<subset>` facts. Configuration resources remain under
`ansible_network_resources` when requested with `gather_network_resources`.

The previous legacy resource-facts names are not emitted by 0.3. Update tasks
that read `ansible_network_resources.<operational_resource>` to the matching
`ansible_net_*` fact.

The default facts request is intentionally read-only and empty. Request
operational subsets explicitly, for example:

```yaml
- nokia.isam.isam_facts:
    gather_subset:
      - "!all"
      - active_alarms
```

## External Authenticator

`isam_security_ext_authenticator` is now an action-only module. Supply
`config` explicitly; `state`, `running_config`, parsing, and gathering are not
supported because the device command is administrative and non-persistent.

## CLI Configuration

`nokia.isam.cli_config` accepts `config` text only. Replace-file and rollback
are rejected because the ISAM cliconf plugin does not expose those operations.
