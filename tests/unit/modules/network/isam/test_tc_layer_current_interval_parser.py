from textwrap import dedent

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.tc_layer_current_interval.tc_layer_current_interval import (
    TcLayerCurrentIntervalParser,
    parse_tc_layer_current_interval,
)


def test_parses_pdf_fields_from_labeled_output_and_converts_counters():
    output = dedent(
        """\
        # show pon interface uni:1/1/1/1/1/1 tc-layer current-interval
        Resource Identifier: uni:1/1/1/1/1/1
        tx-gem-frames: 12
        rx-gem-frames: 34
        tx-payload-bytes: 5678
        rx-payload-bytes: 9012
        encrypkey-errors: 0
        """
    )

    assert parse_tc_layer_current_interval(output) == [
        {
            "resource_identifier": "uni:1/1/1/1/1/1",
            "tx_gem_frames": 12,
            "rx_gem_frames": 34,
            "tx_payload_bytes": 5678,
            "rx_payload_bytes": 9012,
            "encrypkey_errors": 0,
        }
    ]


def test_parses_pipe_delimited_table_rows():
    output = dedent(
        """\
        Resource Identifier | tx-gem-frames | rx-gem-frames | tx-payload-bytes | rx-payload-bytes | encrypkey-errors
        --------------------+----------------+----------------+-------------------+-------------------+-----------------
        mcast:1/1/1/1/7     | 1              | 2              | 3                 | 4                 | 5
        """
    )

    assert TcLayerCurrentIntervalParser().parse(output) == [
        {
            "resource_identifier": "mcast:1/1/1/1/7",
            "tx_gem_frames": 1,
            "rx_gem_frames": 2,
            "tx_payload_bytes": 3,
            "rx_payload_bytes": 4,
            "encrypkey_errors": 5,
        }
    ]


def test_keeps_multiple_labeled_resources_and_ignores_unrelated_fields():
    output = dedent(
        """\
        show pon interface tc-layer current-interval
        Resource Identifier = voip:1/1/1/1/8
        tx-gem-frames  10
        unrelated: ignored
        Resource Identifier = uni:1/1/1/1/9/1/1
        rx-gem-frames = 20
        """
    )

    assert TcLayerCurrentIntervalParser().parse(output) == [
        {"resource_identifier": "voip:1/1/1/1/8", "tx_gem_frames": 10},
        {"resource_identifier": "uni:1/1/1/1/9/1/1", "rx_gem_frames": 20},
    ]


def test_empty_or_noise_only_output_returns_empty_list():
    assert parse_tc_layer_current_interval("# no data\n----------------\n") == []
