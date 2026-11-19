"""LineTest's flat and scoped/hierarchical read grammars; never run a test action."""
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import (
    LinetestTemplate,
    PARAMETER_FIELDS,
    SESSION_FIELDS,
)


def test_hierarchical_blocks_match_flat_output_and_merge_duplicate_identities():
    hierarchical = dedent('''\
        # sanitized example
        linetest
            single
                ltsession 200
                    ownerid tester timeout-period 30
                    test-mode single
                    session-cmd create
                exit
                ltparm 200 resistance
                    value1 1000 min-threshold 500
                exit
                ltsession 201
                    timeout-period 90
                exit
        exit all
    ''')
    flat = (
        "configure linetest single ltsession 200 ownerid tester timeout-period 30 test-mode single\n"
        "configure linetest single ltparm 200 resistance value1 1000 min-threshold 500\n"
        "configure linetest single ltsession 201 timeout-period 90\n"
    )
    parser = LinetestTemplate()
    assert parser.parse(hierarchical) == parser.parse(flat)
    result = parser.parse(flat + "configure linetest single ltsession 200 timeout-period 60\n")
    assert len(result["sessions"]) == 2
    assert result["sessions"][0]["timeout_period"] == "60"
    assert result["sessions"][0]["ownerid"] == "tester"


@pytest.mark.parametrize("prefix", ["configure linetest single ", "linetest single ", "single ", ""])
def test_scoped_session_and_parameter_headers(prefix):
    parsed = LinetestTemplate().parse(prefix + "ltsession 200\n    timeout-period 30\n" +
                                      prefix + "ltparm 200 resistance\n    value1 1000\n")
    assert parsed == {"sessions": [{"session_id": "200", "timeout_period": "30"}],
                      "parameters": [{"session_id": "200", "test_name": "resistance", "value1": "1000"}]}


@pytest.mark.parametrize("field", SESSION_FIELDS)
def test_every_session_field_round_trips(field):
    config = {"sessions": [{"session_id": "200", field.replace("-", "_"): "1"}], "parameters": []}
    parser = LinetestTemplate()
    assert parser.parse("\n".join(parser.render(config))) == config


@pytest.mark.parametrize("field", PARAMETER_FIELDS)
def test_every_parameter_field_round_trips(field):
    config = {"sessions": [], "parameters": [{"session_id": "200", "test_name": "resistance", field.replace("-", "_"): "1"}]}
    parser = LinetestTemplate()
    assert parser.parse("\n".join(parser.render(config))) == config


@pytest.mark.parametrize("field", ["group_opt", "busy_overwrite", "force_measure"])
def test_trailing_no_reset_round_trips(field):
    parser = LinetestTemplate()
    config = {"sessions": [{"session_id": "200", field: None}], "parameters": []}
    assert parser.parse("\n".join(parser.render(config))) == config


def test_parameter_identity_includes_both_session_and_test():
    parsed = LinetestTemplate().parse(
        "ltparm 200 resistance value1 1\nltparm 201 resistance value1 2\n"
        "ltparm 200 voltage value1 3\nltparm 200 resistance value2 4\n")
    assert parsed["parameters"] == [
        {"session_id": "200", "test_name": "resistance", "value1": "1", "value2": "4"},
        {"session_id": "201", "test_name": "resistance", "value1": "2"},
        {"session_id": "200", "test_name": "voltage", "value1": "3"}]
