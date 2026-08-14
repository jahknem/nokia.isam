from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.equipment_replan.equipment_replan import (
    Equipment_replan,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.equipment_replan import (
    Equipment_replanTemplate,
)


def test_deleted_removes_requested_value():
    resource = object.__new__(Equipment_replan)
    resource.state = "deleted"
    resource.want = {"board_auto_replan": "enable"}
    resource.have = {"board_auto_replan": "enable"}
    resource.commands = []
    resource._tmplt = Equipment_replanTemplate()
    resource.generate_commands()
    assert resource.commands == ["configure equipment replan no boardautoreplan"]
