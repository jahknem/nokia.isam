from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_equipment_onts
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


class TestIsamEquipmentOntsModule(TestIsamModule):
    module = isam_equipment_onts

    def setUp(self):
        super(TestIsamEquipmentOntsModule, self).setUp()

        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()

        self.mock_get_config = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.equipment_onts.equipment_onts.Equipment_ontsFacts.get_config"
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
        super(TestIsamEquipmentOntsModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_config.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_equipment_onts_rendered(self):
        set_module_args(
            dict(
                config=dict(
                    interfaces=[
                        dict(
                            ont_idx="1/1/5/1/1",
                            sw_ver_pland="auto",
                            sernum="ALCL:F9772423",
                            fec_up="disable",
                            admin_state="up",
                        )
                    ],
                    slots=[
                        dict(
                            ont_slot_idx="1/1/5/1/1/1",
                            planned_card_type="ethernet",
                            plndnumdataports=1,
                            plndnumvoiceports=0,
                        )
                    ],
                    sw_ctrls=[
                        dict(
                            sw_ctrl_id=1,
                            hw_version="3FE47211AB*",
                            ont_variant="DO",
                        )
                    ],
                ),
                state="rendered",
            ),
            ignore_provider_arg,
        )
        commands = [
            "configure equipment ont interface 1/1/5/1/1 sw-ver-pland auto",
            "configure equipment ont interface 1/1/5/1/1 sernum ALCL:F9772423",
            "configure equipment ont interface 1/1/5/1/1 fec-up disable",
            "configure equipment ont interface 1/1/5/1/1 admin-state up",
            "configure equipment ont slot 1/1/5/1/1/1 planned-card-type ethernet",
            "configure equipment ont slot 1/1/5/1/1/1 plndnumdataports 1",
            "configure equipment ont slot 1/1/5/1/1/1 plndnumvoiceports 0",
            "configure equipment ont sw-ctrl 1 hw-version 3FE47211AB*",
            "configure equipment ont sw-ctrl 1 ont-variant DO",
        ]
        result = self.execute_module(changed=False)
        self.assertEqual(set(result["rendered"]), set(commands))

    def test_isam_equipment_onts_parsed(self):
        set_module_args(
            dict(
                running_config=dedent(
                    """\
                    configure equipment
                    ont
                    interface 1/1/5/1/1 sw-ver-pland auto
                      sernum ALCL:F9772423
                      subslocid WILDCARD
                      fec-up disable
                      sw-dnload-version auto
                      plnd-var DO
                      enable-aes enable
                      planned-us-rate nominal-line-rate
                      admin-state up
                    exit
                    slot 1/1/5/1/1/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0
                    exit
                    sw-ctrl 1 hw-version 3FE47211AB*
                      ont-variant DO
                    exit
                    exit
                    """
                ),
                state="parsed",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        parsed = result["parsed"]
        self.assertEqual(parsed["interfaces"][0]["ont_idx"], "1/1/5/1/1")
        self.assertEqual(parsed["interfaces"][0]["admin_state"], "up")
        self.assertEqual(parsed["slots"][0]["plndnumdataports"], 1)
        self.assertEqual(parsed["sw_ctrls"][0]["ont_variant"], "DO")

    def test_isam_equipment_onts_gathered(self):
        self.get_config.return_value = dedent(
            """\
            configure equipment
            ont
            interface 1/1/5/1/1 sw-ver-pland auto
              sernum ALCL:F9772423
              admin-state up
            exit
            exit
            """
        )
        set_module_args(dict(state="gathered"), ignore_provider_arg)
        result = self.execute_module(changed=False)
        self.assertEqual(result["gathered"]["interfaces"][0]["sernum"], "ALCL:F9772423")

    def test_isam_equipment_onts_merged(self):
        self.get_config.return_value = dedent(
            """\
            configure equipment
            ont
            interface 1/1/5/1/1 sw-ver-pland auto
              sernum ALCL:F9772423
              admin-state down
            exit
            exit
            """
        )
        set_module_args(
            dict(
                config=dict(
                    interfaces=[dict(ont_idx="1/1/5/1/1", admin_state="up")]
                ),
                state="merged",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=True)
        self.assertEqual(
            result["commands"],
            ["configure equipment ont interface 1/1/5/1/1 admin-state up"],
        )
