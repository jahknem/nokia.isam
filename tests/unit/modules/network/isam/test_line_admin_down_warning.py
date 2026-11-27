"""isam_xdsl_lines / isam_ethernet_line: overridden and identity-only deleted send
'no admin-up' (the line goes down); the state documentation must warn about it."""
import pytest
import yaml

from ansible_collections.nokia.isam.plugins.modules import isam_ethernet_line, isam_xdsl_lines
from .module_runner import run_module

CASES = [
    ("isam_xdsl_lines", isam_xdsl_lines, "name",
     "configure xdsl line 1/1/3/1 service-profile 13 admin-up\nconfigure xdsl line 1/1/3/2 service-profile 13 admin-up\n",
     "1/1/3/1", "1/1/3/2", "configure xdsl line 1/1/3/2 "),
    ("isam_ethernet_line", isam_ethernet_line, "if_index",
     "configure ethernet line 1/1/8/1 port-type uni admin-up\nconfigure ethernet line 1/1/8/2 port-type uni admin-up\n",
     "1/1/8/1", "1/1/8/2", "configure ethernet line 1/1/8/2 "),
]


@pytest.mark.parametrize("module_name,module,ident,device,kept,other,prefix", CASES)
def test_overridden_and_identity_deleted_take_lines_down_and_docs_warn(monkeypatch, module_name, module, ident, device,
                                                                       kept, other, prefix):
    over = run_module(monkeypatch, module_name, {"state": "overridden", "config": [{ident: kept, "admin_up": True}]}, device)
    assert any(c.startswith(prefix) and "no admin-up" in c for c in over["commands"]), over["commands"]
    deleted = run_module(monkeypatch, module_name, {"state": "deleted", "config": [{ident: other}]}, device)
    assert any(c.startswith(prefix) and "no admin-up" in c for c in deleted["commands"]), deleted["commands"]

    state_doc = " ".join(yaml.safe_load(module.DOCUMENTATION)["options"]["state"]["description"])
    assert "no admin-up" in state_doc and "WARNING" in state_doc
