# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Fixture-driven integration tests for the scoped targeted families.

For every targeted resource family that has a sanitized live-capture config
fixture (``tests/fixtures/<resource>/<variant>/``, mostly the r6.2.04m
capture on the 7330 FTTN lab device), the real module is driven through
``state: gathered`` against a fake device answering from the fixture output:

* whole read (no ``config``): the fixture output parses into the family's
  facts, the exact whole-read command set is sent, and no ``read_outcomes``
  are carried (the legacy contract);
* targeted read of a real instance from the fixture: only the per-instance
  command(s) are sent (never the whole read), the gathered section holds
  exactly the fixture entries under the addressed identity (siblings are
  scoped out; an identity that is not unique returns all its entries), and
  the outcome is ``present``;
* targeted read of an identity the fixture does not contain: the device's
  "instance does not exist" signal classifies it ``confirmed_absent``.

The whole-node catalog families (``interface_alarms``, ``isam_vlan_global``)
are covered by ``test_whole_node_families.py`` instead -- their contract is
different (one node read, ``unknown`` for catalog absence).

Families without a config fixture (``igmp``, ``isam_dhcp_relay``,
``isam_system_security``, ``l2uni_onts``, ``mcast_control``, ``qos_global``,
``qos_tca``, ``uni_onts``, ``xdsl_inm``, ``xdsl_onts``) remain covered by
the synthetic-data e2e suite (``test_targeted_gathered.py``).
"""
import importlib
import re
import sys
from pathlib import Path

import pytest
import yaml
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import (
    TARGETED_GATHER,
    read_scope,
)

from .isam_module import set_module_args
from .targeted_harness import Device, _ModuleDone, full_commands, outcome_by_selector, outcomes

FIXTURES = Path(__file__).resolve().parents[4] / "fixtures"
MODULES = FIXTURES.parent.parent / "plugins" / "modules"


def _module_name(resource):
    """The module for a facts resource name (isam_ prefix, not doubled)."""
    name = resource if resource.startswith("isam_") else "isam_" + resource
    if not (MODULES / (name + ".py")).exists():
        raise AssertionError("no module %s for resource %s" % (name, resource))
    return name


def _discover():
    """(resource, variant, lines) for every scoped targeted family with a
    whole-node config fixture.

    Fixture directories are named after the resource, except that resources
    already carrying the isam_ prefix are stored without it (cfm -> isam_cfm).
    Only ``info configure`` fixtures with flat ``configure`` lines qualify
    (the fake device answers per-instance reads by prefix-matching them);
    where a family has the canonical r6.2.04m capture, only that variant is
    used (the others are single-instance or operational captures).
    """
    cases = []
    for fixture_dir in sorted(FIXTURES.iterdir()):
        if not fixture_dir.is_dir() or fixture_dir.name in ("live_scenarios", "pon_variants"):
            continue
        # the fixture dir names the resource, or the resource minus its isam_ prefix
        resource = (fixture_dir.name if fixture_dir.name in TARGETED_GATHER
                    else "isam_" + fixture_dir.name)
        if resource not in TARGETED_GATHER or read_scope(resource) == "whole_node":
            continue
        variants = [v for v in fixture_dir.iterdir() if (v / "fixture.yml").exists()]
        canonical = [v for v in variants if v.name == "r6.2.04m"]
        for variant in (canonical or sorted(variants)):
            descriptor = yaml.safe_load((variant / "fixture.yml").read_text()) or {}
            command = descriptor.get("command") or ""
            if not command.startswith("info configure"):
                continue
            lines = (variant / "output.txt").read_text().splitlines()
            if not any(line.startswith("configure ") for line in lines):
                continue
            cases.append((resource, variant.name, lines))
    return cases


CASES = _discover()
IDS = ["%s:%s" % (resource, variant) for resource, variant, _ in CASES]


def run_module(monkeypatch, module_name, args, device):
    """Drive one real module against a fake device; the module's result dict."""
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules." + module_name)

    def exit_json(self, **result):
        raise _ModuleDone(result)

    def fail_json(self, **result):
        raise _ModuleDone(dict(result, failed=True))

    with monkeypatch.context() as patch:
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: device)
        patch.setattr(basic.AnsibleModule, "exit_json", exit_json)
        patch.setattr(basic.AnsibleModule, "fail_json", fail_json)
        set_module_args(args, True)
        with pytest.raises(_ModuleDone) as raised:
            module.main()
        return raised.value.result


def section_items(data, section):
    """The instance list of a (dotted) TARGETED_GATHER section in parsed facts.

    A 'config' section is the fact list itself for list-shaped families and
    the ``config`` key for dict-shaped ones. Sections the facts do not
    populate are empty lists (the fixture may not configure them).
    """
    node = data
    if section != "config" or not isinstance(node, list):
        for part in section.split("."):
            if not isinstance(node, dict) or part not in node:
                return []
            node = node[part]
    return list(node or [])


