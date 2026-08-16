from textwrap import dedent

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import (
    Software_statusFacts,
)


def test_software_status_parses_oswp_table():
    output = dedent(
        """\
        index|name        |availability|act-status|commit-status
        -----+------------+------------+----------+-------------
        1     L6GPAA62.652 enabled      not-active committed
        2     L6GPAA62.819 enabled      active     un-committed
        """
    )

    result = Software_statusFacts(None).parse(output)
    assert len(result) == 2
    assert result[0]["index"] == "1"
    assert result[0]["name"] == "L6GPAA62.652"
    assert result[0]["availability"] == "enabled"
    assert result[0]["act_status"] == "not-active"
    assert result[0]["commit_status"] == "committed"
    assert result[1]["act_status"] == "active"


def test_software_status_handles_empty_table():
    output = dedent(
        """\
        index|name|availability|act-status|commit-status
        -----+----+------------+----------+-------------
        """
    )

    result = Software_statusFacts(None).parse(output)
    assert result == []


def test_software_status_handles_empty_string():
    result = Software_statusFacts(None).parse("")
    assert result == []
