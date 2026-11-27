"""isam_refresh: a whole (or partial) refresh in one task, on one connection.

The planner and the evaluation are tested offline in test_topology_refresh.py; this
checks the run: which commands go to the device, that every discovery source is read
once for the whole run, partial refreshes, and that failures become named gaps.
"""
import json

from .module_runner import run_module
from .test_topology_discovery import port_table

EMPTY = "echo x\n#------------\n"  # header only: nothing configured
ONT = "1/1/5/1/3"


def stack(rows):
    width = 47
    return "\n".join(["=" * 95, "stack table", "=" * 95, "%-*s|%-*s" % (width, "higher", width, "lower"),
                      "-" * width + "+" + "-" * width]
                     + ["%-*s %-*s" % (width, higher, width, lower) for higher, lower in rows]
                     + ["-" * 95, "stack count : %d" % len(rows), "=" * 95])


def device(replies):
    def answer(command):
        for prefix, reply in replies.items():
            if command.startswith(prefix):
                return reply
        return EMPTY
    return answer


def refresh(monkeypatch, args, replies=None):
    result = run_module(monkeypatch, "isam_refresh", dict(args, allow_broad_read=True), device(replies or {}))
    return result, result["_sent"]


def test_a_missing_ont_is_absent_part_by_part_with_read_commands_only(monkeypatch):
    result, sent = refresh(monkeypatch, {"kind": "ont", "identity": ONT})
    outcome = result["refresh"]
    assert {s["status"] for s in outcome["sections"]} == {"absent"}, outcome["sections"]
    assert len(outcome["sections"]) == outcome["stats"]["ids_read"] == 8
    # The fake device has no planned card type: named, never assumed.
    assert [g["reason"] for g in outcome["gaps"]] == ["card_type_unknown"]
    assert not outcome["complete"]
    assert all(c.startswith(("info configure ", "show ")) for c in sent), sent
    assert outcome["stats"]["source_reads"] == 1


def test_every_discovery_source_is_read_once_for_the_whole_card(monkeypatch):
    ports = port_table(["xdsl-line:1/1/3/1", "xdsl-line:1/1/3/2", "ethernet-line:1/1/3/1", "ethernet-line:1/1/3/2"])
    rows = [("bridge-port:1/1/3/1", "ethernet-line:1/1/3/1"), ("vlan-port:1/1/3/1:99", "bridge-port:1/1/3/1")]
    result, sent = refresh(monkeypatch, {"kind": "card", "identity": "lt:1/1/3"},
                           {"show interface port": ports, "show interface stack": stack(rows)})
    outcome = result["refresh"]
    assert sent.count("show interface stack") == 1, sent  # bridge-port and VLAN-port rounds, both lines
    assert sent.count("show interface port") == 1, sent
    objects = json.loads(json.dumps(outcome["objects"]))  # as Ansible returns it
    assert ["bridge_port", ["xdsl_line", "1/1/3/1"]] in objects, objects
    assert ["vlan_port", ["xdsl_line", "1/1/3/1", "99"]] in objects, objects
    assert outcome["stats"]["discovery_rounds"] >= 2


def test_a_partial_refresh_reads_only_its_sections_and_discovers_only_as_deep_as_needed(monkeypatch):
    # The ONT's own entry: no discovery at all, one configuration read.
    result, sent = refresh(monkeypatch, {"kind": "ont", "identity": ONT, "sections": ["equipment_onts.interfaces"]})
    outcome = result["refresh"]
    assert outcome["sections_requested"] == ["equipment_onts.interfaces"]
    assert [(s["resource"], s["section"], s["status"]) for s in outcome["sections"]] == [
        ("equipment_onts", "interfaces", "absent")]
    assert outcome["stats"]["discovery_requests"] == 0
    assert not [c for c in sent if c.startswith("show ") or "equipment ont flat" in c], sent
    # A UNI section: the ONT's slots and UNIs are enumerated, never bridge or VLAN ports.
    slots = "configure equipment ont slot %s/1 planned-card-type 10_100base plndnumdataports 1\n#----------\n" % ONT
    result, sent = refresh(monkeypatch, {"kind": "ont", "identity": ONT, "sections": ["uni_onts"]},
                           {"info configure equipment ont flat": slots, "info configure equipment ont slot": slots})
    kinds = {d["child_kind"] for d in result["refresh"]["discovery"]}
    assert "ont_slot" in kinds and kinds <= {"ont_slot", "uni"}, kinds
    assert "show interface stack" not in sent
    assert {s["resource"] for s in result["refresh"]["sections"]} <= {"uni_onts"}


def test_an_unknown_section_or_root_fails_before_any_command(monkeypatch):
    result, sent = refresh(monkeypatch, {"kind": "ont", "identity": ONT, "sections": ["no_such_family"]})
    assert result.get("failed") and sent == []
    result, sent = refresh(monkeypatch, {"kind": "ont", "identity": "not-an-ont"})
    assert result.get("failed") and sent == []


def test_a_source_not_understood_is_a_named_gap_not_a_failed_task(monkeypatch):
    # A port table whose footer count disagrees with its rows cannot list the card's lines.
    ports = port_table(["xdsl-line:1/1/3/1"], count=2)
    result, _sent = refresh(monkeypatch, {"kind": "card", "identity": "lt:1/1/3"}, {"show interface port": ports})
    assert not result.get("failed"), result.get("msg")
    outcome = result["refresh"]
    errors = [d for d in outcome["discovery"] if d["status"] == "error"]
    assert errors and {d["error"] for d in errors} == {"source_not_understood"}
    assert any(g.get("reason") == "discovery_error" for g in outcome["gaps"])
    assert not outcome["complete"]
