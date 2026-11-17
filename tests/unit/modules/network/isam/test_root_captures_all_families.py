"""Every facts family reads the lab root captures without failing.

`info configure flat` (configured) and `info configure detail flat` (also defaults)
of a real ISAM. Each family gets its own slice (select_resource_config) like the
shared-snapshot read of isam_facts; an unknown keyword must never fail the read.
Skips when the captures (kept outside the repo) are absent.
"""
import os

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts import facts as facts_module
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import select_resource_config
from .isam_module import set_module_args

CAPTURES = os.environ.get("ISAM_ROOT_CAPTURES") or os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    *([os.pardir] * 6 + ["pon-migration-planner", ".local"])
)
FILES = {"configured": "root-flat.txt", "detail": "root-detail-flat.txt"}
_TEXT = {}


def capture(kind):
    path = os.path.join(CAPTURES, FILES[kind])
    if not os.path.exists(path):
        pytest.skip("lab capture not available")
    if kind not in _TEXT:
        with open(path) as handle:
            _TEXT[kind] = handle.read()
    return _TEXT[kind]


class _Failed(Exception):
    pass


@pytest.mark.parametrize("kind", sorted(FILES))
@pytest.mark.parametrize("resource", sorted(facts_module.FACT_RESOURCE_SUBSETS))
def test_family_reads_the_root_capture(monkeypatch, kind, resource):
    text = capture(kind)

    def fail_json(self, **result):
        raise _Failed(result.get("msg"))

    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)
    set_module_args({"state": "gathered"}, True)
    module = basic.AnsibleModule(argument_spec={"state": {"type": "str"}, "config": {"type": "raw"}}, supports_check_mode=True)
    data = select_resource_config(text, resource) or "\n"
    facts = {"ansible_network_resources": {}}
    try:
        facts_module.FACT_RESOURCE_SUBSETS[resource](module).populate_facts(None, facts, data)
    except _Failed as exc:  # message names unsupported keys, never values
        pytest.fail("%s fails on the %s capture: %s" % (resource, kind, exc))
