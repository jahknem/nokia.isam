from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_l2cp, isam_l2cp_session, isam_l2cp_user_port
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2cp.l2cp import L2cp
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2cp import L2cpTemplate
from .isam_module import TestIsamModule, set_module_args


class TestL2cp(TestIsamModule):
    def test_global_merged_is_idempotent(self):
        resource = L2cp.__new__(L2cp)
        resource.template = L2cpTemplate()
        resource.state = "merged"
        resource.want = [{"name": "l2cp", "partition_type": "fixed-assigned"}]
        resource.have = [{"name": "l2cp", "partition_type": "fixed-assigned"}]
        resource.commands = []

        resource.commands = []
        merged = dict(resource.have[0])
        merged.update(resource.want[0])
        if merged != resource.have[0]:
            resource.commands = resource.template.render([merged])

        assert resource.commands == []

    def test_global_rendered_and_parsed(self):
        self.module = isam_l2cp
        set_module_args({"state": "rendered", "config": [{"name": "l2cp", "partition_type": "fixed-assigned"}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure l2cp partition-type fixed-assigned"])

        set_module_args({"state": "parsed", "running_config": "configure l2cp partition-type fixed-assigned"}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "l2cp", "partition_type": "fixed-assigned"}])

    def test_deleted_is_idempotent_when_l2cp_is_unconfigured(self):
        self.module = isam_l2cp
        set_module_args({"state": "deleted", "config": [{"name": "l2cp"}], "_ansible_check_mode": True}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])

    def test_session_rendered_and_parsed(self):
        self.module = isam_l2cp_session
        config = [{"name": "1", "bras_ip_address": "192.0.2.10", "topo_discovery": "disabled", "sig_partition_id": False}]
        set_module_args({"state": "rendered", "config": config}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], [
            "configure l2cp session 1 bras-ip-address 192.0.2.10 gsmp-version 3 gsmp-sub-version 1 encap-type tcp "
            "topo-discovery disabled layer2-oam enabled alive-timer 250 port-reprt-shaper 10 aggr-reprt-shaper 10 "
            "tcp-retry-time 10 gsmp-retry-time 10 dslam-name 00 : 00 : 00 partition-id 0 window-size 10 tcp-port 6068 "
            "router-instance base no sig-partition-id"
        ])

        running = dedent("""\
            configure l2cp session 1 bras-ip-address 192.0.2.10 topo-discovery disabled no sig-partition-id
        """)
        set_module_args({"state": "parsed", "running_config": running}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "1", "bras_ip_address": "192.0.2.10", "topo_discovery": "disabled", "sig_partition_id": False}])

    def test_user_port_rendered_and_parsed(self):
        self.module = isam_l2cp_user_port
        set_module_args({"state": "rendered", "config": [{"name": "1/1/1/1", "partition_id": "7"}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure l2cp user-port 1/1/1/1 partition-id 7"])

        set_module_args({"state": "parsed", "running_config": "configure l2cp no user-port 1/1/1/1 partition-id"}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "1/1/1/1", "partition_id": None}])
