"""Family reads in a refresh: the data (FAMILY_READS) and the proof rules.

Presence comes from the family's parser, absence only from a complete reply with no
line naming the instance; everything else is unverified and read targeted.
"""
import importlib
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import family_reads
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.family_reads import (
    FAMILY_READS, classify, complete, family_read_for, mentioned)

from .module_runner import run_module

CASES = {}
for _path in sorted(pathlib.Path(__file__).parent.glob("targeted_cases_*.py")):
    CASES.update(importlib.import_module("." + _path.stem, __package__).CASES)

END = "#--------------------------------------------------------------------------------"
PAE = FAMILY_READS[("isam_system_security", "pae.ports")]


def _case(resource, section):
    return CASES.get(resource if section == "config" else "%s:%s" % (resource, section))


def _identity(case, resource, section):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER
    config = case["config"]
    for part in ([] if section == "config" else section.split(".")):
        config = config[part]
    return config[0][TARGETED_GATHER[resource][section]]


@pytest.mark.parametrize("resource,section", sorted(FAMILY_READS), ids=lambda v: v)
def test_each_family_read_finds_the_instance_lines_of_its_section(resource, section):
    # The prefix and the family's parser agree with the instance lines of the section's
    # targeted case: a wrong prefix would turn every existing instance into "absent".
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology.refresh_run import _parsed

    entry = FAMILY_READS[(resource, section)]
    assert entry["command"].endswith(("flat detail", "detail flat")), entry
    assert entry["command"].startswith("info " + " ".join(entry["prefix"].split()[:3])), entry
    case = _case(resource, section)
    identity = _identity(case, resource, section)
    reply = "\n".join(case["lines"]) + "\n" + END + "\n"
    assert mentioned(reply, entry["prefix"], identity), (resource, section, identity)

    class Module(object):
        params = {}
        check_mode = True
        _socket_path = None
        _connection = None
        no_log_values = set()

        def warn(self, msg):
            pass

        def fail_json(self, **kw):
            raise AssertionError(kw)
    parsed, _items = _parsed(Module(), resource, section, reply)
    if resource == "pppoe_client_interface":
        assert parsed == set()  # no facts parser: a named instance stays unverified, read targeted
    else:
        assert str(identity) in parsed, (resource, section, parsed)


def test_presence_from_the_parser_absence_only_from_a_complete_reply_naming_nothing():
    reply = "\n".join(["configure system security pae port 1/1/3/1 initialize",
                       "configure system security pae port 1/1/3/2 something-new 7", END])
    ids = ["1/1/3/1", "1/1/3/2", "1/1/3/3"]
    # 1/1/3/2 has a line the parser did not return: unverified, never absent.
    assert classify(reply, PAE, ids, {"1/1/3/1"}) == (["1/1/3/1"], ["1/1/3/3"], ["1/1/3/2"])
    # Without the terminal delimiter the reply may be cut short: nothing is absent.
    truncated = reply.rsplit("\n", 1)[0]
    assert not complete(truncated)
    assert classify(truncated, PAE, ids, {"1/1/3/1"}) == (["1/1/3/1"], [], ["1/1/3/2", "1/1/3/3"])
    # 1/1/3/1 is not 1/1/3/10.
    assert not mentioned("configure system security pae port 1/1/3/10 x\n", PAE["prefix"], "1/1/3/1")


def test_a_family_read_is_chosen_from_its_measured_minimum_and_never_under_an_absence_policy(monkeypatch):
    assert family_read_for("isam_system_security", "pae.ports", ["a"] * 4) is PAE
    assert family_read_for("isam_system_security", "pae.ports", ["a"] * 3) is None
    assert family_read_for("interfaces", "config", ["a"] * 39) is None
    assert family_read_for("qos_interfaces", "config", ["a"] * 500) is None  # 1 MB on production
    monkeypatch.setattr(family_reads, "absence_policy", lambda resource, section: "silent")
    assert family_read_for("isam_system_security", "pae.ports", ["a"] * 48) is None


# -- in a refresh ----------------------------------------------------------------------

