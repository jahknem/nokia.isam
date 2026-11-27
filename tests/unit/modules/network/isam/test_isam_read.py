"""isam_read: several isolated reads on one MSAN, each with its own outcome.

The targeted reads are checked against every targeted gathering case
(targeted_cases_*.py): isam_read must send the same commands and return the same
data as the family module with state gathered and config.
"""
import importlib
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.module_utils.network.isam import read as read_utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import (
    TARGETED_GATHER,
    read_scope,
)

from . import targeted_harness as harness
from .isam_module import set_module_args
from .test_targeted_gathered import CASES, NAMES


def run_read(monkeypatch, reads, device):
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules.isam_read")
    importlib.import_module("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts")
    for path, *_rest in read_utils.MODULE_DIRECT.values():
        importlib.import_module("ansible_collections.nokia.isam.plugins.module_utils.network.isam." + path)

    def exit_json(self, **result):
        raise harness._ModuleDone(result)

    def fail_json(self, **result):
        raise harness._ModuleDone(dict(result, failed=True))

    with monkeypatch.context() as patch:
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: device)
        patch.setattr(basic.AnsibleModule, "exit_json", exit_json)
        patch.setattr(basic.AnsibleModule, "fail_json", fail_json)
        set_module_args({"reads": reads}, True)
        with pytest.raises(harness._ModuleDone) as result:
            module.main()
        return result.value.result


def requests_of(resource, config):
    """isam_read requests naming the instances of a module config, one per instance list."""
    reads = []
    for section in sorted(harness.named_sections(config)):
        field = TARGETED_GATHER[resource][section]
        items = read_utils._section_items(config, section)
        ids = [item[field] if isinstance(field, str) else dict((name, item[name]) for name in field)
               for item in items]
        reads.append({"resource": resource, "section": section, "ids": ids})
    return reads


@pytest.mark.parametrize("name", NAMES)
def test_a_targeted_read_equals_the_family_module(monkeypatch, name):
    case = CASES[name]
    resource = harness.resource_of(name)
    full = harness.full_commands(monkeypatch, case)
    for request in requests_of(resource, case["config"]):
        config = read_utils._nest(request["section"], read_utils._section_items(case["config"], request["section"]))
        lines = case["lines"] + case["sibling"]
        direct_device = harness.Device(lines, full=full, answer=case.get("answer"))
        direct = harness.gathered(monkeypatch, case, config, direct_device)
        device = harness.Device(lines, full=full, answer=case.get("answer"))
        result = run_read(monkeypatch, [request], device)

        assert not result.get("failed") and not result["changed"], result
        (item,) = result["reads"]
        assert item["status"] == "ok", item
        assert device.commands == direct_device.commands
        expected = direct.get("gathered")
        if expected in (None, {}, []):
            expected = read_utils._empty(resource)
        assert item["data"] == read_utils.redact(expected, read_utils.family_spec(resource))
        assert item["returned_ids"] == request["ids"], item
        assert item["confirmed_absent_ids"] == [] and item["unverified_ids"] == []
        assert item["section"] == request["section"] and item["resource"] == resource


@pytest.mark.parametrize("name", NAMES)
def test_a_missing_instance_is_confirmed_absent_only_when_the_device_says_so(monkeypatch, name):
    case = CASES[name]
    resource = harness.resource_of(name)
    full = harness.full_commands(monkeypatch, case)
    for request in requests_of(resource, case["config"]):
        result = run_read(monkeypatch, [request], harness.Device([], full=full, answer=case.get("answer")))
        (item,) = result["reads"]
        assert item["status"] == "ok" and item["returned_ids"] == [], item
        if read_scope(resource) == "whole_node":
            # A catalog that does not list an instance does not establish its absence.
            assert item["unverified_ids"] == request["ids"] and item["confirmed_absent_ids"] == [], item
        else:
            assert item["confirmed_absent_ids"] == request["ids"] and item["unverified_ids"] == [], item