def config_for(section, instance):
    """The module ``config`` selecting exactly one instance of ``section``."""
    if section == "config":
        return [instance]
    config = {}
    node = config
    parts = section.split(".")
    for part in parts[:-1]:
        node[part] = {}
        node = node[part]
    node[parts[-1]] = [instance]
    return config


def _field_choices(module_name, section, field):
    """The argspec ``choices`` of an identity field, if it is choice-constrained."""
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules." + module_name)
    args_cls = next(
        value for name, value in vars(module).items()
        if name.endswith("Args") and hasattr(value, "argument_spec"))
    spec = args_cls.argument_spec
    node = spec.get("config") or {}
    if section != "config":
        for part in section.split("."):
            node = (node.get("options") or {}).get(part) or {}
    elements = node.get("elements")
    if isinstance(elements, dict):
        node = elements
    return ((node.get("options") or {}).get(field) or {}).get("choices")


def fake_identity(instance, fields, module_name, section, baseline_items):
    """An identity the fixture device cannot have.

    Only the most specific identity field is altered -- the other fields of a
    composite identity stay as the fixture has them, because they may be
    choice-constrained (qos_profiles.profile_type). The altered value stays
    valid where the module validates it: a choice-constrained field becomes a
    choice the fixture does not use (isam_traps definitions); a trailing
    numeric segment (port paths, indices) is incremented; free-form names
    become a plausible absent name.
    """

    def well_formed_absent(value):
        match = re.search(r"(\d+)$", value)
        if match:
            return value[:match.start()] + str(int(match.group(1)) + 999)
        return "zz-absent-probe"

    fake = dict(instance)
    field = fields[-1]
    value = instance.get(field)
    if isinstance(value, int):
        fake[field] = 999999
        return fake
    choices = _field_choices(module_name, section, field)
    if choices:
        used = {str(entry.get(field)) for entry in baseline_items}
        unused = [choice for choice in choices if choice not in used]
        if unused:
            fake[field] = unused[0]
            return fake
        # A complete choice catalog (the isam_traps fixture lists every
        # definition): no valid-but-absent identity exists in the choice
        # space, so no absent probe is possible from this fixture.
        return None
    fake[field] = well_formed_absent(str(value))
    return fake


@pytest.mark.parametrize("resource,variant,lines", CASES, ids=IDS)
def test_scoped_family_fixture_round_trip(monkeypatch, resource, variant, lines):
    module_name = _module_name(resource)
    whole = full_commands(monkeypatch, {"module": module_name})

    # --- Phase 1: the whole read is the legacy contract ------------------------
    device = Device(lines, full=whole)
    result = run_module(monkeypatch, module_name, {"state": "gathered"}, device)
    assert not result.get("failed"), result
    assert set(device.commands) == whole, (device.commands, whole)
    assert "read_outcomes" not in result
    baseline = result["gathered"]
    # the first targeted section (registry order) the fixture actually populates
    sections = [s for s in TARGETED_GATHER[resource] if section_items(baseline, s)]
    if not sections:
        # The fixture populates no targeted section (e.g. only a scalar
        # attribute): the whole-read contract is still pinned above.
        return
    section = sections[0]
    instance = section_items(baseline, section)[0]
    field = TARGETED_GATHER[resource][section]
    fields = [field] if isinstance(field, str) else list(field)

    # --- Phase 2: a targeted read of a real instance is scoped and present -----
    device = Device(lines, full=whole)
    result = run_module(monkeypatch, module_name,
                        {"state": "gathered", "config": config_for(section, instance)}, device)
    assert not result.get("failed"), result
    assert device.commands, "the targeted read sent no command"
    assert not set(device.commands) & whole, (device.commands, whole)
    by = outcome_by_selector(result)
    assert by, result
    assert all(o["command"] == "ok" and o["existence"] == "present" for o in by.values()), \
        result.get("read_outcomes")
    # the read addresses the identity: the gathered section holds exactly the
    # fixture entries under it, no others. For unique identities that is the
    # instance alone; the system fixture shows an identity that is not unique
    # (one sntp ip-address carrying several priority entries), and the read
    # returns all of them.
    baseline_items = section_items(baseline, section)
    expected = [
        entry for entry in baseline_items
        if tuple(str(entry.get(name)) for name in fields)
        == tuple(str(instance.get(name)) for name in fields)
    ]
    assert section_items(result["gathered"], section) == expected, result.get("gathered")

    # --- Phase 3: an identity the device does not have is confirmed absent -----
    absent = fake_identity(instance, fields, module_name, section, baseline_items)
    if absent is None:
        return  # no valid-but-absent identity exists for this fixture (see fake_identity)
    device = Device(lines, full=whole)
    result = run_module(monkeypatch, module_name,
                        {"state": "gathered", "config": config_for(section, absent)},
                        device)
    assert not result.get("failed"), result
    assert outcomes(result), result
    assert all(o["existence"] == "confirmed_absent" for o in outcomes(result)), \
        result.get("read_outcomes")
