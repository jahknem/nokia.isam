from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_boards.xdsl_boards import (
    Xdsl_boards,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_boards import (
    Xdsl_boardsTemplate,
)


def test_isam_resource_removal_is_not_prefixed_with_no():
    resource = object.__new__(Xdsl_boards)
    resource._tmplt = Xdsl_boardsTemplate()
    resource.commands = []
    resource.addcmd({"board_id": "1/1/1"}, "board", negate=True)
    assert resource.commands == ["configure xdsl no board 1/1/1"]
