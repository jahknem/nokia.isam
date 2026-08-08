from textwrap import dedent

from ansible_collections.nokia.isam.plugins.modules import isam_efm_oam_interface
from .isam_module import TestIsamModule, set_module_args


class TestEfmOam(TestIsamModule):
    def test_rendered_core_configuration(self):
        self.module = isam_efm_oam_interface
        set_module_args({
            "state": "rendered",
            "config": [{"name": "1/1/1/1", "admin_up": True, "passive_mode": False,
                        "keep_alive_intvl": "120", "response_intvl": "5"}],
        }, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], [
            "configure efm-oam interface 1/1/1/1 admin-up no passive-mode keep-alive-intvl 120 response-intvl 5"
        ])

    def test_parsed_core_configuration(self):
        self.module = isam_efm_oam_interface
        set_module_args({
            "state": "parsed",
            "running_config": dedent("""\
                configure efm-oam interface 1/1/1/1 admin-up no passive-mode keep-alive-intvl 120 response-intvl 5
            """),
        }, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], [{
            "name": "1/1/1/1", "admin_up": True, "passive_mode": False,
            "keep_alive_intvl": "120", "response_intvl": "5",
        }])
