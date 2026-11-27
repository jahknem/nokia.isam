"""Relations and module semantics agree: an entry the device creates with its object
(relations ``created_with``) is reset, never removed.

The relations knew on 2026-11-25 that the ANI and NTP entries come with the ONT, while
the modules still sent ``no tca-thresh`` / ``configure ntp no ont`` (no effect on the
device) until 2026-11-27. This check runs every ``created_with`` section through its
module, with the running configuration of its targeted case, in ``deleted`` and
``overridden``: no command may remove the entry itself. A removal names the entry's
identity last, after a ``no``; a reset ends with the attribute it resets.
"""
import importlib
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import export_catalog

from .module_runner import HEADER, run_module

CASES = {}
for _path in sorted(pathlib.Path(__file__).parent.glob("targeted_cases_*.py")):
    CASES.update(importlib.import_module("." + _path.stem, __package__).CASES)


ONT, VLAN_UNI = "1/1/5/1/3", "1/1/5/1/3/1/1"
# Object kinds of a section whose targeted case covers another kind: a minimal case each.
EXTRA = {
    "interfaces.config:ont": ("isam_interfaces", [{"name": "ont:" + ONT}],
                              ["configure interface port ont:%s user TEST-1" % ONT]),
    "interfaces.config:vlan_port": ("isam_interfaces", [{"name": "vlan-port:%s:99" % VLAN_UNI}],
                                    ["configure interface port vlan-port:%s:99 user TEST-1" % VLAN_UNI]),
    "qos_interfaces.config:ont": ("isam_qos_interfaces", [{"name": "ont:" + ONT}],
                                  ["configure qos interface ont:%s scheduler-node name:A" % ONT]),
    "qos_interfaces.config:vlan_port": ("isam_qos_interfaces", [{"name": "vlan:%s:99" % VLAN_UNI}],
                                        ["configure qos interface vlan:%s:99 scheduler-node name:A" % VLAN_UNI]),
    # The targeted case sets only attributes isam_link_agg's deleted does not reset.
    "link_agg.groups:lag": ("isam_link_agg", {"groups": [{"id": "1/1/8/10"}]},
                            ["configure link-agg group 1/1/8/10 max-active-port 4"]),
    "qos_interfaces.config:pon": ("isam_qos_interfaces", [{"name": "pon:1/1/5/3"}],
                                  ["configure qos interface pon:1/1/5/3 scheduler-node name:A"]),
}


def _instances(config, section):
    if section == "config":
        return config if isinstance(config, list) else []
    for part in section.split("."):
        config = config.get(part) if isinstance(config, dict) else None
    return config if isinstance(config, list) else []


def _created_with_cases():
    found, untested = [], []
    for entry in export_catalog()["created_with"]:
        resource, section = entry["resource"], entry["section"]
        name = "%s.%s:%s" % (resource, section, entry["object"])
        case = CASES.get(resource if section == "config" else "%s:%s" % (resource, section)) \
            or CASES.get("%s:%s" % (resource, section))
        if name in EXTRA:
            module, config, lines = EXTRA[name]
            case = {"module": module, "config": config, "lines": lines}
        field = TARGETED_GATHER[resource][section]
        instances = _instances(case["config"], section) if case else []
        values = [item.get(field) for item in instances if isinstance(field, str)]
        if not values or (entry["prefix"] and not str(values[0]).startswith(entry["prefix"])):
            untested.append(name)
            continue
        found.append(pytest.param(case, section, str(values[0]),
                                  id=name))
    return found, untested


FOUND, UNTESTED = _created_with_cases()


def test_every_created_with_section_is_checked():
    assert UNTESTED == [], "created_with sections without a case: %s" % UNTESTED


def _removes(command, identity):
    tokens = command.split()
    return bool(tokens) and tokens[-1] == identity and "no" in tokens[:-1]


@pytest.mark.parametrize("case,section,identity", FOUND)
@pytest.mark.parametrize("state", ["deleted", "overridden"])
def test_an_entry_created_with_its_object_is_reset_never_removed(monkeypatch, case, section, identity, state):
    running = HEADER + "\n".join(case["lines"]) + "\n"
    result = run_module(monkeypatch, case["module"], {"state": state, "config": case["config"]}, running)
    assert not result.get("failed"), result.get("msg")
    commands = result.get("commands") or []
    removals = [c for c in commands if _removes(c, identity)]
    assert removals == [], removals
    if state == "deleted":
        # The running entry carries a non-default value: deleting it must reset that,
        # so the check above saw real commands.
        assert commands, "deleted produced no command for %s" % identity