def _ports(n):
    from .test_topology_discovery import port_table
    names = ["xdsl-line:1/1/3/%d" % i for i in range(1, n + 1)] + ["ethernet-line:1/1/3/%d" % i for i in range(1, n + 1)]
    return port_table(names)


def _card(monkeypatch, pae_reply):
    empty = "echo x\n#------------\n"

    def device(command):
        if command == "show interface port":
            return _ports(4)
        if command == PAE["command"]:
            return pae_reply
        return empty
    result = run_module(monkeypatch, "isam_refresh", {"kind": "card", "identity": "lt:1/1/3",
                                                      "allow_broad_read": True}, device)
    pae = [s for s in result["refresh"]["sections"]
           if s["resource"] == "isam_system_security" and s["section"] == "pae.ports"]
    return result, {s["id"]: (s["status"], s.get("reason")) for s in pae}


def test_a_card_reads_a_cheap_family_once_and_targeted_only_what_it_left_open(monkeypatch):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.topology import refresh_run
    reply = "\n".join(["configure system security pae port 1/1/3/1 initialize",
                       "configure system security pae port 1/1/3/2 something-new 7", END])
    real = refresh_run._parsed

    def parser_missing_a_line(module, resource, section, text):
        # As if the parser did not recognize the 1/1/3/2 line.
        ids, items = real(module, resource, section, text)
        if section != "pae.ports":
            return ids, items
        return ids - {"1/1/3/2"}, [i for i in items if i.get("port") != "1/1/3/2"]
    monkeypatch.setattr(refresh_run, "_parsed", parser_missing_a_line)
    result, pae = _card(monkeypatch, reply)
    sent = result["_sent"]
    assert sent.count(PAE["command"]) == 1
    assert pae["1/1/3/1"] == ("present", None)
    assert pae["1/1/3/3"] == ("absent", None) and pae["1/1/3/4"] == ("absent", None)
    # Only the instance the family read left unverified is read targeted.
    targeted = [c for c in sent if c.startswith("info configure system security pae port 1/1/3/")]
    assert targeted and all(" 1/1/3/2 " in c for c in targeted), targeted
    assert result["refresh"]["stats"]["family_reads"] >= 1


def test_a_failed_family_read_falls_back_to_targeted_reads(monkeypatch):
    result, pae = _card(monkeypatch, Exception("Error : something"))
    targeted = [c for c in result["_sent"] if c.startswith("info configure system security pae port 1/1/3/")]
    assert len({c.split()[6] for c in targeted}) == 4, targeted
    assert set(pae) == {"1/1/3/%d" % i for i in range(1, 5)}


def test_a_section_no_read_can_show_is_not_read_and_named(monkeypatch):
    # isam_dhcp_relay (relations observable: False) on a VLAN port of a UNI.
    from .test_isam_refresh import stack
    uni = "1/1/5/1/3/1/1"

    def device(command):
        if command == "show interface stack":
            return stack([("bridge-port:%s" % uni, "uni:%s" % uni), ("vlan-port:%s:99" % uni, "bridge-port:%s" % uni)])
        return "echo x\n#------------\n"
    result = run_module(monkeypatch, "isam_refresh", {"kind": "uni", "identity": uni, "allow_broad_read": True}, device)
    assert not [c for c in result["_sent"] if "dhcp-relay" in c], result["_sent"]
    dhcp = [s for s in result["refresh"]["sections"] if s["resource"] == "isam_dhcp_relay"]
    assert dhcp and all(s["reason"] == "not_observable" for s in dhcp)
    assert result["refresh"]["stats"]["sections_not_read"] >= 1


def test_a_requested_section_that_configures_nothing_under_the_root_is_a_gap(monkeypatch):
    result = run_module(monkeypatch, "isam_refresh", {"kind": "ont", "identity": "1/1/5/1/3", "allow_broad_read": True,
                                                      "sections": ["system"]}, "echo x\n#------------\n")
    outcome = result["refresh"]
    assert {"section": "system.config", "reason": "section_not_under_root"} in outcome["gaps"] or any(
        g.get("reason") == "section_not_under_root" for g in outcome["gaps"]), outcome["gaps"]
    assert not outcome["complete"]