def test_every_no_log_field_of_the_collection_is_redacted():
    """Each argspec with no_log fields belongs to a family whose reads isam_read
    redacts by that argspec (a facts class without argument_spec would leak them)."""
    import pkgutil

    import ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec as argspecs

    with_secrets = {}
    for info in pkgutil.walk_packages(argspecs.__path__, argspecs.__name__ + "."):
        loaded = importlib.import_module(info.name)
        for value in vars(loaded).values():
            spec = getattr(value, "argument_spec", None)
            if isinstance(spec, dict) and isinstance(spec.get("config"), dict) and \
                    read_utils.no_log_paths(spec["config"].get("options")):
                with_secrets[id(spec["config"])] = info.name
    assert with_secrets, "expected argspecs with no_log fields"
    covered = set()
    for resource in read_utils.configuration_resources():
        spec = read_utils.family_spec(resource)
        if spec is not None:
            covered.add(id(spec))
    # IHUB and statistics modules are not read through isam_read.
    readable = dict((key, name) for key, name in with_secrets.items()
                    if not name.rsplit(".", 1)[-1].startswith(("ihub", "security_ext")))
    assert set(readable) <= covered, sorted(name for key, name in readable.items() if key not in covered)


def test_an_snmp_community_is_removed_where_the_argspec_puts_it():
    spec = read_utils.family_spec("isam_system_security")
    assert "snmp_communities[].name" in "|".join(read_utils.no_log_paths(spec["options"]))
    data = {"snmp": {"snmp_communities": [{"name": "s3cret", "privilege": "read-only"}]}} \
        if "snmp" in spec["options"] else None
    paths = read_utils.no_log_paths(spec["options"])
    assert any(path.endswith("snmp_communities[].name") for path in paths), paths
    if data is not None:
        assert "s3cret" not in repr(read_utils.redact(data, spec))


def test_reads_are_isolated_and_keep_their_order(monkeypatch):
    vlans = CASES["vlans"]
    lines = vlans["lines"]
    device = harness.Device(lines, full=harness.full_commands(monkeypatch, vlans), answer=vlans.get("answer"))
    reads = [
        {"resource": "no_such_family"},
        {"resource": "vlans", "section": "config", "ids": ["bad id; logout"]},
        dict(requests_of("vlans", vlans["config"])[0], meta={"scope": "vlan"}),
        {"kind": "operational", "resource": "vlans"},
    ]
    result = run_read(monkeypatch, reads, device)
    assert not result.get("failed"), result
    first, second, third, fourth = result["reads"]
    assert first["status"] == "error" and first["error"] == "invalid_request", first
    assert second["status"] == "error" and second["error"] == "invalid_request", second
    assert "bad id" not in " ".join(device.commands)
    assert third["status"] == "ok" and third["meta"] == {"scope": "vlan"}, third
    assert vlans["marker"] in repr(third["data"])
    assert fourth["status"] == "error" and fourth["error"] == "invalid_request", fourth
    assert result["status"] == "partial"


def test_a_failing_read_does_not_stop_the_next_one(monkeypatch):
    case = CASES["vlans"]
    first = requests_of("vlans", case["config"])[0]
    full = harness.full_commands(monkeypatch, case)
    lost = harness.Device(case["lines"], full=full, answer=case.get("answer"), fail=True)
    result = run_read(monkeypatch, [first, first], lost)
    assert [item["status"] for item in result["reads"]] == ["error", "error"]
    assert result["reads"][0]["error"] == "read_failed"
    assert result["reads"][0]["unverified_ids"] == first["ids"]
    assert result["status"] == "error"
    # The device text never reaches the result.
    assert "connection to the device was lost" not in repr(result)


def test_a_rejected_selector_stays_unverified(monkeypatch):
    # The device rejecting an instance path says nothing about its existence.
    case = CASES["vlans"]
    request = requests_of("vlans", case["config"])[0]
    device = harness.Device(case["lines"], full=harness.full_commands(monkeypatch, case), reject=True)
    (item,) = run_read(monkeypatch, [request], device)["reads"]
    # The rejection is reported (status partial, a stable warning class), never as absence.
    assert item["status"] == "partial" and item["warnings"] == ["unsupported_resource"], item
    assert item["unverified_ids"] == request["ids"], item
    assert item["confirmed_absent_ids"] == [] and item["returned_ids"] == []


