from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_pppoe_client_interface
from ansible_collections.nokia.isam.plugins.modules import isam_pppoe_client_ppp_profile
from ansible_collections.nokia.isam.plugins.modules import isam_pppoel2_statistics
from .isam_module import TestIsamModule, set_module_args


class TestPppoeResources(TestIsamModule):
    def test_profile_rendered(self):
        self.module = isam_pppoe_client_ppp_profile
        set_module_args({"state": "rendered", "config": [{"name": "home", "ipversion": "dual", "authproto": "pap", "mru": 1492}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure pppoe-client ppp-profile home ipversion dual authproto pap mru 1492"])

    def test_profile_parsed(self):
        self.module = isam_pppoe_client_ppp_profile
        set_module_args({"state": "parsed", "running_config": dedent("""\
            configure pppoe-client ppp-profile home ipversion dual authproto pap mru 1492
        """)}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "home", "ipversion": "dual", "authproto": "pap", "mru": 1492}])

    def test_interface_rendered(self):
        self.module = isam_pppoe_client_interface
        set_module_args({"state": "rendered", "config": [{"name": "1/1/1:100", "client_id": 1, "profile_name": "home", "username": "u", "password": "p", "pbit": 3}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(
            result["rendered"],
            ["configure pppoe-client interface 1/1/1:100 client-id 1 profile-name home username u password p pbit 3"],
        )

    def test_l2_statistics_parse_and_render(self):
        self.module = isam_pppoel2_statistics
        set_module_args({"state": "parsed", "running_config": "configure pppoel2 no statistics vlan-port 1/1/1:100"}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{"name": "vlan-port 1/1/1:100", "enabled": False}])

        set_module_args({"state": "rendered", "config": [{"name": "vlan-port 1/1/1:100", "enabled": True}]}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure pppoel2 statistics vlan-port 1/1/1:100"])
