# Agent Guidelines for nokia.isam Collection

## Fixture Conventions

### Fixture Structure
All fixtures follow a consistent structure under `tests/fixtures/<resource>/<variant>/`:
- `fixture.yml`: Metadata descriptor with required fields
- `output.txt`: Raw device output (sanitized for live captures)

### Fixture Descriptor Fields
Every `fixture.yml` must include:
```yaml
schema_version: 1
resource: <resource_name>
device_type: <device_model>
software_version: <version>
command: <command_that_generated_output>
captured_at: <YYYY-MM-DD>
source: sanitized-live-capture | synthetic-regression
```

### Fixture Sources
1. **sanitized-live-capture**: Real device output with sensitive data sanitized
   - Use length-preserving sanitization for fixed-width tables
   - Replace serials: `<VENDOR>:<HEX>` → `XXXX:SANIT` (10 chars)
   - Replace IPs: preserve column width with padding
   - Replace hostnames: `DS-LIN-TEST-01` → `SANITIZED-ISAM`

2. **synthetic-regression**: Manually crafted test data
   - Must be parseable by the resource parser
   - Should cover edge cases and typical configurations

### Fixture Testing
All fixtures must have corresponding tests in `tests/unit/modules/network/isam/test_device_fixtures.py`:
- Load the fixture using `fixture_bundle(resource, variant)`
- Parse with the appropriate parser/template
- Assert specific parsed values to verify correctness

### Parser Guidelines
1. **Table Parsers**: Use `parse_status_table()` for pipe-delimited tables
2. **Config Parsers**: Use `NetworkTemplate` subclasses with regex patterns
3. **Operational Parsers**: Use specialized parsers (e.g., `AlarmStatusParser`, `OntRangingStatusParser`)

### Common Parser Patterns
- Two-line headers: Merge top/bottom rows before parsing
- Count lines: Skip lines matching `^<name> count : \d+$`
- Pipe vs whitespace: Detect `|` to choose split strategy
- Length preservation: Critical for fixed-width table sanitization

### Testing Commands
```bash
# Run all tests
python -m pytest tests/unit/modules/network/isam/ -q

# Run fixture tests only
python -m pytest tests/unit/modules/network/isam/test_device_fixtures.py -v

# Run integration tests
python -m pytest tests/unit/modules/network/isam/test_isam_facts.py -v

# Run round-trip render tests
python -m pytest tests/unit/modules/network/isam/test_render_round_trip.py -v

# Run lint
.venv/bin/tox --workdir /tmp/opencode/nokia-isam-tox -e lint
```

### Adding New Fixtures
1. Create fixture directory: `tests/fixtures/<resource>/<variant>/`
2. Add `fixture.yml` with all required fields
3. Add `output.txt` with device output (sanitized if live)
4. Add test function in `test_device_fixtures.py`
5. Verify parser handles the format correctly
6. Run tests to ensure no regressions

### Integration Tests
Integration tests in `test_isam_facts.py` verify end-to-end module behavior:
- Load fixture files and feed them through the actual `isam_facts` module
- Use mock connections that return fixture content
- Verify the module returns correct parsed data structure
- Test both config and operational resources

Example:
```python
def test_isam_facts_with_alarm_status_fixture(self):
    fixture_path = Path(__file__).parent.parent.parent.parent.parent / "fixtures" / "alarm_status" / "r6.2.04m" / "output.txt"
    fixture_content = fixture_path.read_text()
    
    class AlarmConn:
        def get(self, cmd):
            if cmd == "show alarm current table":
                return fixture_content
            return ""
    
    self.get_resource_connection_facts.return_value = AlarmConn()
    set_module_args(dict(gather_subset=["active_alarms"]))
    
    result = self.execute_module(changed=False)
    alarms = result["ansible_facts"]["ansible_net_active_alarms"]["alarms"]
    assert len(alarms) == 40
```

### Round-Trip Render Tests
Round-trip tests in `test_render_round_trip.py` verify parse → render → parse consistency:
- Parse configuration with template
- Render parsed data back to commands
- Parse rendered commands again
- Verify both parse results are identical

This ensures templates can both read and write configuration correctly.

### Sanitization Best Practices
- Use regex with length-preserving replacements
- Test that sanitized output still parses correctly
- Verify column alignment in fixed-width tables
- Keep vendor prefixes when sanitizing serials (e.g., `GNXS:SANIT`)
