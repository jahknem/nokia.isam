from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_equipment
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamEquipmentModule(TestIsamModule):
    module = isam_equipment

    def setUp(self):
        super(TestIsamEquipmentModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.isam_equipment.isam_equipment.Isam_equipmentFacts.get_config"
        )
        self.get_config = self.mock_get_config.start()

        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()

        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamEquipmentModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_equipment_rendered(self):
        set_module_args(
            dict(
                state="rendered",
                config=dict(
                    shelves=[dict(id="1/1", planned_type="nfxs-b")],
                    slots=[dict(id="lt:1/1/1", planned_type="ndps-c", admin_state="unlocked")],
                    appliques=[dict(id="ntio-1", planned_type="ncnc-d")],
                    protection_groups=[dict(id=33, admin_status="lock", eps_quenchfactor=0)],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            [
                "configure equipment shelf 1/1 planned-type nfxs-b",
                "configure equipment slot lt:1/1/1 planned-type ndps-c",
                "configure equipment slot lt:1/1/1 unlock",
                "configure equipment applique ntio-1 planned-type ncnc-d",
                "configure equipment protection-group 33 admin-status lock",
                "configure equipment protection-group 33 eps-quenchfactor 0",
            ],
        )

    def test_isam_equipment_parsed(self):
        set_module_args(
            dict(
                state="parsed",
                running_config=dedent(
                    """\
                    configure
                    equipment
                    shelf 1/1
                      planned-type nfxs-b
                    exit
                    slot lt:1/1/1
                      planned-type ndps-c
                      unlock
                    exit
                    applique ntio-1
                      planned-type ncnc-d
                    exit
                    protection-group 33
                      admin-status lock
                      eps-quenchfactor 0
                    exit
                    exit
                    """
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["shelves"], [dict(id="1/1", planned_type="nfxs-b")])
        self.assertEqual(
            result["parsed"]["slots"],
            [dict(id="lt:1/1/1", planned_type="ndps-c", unlock=True)],
        )
        self.assertEqual(result["parsed"]["appliques"], [dict(id="ntio-1", planned_type="ncnc-d")])
        self.assertEqual(
            result["parsed"]["protection_groups"],
            [dict(id=33, admin_status="lock", eps_quenchfactor=0)],
        )

    def test_isam_equipment_merged_idempotent(self):
        self.get_config.return_value = dedent(
            """\
            configure
            equipment
            shelf 1/1
              planned-type nfxs-b
            exit
            slot lt:1/1/1
              planned-type ndps-c
              unlock
            exit
            applique ntio-1
              planned-type ncnc-d
            exit
            protection-group 33
              admin-status lock
              eps-quenchfactor 0
            exit
            exit
            """
        )
        set_module_args(
            dict(
                state="merged",
                config=dict(
                    shelves=[dict(id="1/1", planned_type="nfxs-b")],
                    slots=[dict(id="lt:1/1/1", planned_type="ndps-c", unlock=True)],
                    appliques=[dict(id="ntio-1", planned_type="ncnc-d")],
                    protection_groups=[dict(id=33, admin_status="lock", eps_quenchfactor=0)],
                ),
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])
