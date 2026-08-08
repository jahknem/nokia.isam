from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_boards.xdsl_boards import (
    Xdsl_boardsFacts,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch


class FakeConnection:
    def __init__(self):
        self.commands = []

    def get(self, command):
        self.commands.append(command)
        if command == "info configure xdsl board flat":
            return "board 1/1/1 annex-a"
        return "vp-board 1/1/1 profile default"


def test_xdsl_boards_gathers_board_and_vp_board():
    connection = FakeConnection()
    facts = Xdsl_boardsFacts(module=None)
    ansible_facts = {"ansible_network_resources": {}}

    with patch(
        "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_boards.xdsl_boards.validate_config_safe",
        side_effect=lambda argument_spec, data: data,
    ):
        facts.populate_facts(connection, ansible_facts)

    assert connection.commands == [
        "info configure xdsl board flat",
        "info configure xdsl vp-board flat",
    ]
    assert ansible_facts["ansible_network_resources"]["xdsl_boards"] == {
        "boards": [{"board_id": "1/1/1", "annex_a": True}],
        "vp_boards": [{"vp_board_id": "1/1/1", "profile": "default"}],
    }
