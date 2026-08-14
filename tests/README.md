The supported automated test suite is under `tests/unit/modules/network/isam`.

Run it with:

```bash
make test
```

Live inventory and credentials are intentionally kept outside this collection.

Sanitized and synthetic CLI fixtures are under `tests/fixtures`. Each fixture
bundle contains `output.txt` and a required `fixture.yml` descriptor recording
the resource, device type, software version, command, capture date, and source.
