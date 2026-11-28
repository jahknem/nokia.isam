"""Missing dependencies require an independent, exact owner-absence proof."""
from copy import deepcopy

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.absence import resolve_owner_absence


UNI = "1/1/7/16/1/1/1"


def gap(port=UNI):
    return {"kind": "configuration", "resource": "bridges", "section": "port", "ids": [port],
            "status": "ok", "returned_ids": [], "confirmed_absent_ids": [], "unverified_ids": [port],
            "dependency_gaps": [{"id": port, "dependency_gap": "lower-interface"}]}


def answer(request, state):
    result = dict(request, status="ok", returned_ids=[], confirmed_absent_ids=[], unverified_ids=[])
    result[{"present": "returned_ids", "absent": "confirmed_absent_ids", "unknown": "unverified_ids"}[state]] = list(request["ids"])
    return result


def test_absent_uni_proves_its_bridge_port_absent_without_a_bridge_exception():
    result, reads = gap(), []

    def read(request):
        reads.append(request)
        return answer(request, "absent")

    resolve_owner_absence([result], read)
    assert reads == [{"kind": "configuration", "resource": "ethernet_onts", "section": "config", "ids": [UNI]}]
    assert result["confirmed_absent_ids"] == [UNI] and result["unverified_ids"] == []
    assert result["absence_evidence"][0]["owner"]["kind"] == "uni"


@pytest.mark.parametrize("state", ["present", "unknown", "error"])
def test_no_inference_from_present_unknown_or_failed_owner_read(state):
    result = gap()
    original = deepcopy(result)
    reads = []

    def read(request):
        reads.append(request)
        return dict(request, status="error") if state == "error" else answer(request, state)

    resolve_owner_absence([result], read)
    assert result == original
    assert reads


def test_existing_batch_proof_is_reused_regardless_of_request_order():
    proof = answer({"kind": "configuration", "resource": "ethernet_onts", "section": "config", "ids": [UNI]}, "absent")
    for results in ([gap(), proof], [proof, gap()]):
        resolve_owner_absence(results, lambda req: pytest.fail("unnecessary read"))
        assert next(r for r in results if r["resource"] == "bridges")["confirmed_absent_ids"] == [UNI]


def test_conflicting_evidence_cannot_erase_configuration():
    request = {"kind": "configuration", "resource": "ethernet_onts", "section": "config", "ids": [UNI]}
    results = [gap(), answer(request, "absent"), answer(request, "present")]
    resolve_owner_absence(results, lambda req: pytest.fail("unnecessary read"))
    assert results[0]["unverified_ids"] == [UNI]


def test_present_child_blocks_absent_ancestor():
    parent = answer({"kind": "configuration", "resource": "equipment_onts", "section": "interfaces",
                     "ids": ["1/1/7/16/1"]}, "absent")
    child = answer({"kind": "configuration", "resource": "ethernet_onts", "section": "config", "ids": [UNI]}, "present")
    result = gap()
    resolve_owner_absence([result, parent, child], lambda req: pytest.fail("unnecessary read"))
    assert result["unverified_ids"] == [UNI]


def test_unknown_owner_can_be_resolved_by_an_independently_absent_container():
    result, reads = gap(), []

    def read(request):
        reads.append(request)
        return answer(request, "absent" if request["section"] == "slots" else "unknown")

    resolve_owner_absence([result], read)
    assert len(reads) == 2 and reads[-1]["ids"] == ["1/1/7/16/1/1"]
    assert result["confirmed_absent_ids"] == [UNI]


def test_ambiguous_bare_lt_address_does_not_guess_a_card_or_port_kind():
    result = gap("1/1/3/1")
    resolve_owner_absence([result], lambda req: pytest.fail("ambiguous identity must not be probed"))
    assert result["unverified_ids"] == ["1/1/3/1"]


def test_optional_section_absence_is_not_object_absence(monkeypatch):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import absence

    monkeypatch.setitem(absence.FAMILIES, "example_service", {"sections": {
        "config": {"object": "uni", "identity": "name"}}})
    optional = answer({"kind": "configuration", "resource": "example_service", "section": "config", "ids": [UNI]}, "absent")
    result, reads = gap(), []

    def read(request):
        reads.append(request)
        return answer(request, "present")

    resolve_owner_absence([result, optional], read)
    assert reads and result["unverified_ids"] == [UNI]


def test_dependency_gap_resolution_is_not_a_resource_name_rule(monkeypatch):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import absence

    monkeypatch.setitem(absence.FAMILIES, "example_service", {"sections": {
        "config": {"object": "uni", "identity": "name"}}})
    result = dict(gap(), resource="example_service", section="config")
    resolve_owner_absence([result], lambda req: answer(req, "absent"))
    assert result["confirmed_absent_ids"] == [UNI]


def test_isam_read_runs_an_exact_proof_read_and_keeps_the_public_request_scope(monkeypatch):
    from .module_runner import run_module

    def device(command):
        if command.startswith("info configure bridge port " + UNI):
            return "Error : specified lower-interface does not exist\n"
        if command.startswith("info configure ethernet ont " + UNI):
            return "Error : instance does not exist\n"
        pytest.fail("unexpected command: " + command)

    request = {"kind": "configuration", "resource": "bridges", "section": "port", "ids": [UNI]}
    result = run_module(monkeypatch, "isam_read", {"reads": [request]}, device)
    assert not result.get("failed"), result.get("msg")
    (read,) = result["reads"]
    assert read["confirmed_absent_ids"] == [UNI] and read["unverified_ids"] == []
    assert read["resource"] == "bridges" and read["ids"] == [UNI]
    assert read["absence_evidence"][0]["owner"]["resource"] == "ethernet_onts"
    assert len(result["_sent"]) == 2
