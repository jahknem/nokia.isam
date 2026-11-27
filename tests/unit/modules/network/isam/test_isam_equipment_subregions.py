"""isam_equipment: new sub-regions (diagnostics sfp, protection-element, rack,
external-link-assign/host) and the envbox/isam settings blocks."""
from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_equipment
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args

ignore_provider_arg = True


class TestIsamEquipmentSubregions(TestIsamModule):
    module = isam_equipment

    def setUp(self):
        super(TestIsamEquipmentSubregions, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamEquipmentSubregions, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_parsed_new_subregions(self):
        running = dedent("""
            configure equipment diagnostics sfp ntio-1:sfp:2 rssi-prof-id 3 rssi-state high
            configure equipment protection-element nt-a redcy-ctrl-status active
            configure equipment rack 1 description Row-A
            configure equipment external-link-assign ntio-1:sfp:2 remote lt:1/1/9
            configure equipment external-link-host ntio-1:sfp:2 direction east
            configure equipment envbox enable-supervise
            configure equipment isam description Lab-MSAN
        """)
        set_module_args(dict(running_config=running, state="parsed"), ignore_provider_arg)
        parsed = self.execute_module(changed=False)["parsed"]
        assert parsed["diagnostics_sfp"][0]["rssi_prof_id"] == 3
        assert parsed["diagnostics_sfp"][0]["rssi_state"] == "high"
        assert parsed["protection_elements"][0]["redcy_ctrl_status"] == "active"
        assert parsed["racks"][0]["description"] == "Row-A"
        assert parsed["external_link_assigns"][0]["remote"] == "lt:1/1/9"
        assert parsed["external_link_hosts"][0]["direction"] == "east"
        assert parsed["envbox"]["enable_supervise"] is True
        assert parsed["isam"]["description"] == "Lab-MSAN"

    def test_rendered_new_subregions(self):
        set_module_args(dict(state="rendered", config={
            "racks": [{"id": "1", "description": "Row-A"}],
            "diagnostics_sfp": [{"id": "ntio-1:sfp:2", "rssi_prof_id": 3}],
            "envbox": {"enable_supervise": True},
            "isam": {"description": "Lab-MSAN"},
        }), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        assert "configure equipment rack 1 description Row-A" in rendered
        assert "configure equipment diagnostics sfp ntio-1:sfp:2 rssi-prof-id 3" in rendered
        assert "configure equipment envbox enable-supervise" in rendered
        assert "configure equipment isam description Lab-MSAN" in rendered

    def test_merged_rack_idempotent(self):
        class FakeConn:
            def get(self, cmd):
                return "configure equipment rack 1 description Row-A\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="merged", config={"racks": [{"id": "1", "description": "Row-A"}]}), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_deleted_resets_singleton_and_list(self):
        class FakeConn:
            def get(self, cmd):
                return "configure equipment rack 1 description Row-A\nconfigure equipment envbox enable-supervise\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="deleted", config={
            "racks": [{"id": "1"}], "envbox": {},
        }), ignore_provider_arg)
        result = self.execute_module(changed=True)
        assert "configure equipment rack 1 no description" in result["commands"]
        assert "configure equipment envbox no enable-supervise" in result["commands"]
