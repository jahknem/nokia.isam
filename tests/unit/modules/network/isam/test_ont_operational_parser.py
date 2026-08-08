from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.ont_operational.ont_operational import (
    parse_ont_operational,
    parse_operational_facts,
    parse_pon_operational,
    parse_status_table,
)


def test_parse_operational_facts_keeps_multiple_ont_sections_and_normalizes_labels():
    output = """
    # show equipment ont status
    ONT 1/1/5/1/1:
      Admin state: up
      Operational state = up
      Serial-number: ALCL:F9772423
    ONT 1/1/5/1/2:
      Admin state: down
    """

    assert parse_ont_operational(output) == [
        {
            "type": "ont",
            "id": "1/1/5/1/1",
            "admin_state": "up",
            "operational_state": "up",
            "serial_number": "ALCL:F9772423",
        },
        {"type": "ont", "id": "1/1/5/1/2", "admin_state": "down"},
    ]


def test_parse_operational_facts_accepts_unscoped_labeled_output():
    assert parse_operational_facts("Optical RX power: -18.2 dBm\nTemperature: 42 C\n") == [
        {"optical_rx_power": "-18.2 dBm", "temperature": "42 C"}
    ]


def test_parse_pon_operational_filters_ont_sections():
    output = """
    PON interface 1/1/5/1:
      Oper state: up
    ONT 1/1/5/1/1:
      Oper state: down
    """

    assert parse_pon_operational(output) == [
        {"type": "pon", "id": "1/1/5/1", "oper_state": "up"}
    ]


def test_parse_status_table_reads_fixed_width_device_rows():
    output = """
    port      |admin-state|oper-state
    ----------+-----------+----------
    pon:1/1/1  up          down
    """

    assert parse_status_table(output) == [
        {"port": "pon:1/1/1", "admin_state": "up", "oper_state": "down"}
    ]
