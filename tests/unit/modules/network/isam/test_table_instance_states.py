"""Replacing named instances must never remove their siblings."""
import pytest

from .module_runner import run_module


CASES = [
    ("isam_voice_sip", {"vsp": [{"name": "vsp1", "domain_name": "example.org", "ta4": 6000}]},
     "configure voice sip vsp vsp1 domain-name example.org tinfo 1200 ta4 5000 timer-b 65000\n"
     "configure voice sip vsp vsp2 domain-name other.example\n",
     "configure voice sip vsp vsp1 no tinfo ta4 6000", "configure voice sip no vsp vsp2"),
    ("isam_software_mngt", {"oswp": [{"id": "1", "auto_verify": "enabled"}]},
     "configure software-mngt oswp 1 activate after-download\nconfigure software-mngt oswp 2 no auto-verify\n",
     "configure software-mngt oswp 1 no activate auto-verify enabled", "configure software-mngt no oswp 2"),
]


@pytest.mark.parametrize("module,config,device,update,remove", CASES, ids=[case[0] for case in CASES])
def test_replaced_updates_named_instance_only(monkeypatch, module, config, device, update, remove):
    result = run_module(monkeypatch, module, {"state": "replaced", "config": config}, device)
    assert result["commands"] == [update]
    assert remove not in result["commands"]


@pytest.mark.parametrize("module,config,device,update,remove", CASES, ids=[case[0] for case in CASES])
def test_overridden_still_removes_unnamed_instances(monkeypatch, module, config, device, update, remove):
    result = run_module(monkeypatch, module, {"state": "overridden", "config": config}, device)
    assert result["commands"] == [remove, update]
