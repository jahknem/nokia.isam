from textwrap import dedent
import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_cfm
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from .isam_module import TestIsamModule, set_module_args


class TestCfmModule(TestIsamModule):
    module = isam_cfm

    def setUp(self):
        super(TestCfmModule, self).setUp()
        self.connection_patch = patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection")
        self.connection_patch.start()
        self.facts_patch = patch("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.cfm.cfm.CfmFacts.get_facts")
        self.get_facts = self.facts_patch.start()
        self.get_facts.return_value = ({"ansible_network_resources": {"isam_cfm": {"domains": [], "slm": {}, "y1731pm": []}}}, [])

    def tearDown(self):
        self.facts_patch.stop()
        self.connection_patch.stop()
        super(TestCfmModule, self).tearDown()

    def test_rendered_core_domain_and_mep(self):
        set_module_args({"state": "rendered", "config": {"domains": [{"domain_index": 1, "name": "string operator", "level": 3, "associations": [{"association_index": 2, "ccm_interval": "10", "meps": [{"mepid": 7, "location": "slot:1/1/1"}]}]}]}}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["rendered"], ["configure cfm domain 1 name string operator level 3", "configure cfm domain 1 association 2 ccm-interval 10", "configure cfm domain 1 association 2 mep 7 location slot:1/1/1"])

    def test_parsed(self):
        self.facts_patch.stop()
        set_module_args({"state": "parsed", "running_config": dedent("""\
            configure cfm domain 1 name string operator level 3
            configure cfm domain 1 association 2 mep 7 location slot:1/1/1 cci-enable
        """)}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"]["domains"][0]["level"], 3)
        self.assertTrue(result["parsed"]["domains"][0]["associations"][0]["meps"][0]["cci_enable"])

    def test_merged_check_mode(self):
        self.get_facts.return_value = ({"ansible_network_resources": {"isam_cfm": {"domains": [{"domain_index": 1, "name": "string operator", "level": 3}], "slm": {}, "y1731pm": []}}}, [])
        set_module_args({"state": "merged", "config": {"domains": [{"domain_index": 1, "name": "string operator", "level": 3, "associations": [{"association_index": 2, "ccm_interval": "10"}]}]}}, True)
        result = self.execute_module(changed=True)
        self.assertEqual(result["commands"], ["configure cfm domain 1 association 2 ccm-interval 10"])


def test_y1731pm_short_lines_do_not_raise():
    """Lines shorter than the 8-word y1731pm identity used to raise IndexError (guard was len < 6, read words[7])."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.cfm import CfmTemplate

    lines = [
        "configure cfm y1731pm domain 1 association 2 mep 3",
        "configure cfm y1731pm domain 1 association 2 mep 3 session-id",
        "configure cfm y1731pm domain 1 association 2 mep",
        "configure cfm y1731pm domain 1 association 2 xx 3 session-id 4",
        "configure cfm y1731pm domain 1 association 2 mep 3 session-id 4 type dmm target-mac 00:11:22:33:44:55 priority 5",
    ]
    parsed = CfmTemplate(lines=lines).parse()
    assert parsed["y1731pm"] == [{
        "domain_index": 1, "association": 2, "mep": 3, "session_id": 4,
        "type": "dmm", "target_mac": "00:11:22:33:44:55", "priority": 5,
    }]


CFM_CONFIG = {"domains": [{"domain_index": 1, "name": "string operator", "level": 3},
                          {"domain_index": 2, "name": "string other", "level": 4}],
              "slm": {"inactivity_time": 60}, "y1731pm": []}


def _cfm(monkeypatch, state, config, have=None):
    from copy import deepcopy
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.cfm.cfm import CfmFacts
    from .module_runner import run_module

    monkeypatch.setattr(CfmFacts, "get_facts", lambda *args, **kwargs:
                        ({"ansible_network_resources": {"isam_cfm": deepcopy(CFM_CONFIG if have is None else have)}}, []))
    return run_module(monkeypatch, "isam_cfm", {"state": state, "config": config})


def test_deleted_slm_never_deletes_domains(monkeypatch):
    assert _cfm(monkeypatch, "deleted", {"slm": {}})["commands"] == ["configure cfm slm no inactivity-time"]


def test_replaced_slm_never_deletes_domains(monkeypatch):
    assert _cfm(monkeypatch, "replaced", {"slm": {"inactivity_time": 90}})["commands"] == [
        "configure cfm slm inactivity-time 90"]


@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_domain_name_change_fails_without_implicitly_deleting_the_domain(monkeypatch, state):
    result = _cfm(monkeypatch, state, {"domains": [
        {"domain_index": 1, "name": "string renamed", "level": 3}, CFM_CONFIG["domains"][1]]})
    assert result.get("failed") and "cannot be modified" in result["msg"]


def test_domain_index_is_the_identity_when_only_selecting_existing_domains(monkeypatch):
    assert _cfm(monkeypatch, "replaced", {"domains": [{"domain_index": 1}, {"domain_index": 2}]})["commands"] == []


def test_domain_creation_requires_name_and_level(monkeypatch):
    result = _cfm(monkeypatch, "merged", {"domains": [{"domain_index": 3, "level": 2}]})
    assert result.get("failed") and "requires both name and level" in result["msg"]


def test_deleted_domain_preserves_slm_and_other_domains(monkeypatch):
    assert _cfm(monkeypatch, "deleted", {"domains": [{"domain_index": 1}]})["commands"] == [
        "configure cfm no domain 1"]


def test_remote_mep_and_pm_configuration_is_idempotent(monkeypatch):
    config = {"domains": [{"domain_index": 1, "associations": [{"association_index": 2,
               "remote_meps": [7], "meps": [{"mepid": 3, "active_remote_meps": [8]}]}]}],
              "y1731pm": [{"domain_index": 1, "association": 2, "mep": 3, "session_id": 200,
                           "type": "dmm", "target_mac": "00:11:22:33:44:55", "priority": 5}]}
    assert _cfm(monkeypatch, "merged", config, have=config)["commands"] == []


def test_pm_identity_includes_session_id(monkeypatch):
    have = {"y1731pm": [{"domain_index": 1, "association": 2, "mep": 3, "session_id": 200, "priority": 5}]}
    want = {"y1731pm": [{"domain_index": 1, "association": 2, "mep": 3, "session_id": 201, "priority": 5}]}
    assert _cfm(monkeypatch, "merged", want, have=have)["commands"] == [
        "configure cfm y1731pm domain 1 association 2 mep 3 session-id 201 priority 5"]
