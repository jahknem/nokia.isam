# Device Fixtures

Captured CLI output belongs in a fixture bundle:

```text
tests/fixtures/<resource>/<fixture-name>/
  fixture.yml
  output.txt
```

Every `fixture.yml` must identify the device family, software version, command,
capture date, and whether the output is a sanitized capture or a synthetic
regression fixture. Do not store credentials, hostnames, public IP addresses,
or other secrets in fixture output.

Required descriptor fields:

```yaml
schema_version: 1
resource: voice_sip
device_type: Nokia ISAM 7330 FTTN
software_version: R6.2.04m
command: info configure voice sip flat
captured_at: 2026-08-10
source: sanitized-live-capture
```

Use `source: synthetic-regression` when the fixture is assembled from known
device grammar rather than copied from a device.
