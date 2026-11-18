from ansible_collections.nokia.isam.tests.unit.compat.mock import MagicMock, patch
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

    def test_deleted_is_idempotent_for_unknown_interface(self):
        self.module = isam_efm_oam_interface
        # The module reads the device: an empty EFM OAM configuration.
        device = MagicMock()
        device.get.return_value = ""
        patcher = patch(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.efm_oam.efm_oam.get_resource_connection",
            return_value=device,
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        set_module_args({
            "state": "deleted",
            "config": [{"name": "1/1/1/1"}],
            "_ansible_check_mode": True,
        }, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["commands"], [])


PORT = "configure efm-oam interface 1/1/6/5 admin-up response-intvl 7\n"


def _efm(monkeypatch, state, config, running=PORT):
    from .module_runner import run_module

    return run_module(monkeypatch, "isam_efm_oam_interface", {"state": state, "config": config}, running)["commands"]


def test_merged_compares_with_the_device_and_keeps_unnamed_attributes(monkeypatch):
    """Lab ISAM: merged re-sent the whole port every run and reset unnamed intervals."""
    assert _efm(monkeypatch, "merged", [{"name": "1/1/6/5", "admin_up": True}]) == []
    assert _efm(monkeypatch, "merged", [{"name": "1/1/6/5", "keep_alive_intvl": "5"}]) == [
        "configure efm-oam interface 1/1/6/5 keep-alive-intvl 5"]
    assert _efm(monkeypatch, "merged", [{"name": "1/1/6/7", "admin_up": True}], running="") == [
        "configure efm-oam interface 1/1/6/7 admin-up"]


def test_replaced_overridden_and_deleted_reset_to_the_defaults(monkeypatch):
    assert _efm(monkeypatch, "replaced", [{"name": "1/1/6/5", "admin_up": True}]) == [
        "configure efm-oam interface 1/1/6/5 no response-intvl"]
    assert _efm(monkeypatch, "overridden", [{"name": "1/1/6/7", "admin_up": True}]) == [
        "configure efm-oam interface 1/1/6/7 admin-up",
        "configure efm-oam interface 1/1/6/5 no admin-up no response-intvl"]
    assert _efm(monkeypatch, "deleted", [{"name": "1/1/6/5"}]) == [
        "configure efm-oam interface 1/1/6/5 no admin-up no response-intvl"]
    assert _efm(monkeypatch, "deleted", [{"name": "1/1/6/5"}], running="") == []


def test_an_interval_at_its_device_default_equals_the_unset_interval(monkeypatch):
    """Lab ISAM: 'response-intvl 5' is the default and not shown afterwards."""
    running = "configure efm-oam interface 1/1/6/5 admin-up\n"
    assert _efm(monkeypatch, "merged", [{"name": "1/1/6/5", "response_intvl": "5"}], running) == []
    assert _efm(monkeypatch, "merged", [{"name": "1/1/6/5", "keep_alive_intvl": "300"}], running) == []


def test_deleted_named_setting_keeps_the_others(monkeypatch):
    assert _efm(monkeypatch, "deleted", [{"name": "1/1/6/5", "admin_up": True}]) == [
        "configure efm-oam interface 1/1/6/5 no admin-up"]
