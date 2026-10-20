from pathlib import Path
import subprocess
import sys

import pytest
from ansible.errors import AnsibleFilterError
from ansible_collections.nokia.isam.plugins.filter.monitoring import FilterModule
from ansible_collections.nokia.isam.plugins.module_utils.monitoring import (
    parse_unprovisioned_onts, parse_xdsl_operational_lines,
)

FIXTURES = Path(__file__).resolve().parents[4] / "fixtures"


def output(name):
    return (FIXTURES / name / "synthetic-regression/output.txt").read_text()


@pytest.mark.parametrize("parser,name", [(parse_unprovisioned_onts, "unprovisioned_onts"),
                                         (parse_xdsl_operational_lines, "xdsl_operational_lines")])
def test_incomplete_tables_fail_instead_of_becoming_empty(parser, name):
    text = output(name)
    with pytest.raises(ValueError):
        parser(text.replace("count : 2", "count : 3"))
    with pytest.raises(ValueError):
        parser("invalid token")
    with pytest.raises(ValueError):
        parser("unprovision-onu count : 0\nline count : 0")


def test_fixed_width_blank_auth_id_is_not_the_rate():
    text = output("unprovisioned_onts")
    row = " ".join(value.ljust(width) for value, width in zip(
        ["1", "1/1/1/1", "XXXX:SANIT", "LOC1", "", "0.00k"], [9, 17, 14, 16, 14, 7]))
    text = text.replace("1|1/1/1/1|XXXX:SANIT|LOC1|auth1|0.00k", row)
    result = parse_unprovisioned_onts(text)
    assert result[0]["logical_authid"] == ""
    assert result[0]["actual_us_rate"] == "0.00k"


def test_blank_subscriber_location_does_not_become_the_rate():
    text = output("unprovisioned_onts")
    row = " ".join(value.ljust(width) for value, width in zip(
        ["1", "1/1/1/1", "XXXX:SANIT", "", "", "0.00k"], [9, 17, 14, 16, 14, 7]))
    result = parse_unprovisioned_onts(text.replace("1|1/1/1/1|XXXX:SANIT|LOC1|auth1|0.00k", row))
    assert result[0]["subscriber_locid"] == ""
    assert result[0]["actual_us_rate"] == "0.00k"


def test_filter_import_does_not_load_the_resource_framework():
    code = '''import sys
from ansible_collections.nokia.isam.plugins.filter.monitoring import FilterModule
assert len(FilterModule().filters()) == 2
assert "ansible_collections.nokia.isam.plugins.module_utils.network.isam" not in sys.modules
assert not any("rm_base.resource_module" in name for name in sys.modules)
'''
    subprocess.run([sys.executable, "-c", code], check=True)


def test_empty_table_is_valid_only_with_its_header_and_zero_count():
    text = output("unprovisioned_onts")
    text = "\n".join(line for line in text.splitlines() if not line.startswith(("1|", "2|")))
    assert parse_unprovisioned_onts(text.replace("count : 2", "count : 0")) == []


def test_xdsl_missing_rates_are_not_invented_as_zero():
    rows = parse_xdsl_operational_lines(output("xdsl_operational_lines"))
    assert rows[0]["us_rate"] == "5493" and rows[0]["ds_rate"] == "32995"
    assert rows[1]["us_rate"] is None and rows[1]["ds_rate"] is None


def test_xdsl_bad_numeric_rate_fails():
    with pytest.raises(ValueError):
        parse_xdsl_operational_lines(output("xdsl_operational_lines").replace("5493", "broken"))


def test_filter_errors_are_real_failures_not_successful_strings():
    filters = FilterModule().filters()
    with pytest.raises(AnsibleFilterError):
        filters["parse_unprovisioned_onts"]("invalid token")

