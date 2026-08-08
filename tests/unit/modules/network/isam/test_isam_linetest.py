from textwrap import dedent

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.linetest import LinetestTemplate


def test_linetest_parse_ignores_test_actions():
    parsed = LinetestTemplate().parse(dedent("""
        configure linetest single ltsession 3 session-cmd create timeout-period 120 test-mode single
        configure linetest single ltparm 3 resist-tr(ohm) value1 1 min-threshold 10
    """))
    assert parsed["sessions"] == [{"session_id": "3", "timeout_period": "120", "test_mode": "single"}]
    assert parsed["parameters"] == [{
        "session_id": "3", "test_name": "resist-tr(ohm)", "value1": "1", "min_threshold": "10",
    }]


def test_linetest_render_is_configuration_only():
    commands = LinetestTemplate().render({"sessions": [{"session_id": "1", "timeout_period": "120"}], "parameters": []})
    assert commands == ["configure linetest single ltsession 1 timeout-period 120"]
    assert all("session-cmd" not in command for command in commands)
