from ansible_collections.nokia.isam.plugins.modules import isam_bridges
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args


ignore_provider_arg = True


# NOTE: The argspec for vlan_id suboptions has several prior_* bool fields
# with default: "none" (string), which Ansible rejects.  As a workaround
# we explicitly pass False for every such field in vlan_id entries.
# This can be removed once the argspec defaults are corrected to None.
_VLAN_BOOL_DEFAULTS = {
    k: False
    for k in (
        "prior_best_effort",
        "prior_background",
        "prior_spare",
        "prior_exc_effort",
        "prior_ctrl_load",
        "prior_less_100ms",
        "prior_less_10ms",
        "prior_nw_ctrl",
    )
}


class TestIsamBridgesModule(TestIsamModule):
    module = isam_bridges

    def setUp(self):
        super(TestIsamBridgesModule, self).setUp()

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
        super(TestIsamBridgesModule, self).tearDown()
        self.get_resource_connection.stop()
        self.get_resource_connection_config.stop()
        self.get_resource_connection_facts.stop()

    def test_isam_bridges_gathered_empty(self):
        # With empty output, gathered should be an empty list
        class FakeConn:
            def get(self, cmd):
                return ""

        self.get_resource_connection_facts.return_value = FakeConn()

        set_module_args(dict(state="gathered"), ignore_provider_arg)

        result = self.execute_module(changed=False)
        self.assertEqual(result.get("gathered"), [])

    def test_isam_bridges_rendered_ageing_time_only(self):
        """Rendered with only top-level ageing_time."""
        set_module_args(
            dict(
                config={"ageing_time": 300},
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge ageing-time 300",
        ])

    def test_isam_bridges_rendered_port_basic(self):
        """Rendered with port-level pvid, default-priority, mac-learn-off."""
        set_module_args(
            dict(
                config={
                    "ageing_time": 300,
                    "port": [{
                        "port": "1/1/8/1",
                        "pvid": 99,
                        "default-priority": 0,
                        "mac-learn-off": True,
                    }],
                },
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge ageing-time 300",
            "configure bridge port 1/1/8/1",
            "configure bridge port 1/1/8/1 pvid 99",
            "configure bridge port 1/1/8/1 default-priority 0",
            "configure bridge port 1/1/8/1 mac-learn-off",
        ])

    def test_isam_bridges_rendered_vlan(self):
        """Rendered with vlan_id entries including tag."""
        vlan_entry = dict(
            {"id": "100", "tag": "untagged"},
            **{"prior_best_effort": False,
               "prior_background": False,
               "prior_spare": False,
               "prior_exc_effort": False,
               "prior_ctrl_load": False,
               "prior_less_100ms": False,
               "prior_less_10ms": False,
               "prior_nw_ctrl": False},
        )
        set_module_args(
            dict(
                config={
                    "ageing_time": 300,
                    "port": [{
                        "port": "1/1/8/1",
                        "vlan_id": [vlan_entry],
                    }],
                },
                state="rendered",
            ),
            ignore_provider_arg,
        )
        result = self.execute_module(changed=False)
        self.assertEqual(result.get("rendered"), [
            "configure bridge ageing-time 300",
            "configure bridge port 1/1/8/1",
            "configure bridge port 1/1/8/1 vlan-id 100 tag untagged",
        ])

    def test_isam_bridges_parsed_requires_running_config(self):
        set_module_args(dict(state="parsed"), ignore_provider_arg)
        self.execute_module(failed=True)