class _Rejecting:
    commands = []  # type: list

    def get(self, command, *args, **kwargs):
        self.commands.append(command)
        raise Exception("Error : invalid token")


def test_a_family_the_msan_does_not_know_is_an_unsupported_read(monkeypatch):
    result = run_read(monkeypatch, [{"resource": "vlans"}, {"kind": "operational", "resource": "ont_status"}], _Rejecting())
    first, second = result["reads"]
    assert first["status"] == "error" and first["error"] == "unsupported_resource", first
    assert second["status"] == "error", second
    assert "invalid token" not in repr(result)


def test_an_operational_subset_and_a_configuration_family_in_one_call(monkeypatch):
    import pathlib

    fixture = (pathlib.Path(__file__).resolve().parents[4] / "fixtures" / "ont_status" / "r6.2.04m" / "output.txt").read_text()
    vlans = CASES["vlans"]

    class Mixed(harness.Device):
        def get(self, command, *args, **kwargs):
            if command == "show equipment ont status pon":
                self.commands.append(command)
                return fixture
            return super(Mixed, self).get(command, *args, **kwargs)

    device = Mixed(vlans["lines"], full=_All())
    result = run_read(monkeypatch, [{"kind": "operational", "resource": "ont_status"}, {"resource": "vlans"}], device)
    status, family = result["reads"]
    assert status["status"] == "ok" and len(status["data"]) == 74, status.get("error")
    assert status["data"][0]["pon"] == "1/1/2/1"
    assert family["status"] == "ok" and vlans["marker"] in repr(family["data"]), family
    assert result["status"] == "ok"


def test_credentials_never_leave_the_module(monkeypatch):
    lines = ["configure pppoe-client interface 1/1/1/1/3:100 client-id 1 profile-name prof-alpha username alice pbit 3",
             "configure pppoe-client ppp-profile prof-alpha password plain:geheim"]
    device = harness.Device(lines, full=_All(), answer=None)
    result = run_read(monkeypatch, [{"resource": "pppoe_client_ppp_profile"}, {"resource": "pppoe_client_interface"}],
                      device)
    assert "geheim" not in repr(result), result
    assert [item["status"] for item in result["reads"]] == ["ok", "ok"], result
    assert "alice" in repr(result["reads"][1]["data"])


class _All(set):
    def __contains__(self, item):
        return True


def test_the_request_checks():
    configuration = frozenset(["vlans", "equipment_onts"])
    operational = frozenset(["ont_status"])

    def check(read):
        return read_utils.normalize(read, configuration, operational)

    assert check({"resource": "vlans"}) == {"kind": "configuration", "resource": "vlans", "section": None, "ids": []}
    assert check({"resource": "equipment_onts", "section": "interfaces", "ids": ["1/1/8/5/1"]})["ids"] == ["1/1/8/5/1"]
    for bad in ({"resource": "ont_status"}, {"kind": "operational", "resource": "ont_status", "ids": ["x"]},
                {"resource": "vlans", "ids": ["1"]}, {"resource": "vlans", "section": "config"},
                {"resource": "equipment_onts", "section": "nope", "ids": ["1"]},
                {"resource": "equipment_onts", "section": "interfaces", "ids": ["1/1/8/5/1", "1/1/8/5/1"]},
                {"resource": "equipment_onts", "section": "interfaces", "ids": ["1 1"]}):
        with pytest.raises(read_utils.ReadRequestError):
            check(bad)


def test_redaction_and_warning_categories():
    spec = {"type": "list", "options": {"name": {}, "key": {"no_log": True},
                                        "users": {"type": "list", "options": {"name": {"no_log": True}}}}}
    assert read_utils.no_log_paths(spec["options"]) == {"key", "users[].name"}
    data = [{"name": "a", "key": "k", "Password": "p", "nested": {"secret": "s", "ok": 1},
             "users": [{"name": "u", "role": "r"}]}]
    assert read_utils.redact(data, spec) == [{"name": "a", "nested": {"ok": 1}, "users": [{"role": "r"}]}]
    assert read_utils.safe_warnings(["resource 'x' is not supported: invalid token at 1/1/1",
                                     "unmatched configuration for 'y': configure y z", "other"]) == [
        "unsupported_resource", "unmatched_configuration", "collection_warning"]


