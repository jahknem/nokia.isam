from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ont_ranging_status import (
    OntRangingStatusParser,
)


def test_ont_ranging_status_parser_reads_channel_pair_table():
    output = """\
ONT                    Usage by ONT
---                    ------------
1/1/5/1/1              pref-ranged
1/1/5/1/2              prot-not-ranged-ready
"""

    assert OntRangingStatusParser().parse(output) == {
        "ranging_status": [
            {"ont": "1/1/5/1/1", "usage_by_ont": "pref-ranged"},
            {"ont": "1/1/5/1/2", "usage_by_ont": "prot-not-ranged-ready"},
        ]
    }


def test_ont_ranging_status_parser_accepts_pipe_table_and_normalizes_headers():
    output = """\
show equipment ont ranging-status channel-pair
| ont | usage-by-ont |
|-----|--------------|
| 1/1/5/1/3 | ranged-parked |
"""

    assert OntRangingStatusParser().parse(output) == {
        "ranging_status": [
            {"ont": "1/1/5/1/3", "usage_by_ont": "ranged-parked"}
        ]
    }


def test_ont_ranging_status_parser_returns_empty_records_without_a_table():
    assert OntRangingStatusParser().parse("No ONTs are using this channel pair") == {
        "ranging_status": []
    }
