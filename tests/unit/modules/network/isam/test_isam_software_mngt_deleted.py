from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.software_mngt.software_mngt import (
    Software_mngt,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    Software_mngtTemplate,
)


def test_deleted_oswp_preserves_unrequested_siblings():
    resource = object.__new__(Software_mngt)
    resource.state = "deleted"
    resource.want = {"oswp": [{"id": "1"}]}
    resource.have = {
        "oswp": [
            {"id": "1", "primary_file_server_id": "a", "second_file_server_id": "b"},
            {"id": "2", "primary_file_server_id": "c", "second_file_server_id": "d"},
        ]
    }
    resource.commands = []
    resource._tmplt = Software_mngtTemplate()
    resource.generate_commands()
    assert resource.commands == ["configure software-mngt no oswp 1"]
