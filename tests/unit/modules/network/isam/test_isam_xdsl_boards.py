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

    def tearDown(self):
        super(TestIsamXdslBoardsModule, self).tearDown()
        self.get_config.stop()

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
        self.assertEqual(result["commands"], ["configure xdsl no board 1/1/1"])
