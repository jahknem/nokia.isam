from textwrap import dedent
from pathlib import Path

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.operational import (
    Equipment_statusFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.isam_equipment.operational import (
    EquipmentOperationalParser,
)


class TestEquipmentOperationalParser(object):
    def setup_method(self):
        self.parser = EquipmentOperationalParser()

    def test_parses_equipment_records_and_normalizes_values(self):
        output = dedent(
            """\
            DS-LIN-TEST-01:automationuser># show equipment
            shelf 1/1
              actual-type: nfxs-b
              operational-state: up
            slot lt:1/1/1
              actual-type ndps-c
              admin-state: unlocked
            applique ntio-1
              actual-type: ncnc-d
            protection-group 33
              admin-status: lock
              eps-quenchfactor: 0
            DS-LIN-TEST-01:automationuser>#
            """
        )

        assert self.parser.parse(output) == {
            "shelves": [{"id": "1/1", "actual_type": "nfxs-b", "operational_state": "up"}],
            "slots": [{"id": "lt:1/1/1", "actual_type": "ndps-c", "admin_state": "unlocked"}],
            "appliques": [{"id": "ntio-1", "actual_type": "ncnc-d"}],
            "protection_groups": [{"id": 33, "admin_status": "lock", "eps_quenchfactor": 0}],
        }

    def test_ignores_comments_and_unrelated_lines(self):
        output = dedent(
            """\
            #-------------------------------------------------------------------------------
            random heading
            slot nt-a
              serial-no: ABC123
              firmware-version 6.02.04
            exit
            """
        )

        assert self.parser.parse(output) == {
            "slots": [
                {
                    "id": "nt-a",
                    "serial_no": "ABC123",
                    "firmware_version": "6.02.04",
                }
            ]
        }

    def test_empty_output_returns_empty_mapping(self):
        assert self.parser.parse("") == {}

    def test_structured_equipment_status_discovers_fglt_b_from_fixture(self):
        output = Path(__file__).parents[4].joinpath(
            "fixtures", "equipment_status", "fglt-b", "output.txt"
        ).read_text()
        slots = Equipment_statusFacts(None).parse(output)["slots"]
        assert any(
            row["slot"] == "lt:1/1/5"
            and row["actual_type"] == "fglt-b"
            and row["enabled"] == "yes"
            for row in slots
        )

    def test_structured_equipment_status_discovers_fglt_d_from_fixture(self):
        output = Path(__file__).parents[4].joinpath(
            "fixtures", "equipment_status", "fglt-d", "output.txt"
        ).read_text()
        slots = Equipment_statusFacts(None).parse(output)["slots"]
        assert sum(row["actual_type"] == "fglt-d" for row in slots) == 2
