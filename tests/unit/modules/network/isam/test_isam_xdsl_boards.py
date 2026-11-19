from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_boards
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


class TestIsamXdslBoardsModule(TestIsamModule):
    module = isam_xdsl_boards

    def setUp(self):
        super(TestIsamXdslBoardsModule, self).setUp()
        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_boards.xdsl_boards.Xdsl_boardsFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()
        # The module needs a (mocked) device connection of its own; it used to ride on
        # patches other test classes leaked.
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamXdslBoardsModule, self).tearDown()
        self.mock_get_config.stop()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_deleted_board_preserves_vp_board_with_same_id(self):
        self.get_config.return_value = "\n".join([
            "configure xdsl board 1/1/1 vce-profile 10",
            "configure xdsl vp-board 1/1/1 admin-state up",
        ])
        set_module_args(
            {"state": "deleted", "config": {"boards": [{"board_id": "1/1/1"}]}},
            True,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure xdsl board 1/1/1 no vce-profile"])
