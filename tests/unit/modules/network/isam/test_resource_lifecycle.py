"""State-to-execution contract shared by ordinary resource config classes."""
from types import SimpleNamespace

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule


@pytest.mark.parametrize("state,expected", [
    ("parsed", []), ("gathered", []), ("rendered", ["generate"]),
    ("merged", ["generate", "run"]), ("replaced", ["generate", "run"]),
    ("overridden", ["generate", "run"]), ("deleted", ["generate", "run"]),
])
def test_resource_lifecycle(state, expected):
    calls = []
    result = {"changed": False}
    resource = SimpleNamespace(state=state, result=result,
                               generate_commands=lambda: calls.append("generate"),
                               run_commands=lambda: calls.append("run"))
    assert IsamResourceModule.execute_module(resource) is result
    assert calls == expected
