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

The CFM, EFM OAM, L2CP, PPPoE-client and PPPoE-L2 synthetic bundles were corrected
against lab CLI help on 2026-11-19. The channel-pair PM, EPON and NG-PON2 channel-group
bundles use the matching CLI guide grammar (sections 68.9, 69.2 and 57.2/57.3):
those features are unavailable in the lab platform's help tree, so these are **not**
live-verified captures. Tests must assert actual parsed identities and attributes;
`len(parsed) >= 0` does not test parsing and must not be used.

## Live write scenarios

`live_scenarios/<bundle>/` pins write behaviour from live device tests (lab ISAM,
linecard 6 planned as another board type):

```text
fixture.yml          descriptor (as above)
output.txt           device state with every set step applied (flat)
output-detail.txt    the same, 'flat detail'
base.txt             the card freshly planned (flat)
base-detail.txt      the same, 'flat detail'
scenarios.yml        per step: module, state, config, the device state before it
                     (base or configured) and the commands the device accepted
                     (or the facts it returned)
```

`test_live_write_scenario` runs every scenario against the captured state. Only
steps whose prior state is one of the two captures are scenarios. Bundles are built
from the live test results; the files contain only the tested card's lines.
