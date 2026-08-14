# Live Validation 2026-08-10

Target: `DS-LIN-TEST-01` using the production inventory and vault.

The read-only gathered sweep passed for every `isam_*.py` module in the
collection, including bridges and optional PON variant modules. No
configuration or administrative action was applied during this sweep.

On this target, EPON, NG-PON2 channel-group, and channel-pair are not
installed. Their gathered results are empty rather than failures when ISAM
returns `invalid token` for the PDF-defined optional command paths.

The validated command was equivalent to:

```text
ansible DS-LIN-TEST-01 -m nokia.isam.<module> -a state=gathered
```

The following were intentionally excluded because they are not gathered
resource modules:

- `isam_facts` requires explicit `gather_subset` or `gather_network_resources` selection.
- `cli_config` is config-only.
- `isam_security_ext_authenticator` is action-only.

Mutating states were validated only through unit tests and check mode. Replace
and rollback are not supported by the ISAM cliconf plugin.