def test_every_family_loaded_by_path_is_shipped_with_the_module():
    # Ansible packs only module_utils imported by name; a path loaded with __import__
    # at run time is missing on the device unless read.py also imports it statically.
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(read_utils))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.update("%s.%s" % (node.module, alias.name) for alias in node.names)
            imported.add(node.module)
    paths = [entry[0] for entry in read_utils.MODULE_DIRECT.values()]
    paths += [entry[3] for entry in read_utils.MODULE_DIRECT.values()]
    paths += [entry[0] for entry in read_utils.FAMILY_ARGSPECS.values()]
    missing = sorted(path for path in set(paths) if read_utils._BASE + path not in imported)
    assert not missing, missing


VP = "vlan-port:1/1/7/16/1/1/1:99"


def test_arp_relay_statistics_on_answers_with_the_header_only_and_is_present(monkeypatch):
    # Live 2026-11-26: off -> "instance does not exist"; on -> header only, also with detail.
    on = run_read(monkeypatch, [{"resource": "isam_arp_relay", "section": "config", "ids": [VP]}],
                  harness.Device([], header=True))
    assert on["reads"][0]["returned_ids"] == [VP], on["reads"][0]
    off = run_read(monkeypatch, [{"resource": "isam_arp_relay", "section": "config", "ids": [VP]}],
                   harness.Device([]))
    assert off["reads"][0]["confirmed_absent_ids"] == [VP], off["reads"][0]


def test_a_vlan_port_without_pppoe_client_answers_with_the_header_and_is_absent(monkeypatch):
    # A client always prints profile, user and password: header only is no client.
    read = [{"resource": "pppoe_client_interface", "section": "config", "ids": [VP]}]
    none = run_read(monkeypatch, read, harness.Device([], header=True))
    assert none["reads"][0]["confirmed_absent_ids"] == [VP], none["reads"][0]
    line = "configure pppoe-client interface %s client-id 1 profile-name name:p username u password x" % VP
    client = run_read(monkeypatch, read, harness.Device([line]))
    assert client["reads"][0]["returned_ids"] == [VP], client["reads"][0]


def test_default_only_xdsl_parts_are_present_through_their_detail_read(monkeypatch):
    # Live 2026-11-26, NDLT-F: bonding group, bonding board and INM sensors print the header
    # only in flat and their line with defaults in flat detail.
    cases = [("xdsl_bonding", "groups", "1/1/3/1", "configure xdsl-bonding group 1/1/3/1 no group-profile"),
             ("xdsl_bonding", "boards", "1/1/3", "configure xdsl-bonding board 1/1/3 vect-fallback"),
             ("xdsl_inm", "near_end", "1/1/3/1", "configure xdsl imp-noise-sensor near-end 1/1/3/1 no inm-mode")]
    for resource, section, ident, line in cases:
        read = [{"resource": resource, "section": section, "ids": [ident]}]

        def answer(command, _lines, line=line):
            # flat: the header only (an empty reply); flat detail: the line with defaults
            return line + "\n" if command.endswith(" flat detail") else "echo x\n#------------\n"
        got = run_read(monkeypatch, read, harness.Device([], answer=answer))
        assert got["reads"][0]["returned_ids"] == [ident], (resource, got["reads"][0])


def test_a_missing_dependency_is_labelled_on_the_unverified_id(monkeypatch):
    # "lower-interface does not exist" on the detail probe: unverified, never absent,
    # and the label tells the refresh which object the device could not resolve.
    read = [{"resource": "bridges", "section": "port", "ids": ["1/1/5/1/3/1/1"]}]

    def answer(command, _lines):
        if command.endswith(" flat detail"):
            raise Exception("Error : lower-interface does not exist")
        return "echo x\n#------------\n"
    item = run_read(monkeypatch, read, harness.Device([], answer=answer))["reads"][0]
    assert item["unverified_ids"] == ["1/1/5/1/3/1/1"] and item["confirmed_absent_ids"] == [], item
    assert item["dependency_gaps"] == [{"id": "1/1/5/1/3/1/1", "dependency_gap": "lower-interface"}], item
