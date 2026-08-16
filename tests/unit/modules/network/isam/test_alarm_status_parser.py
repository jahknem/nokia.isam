from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm_status import (
    AlarmStatusParser,
)


def test_alarm_status_parser_reads_active_alarm_table():
    output = """\
Alarm ID  Severity  State   Source    Description
1001      major     active  1/1/1/1  Loss of signal
1002      warning   active  1/1/1/2  Remote defect indication
"""

    assert AlarmStatusParser().parse(output) == {
        "alarms": [
            {
                "alarm_id": "1001",
                "severity": "major",
                "state": "active",
                "source": "1/1/1/1",
                "description": "Loss of signal",
            },
            {
                "alarm_id": "1002",
                "severity": "warning",
                "state": "active",
                "source": "1/1/1/2",
                "description": "Remote defect indication",
            },
        ]
    }


def test_alarm_status_parser_normalizes_headers_and_ignores_framing():
    output = """\
=== Active alarms ===
ID        Severity  Status  Location  Text
---       --------  ------  --------  ----
42        critical  active  shelf-1   Board failure reported
"""

    assert AlarmStatusParser().parse(output) == {
        "alarms": [
            {
                "alarm_id": "42",
                "severity": "critical",
                "state": "active",
                "source": "shelf-1",
                "description": "Board failure reported",
            }
        ]
    }


def test_alarm_status_parser_returns_empty_records_without_a_table():
    assert AlarmStatusParser().parse("No active alarms") == {"alarms": []}


def test_alarm_status_parser_reads_index_type_timestamp_table():
    output = """\
index     |type                 |last-updated-on
----------+---------------------+-----------------------------------------------
1          olt-gen               2026-08-10:13:00:31
2          ont-ploam             2026-08-10:13:00:26
"""

    result = AlarmStatusParser().parse(output)
    assert len(result["alarms"]) == 2
    assert result["alarms"][0] == {
        "index": "1",
        "type": "olt-gen",
        "last_updated_on": "2026-08-10:13:00:31",
    }
    assert result["alarms"][1] == {
        "index": "2",
        "type": "ont-ploam",
        "last_updated_on": "2026-08-10:13:00:26",
    }


def test_alarm_status_parser_handles_pipe_delimited_table():
    output = """\
Alarm ID|Severity|State|Source|Description
--------+--------+-----+------+-----------
1001    |major   |active|1/1/1|Loss of signal
"""

    result = AlarmStatusParser().parse(output)
    assert len(result["alarms"]) == 1
    assert result["alarms"][0]["alarm_id"] == "1001"
    assert result["alarms"][0]["severity"] == "major"


def test_alarm_status_parser_rejects_unrecognized_columns():
    output = """\
index     |type     |unknown-col
----------+---------+------------
1          olt-gen   ignored
"""

    result = AlarmStatusParser().parse(output)
    assert result == {"alarms": []}


def test_alarm_status_parser_handles_empty_table():
    output = """\
index     |type                 |last-updated-on
----------+---------------------+-----------------------------------------------
"""

    result = AlarmStatusParser().parse(output)
    assert result == {"alarms": []}
