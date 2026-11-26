"""bridges against `info configure detail flat` of a real ISAM.

Port: outervlancapture, direction, default_tpid and the vlan-tpid0/vlan-tpid1 sub-nodes.
VLAN port: inner_pbit_remark, groupid, usacceptframetype, oltregenprofile (and tpid as a
string). Parse (detail lines incl. `no X` defaults), render round trip, merged
idempotence, replaced/deleted reset forms, documentation, and the gap report.
"""
import os

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_bridges
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.bridges.bridges import (
    BridgesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.bridges.bridges import (
    BridgesFacts,
)

from .isam_module import set_module_args
from .test_isam_bridges import TestIsamBridgesModule as _Base
from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson, AnsibleFailJson

P = "configure bridge port 1/1/8/1"
VLAN_DEFAULTS = (
    "no qos no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort "
    "no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name "
    "no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl "
    "no min-cvlan-id no max-cvlan-id no ds-dedicated-q"
)

# Lab capture format, every new attribute at its default.
DETAIL_DEFAULTS = "\n".join([
    P + " no default-priority no mac-learn-off max-unicast-mac 5 no qos-profile no prio-regen-prof no prio-regen-name"
    " no max-committed-mac no mirror-mode no mirror-vlan no outervlancapture no direction no pvid-tagging-flag"
    " no ds-pbit-mode no default-tpid",
    P + " vlan-tpid0 0 no tpid",
    P + " vlan-tpid1 1 no tpid",
    P + " pvid 99",
    P + " vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local " + VLAN_DEFAULTS
    + " no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile",
    P + " vlan-id 99 no tag no l2fwder-vlan no vlan-scope " + VLAN_DEFAULTS
    + " no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile",
])

# Same port, every new attribute set to a non-default value (CLI guide 3HH-08079-FCEH-TCZZA
# syntax and value ranges; the values are synthetic).
DETAIL_SET = "\n".join([
    P + " no default-priority no mac-learn-off max-unicast-mac 5 no qos-profile no prio-regen-prof no prio-regen-name"
    " no max-committed-mac no mirror-mode no mirror-vlan outervlancapture 100 direction ingress no pvid-tagging-flag"
    " no ds-pbit-mode default-tpid 9100",
    P + " vlan-tpid0 0 tpid 88a8",
    P + " vlan-tpid1 1 tpid 9100",
    P + " pvid 99",
    P + " vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local " + VLAN_DEFAULTS
    + " tpid 8100 inner-pbit-remark remark groupid 7 usacceptframetype untagged oltregenprofile enabled",
    P + " vlan-id 99 no tag no l2fwder-vlan no vlan-scope " + VLAN_DEFAULTS
    + " no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile",
])

NEW_PORT = {"outervlancapture": 100, "direction": "ingress", "default_tpid": "9100",
            "vlan_tpid0": {"tpid": "88a8"}, "vlan_tpid1": {"tpid": "9100"}}
NEW_VLAN = {"tpid": "8100", "inner_pbit_remark": "remark", "groupid": "7",
            "usacceptframetype": "untagged", "oltregenprofile": "enabled"}


def _port(text):
    ports = BridgesFacts(module=None)._parse_bridge_config(text)["port"]
    assert len(ports) == 1
    return ports[0]


def test_detail_defaults_report_none_of_the_new_attributes():
    port = _port(DETAIL_DEFAULTS)
    for key in NEW_PORT:
        assert key not in port
    assert "vlan_tpid" not in str(port)
    for vlan in port["vlan_id"]:
        for key in NEW_VLAN:
            assert key not in vlan
    assert port["pvid"] == 99 and port["max_unicast_mac"] == 5


def test_detail_set_parses_every_new_attribute():
    port = _port(DETAIL_SET)
    for key, value in NEW_PORT.items():
        assert port[key] == value, key
    vlan10 = [v for v in port["vlan_id"] if v["id"] == "10"][0]
    for key, value in NEW_VLAN.items():
        assert vlan10[key] == value, key
    # Hex TPIDs that look numeric stay strings (argspec type str).
    assert isinstance(port["default_tpid"], str) and isinstance(vlan10["tpid"], str)


def test_unknown_vlan_tpid_keywords_never_fail_the_read():
    port = _port(P + " vlan-tpid0 0 tpid 88a8 future-knob 3\n" + P + " vlan-tpid2 2 tpid 9100")
    assert port["vlan_tpid0"]["tpid"] == "88a8"


def test_new_options_documented():
    import yaml

    doc = yaml.safe_load(isam_bridges.DOCUMENTATION)["options"]["config"]["suboptions"]["port"]["suboptions"]
    spec = BridgesArgs.argument_spec["config"]["options"]["port"]["options"]
    for key in NEW_PORT:
        assert key in doc and key in spec
        assert doc[key]["type"] == spec[key]["type"]
    for key in NEW_VLAN:
        assert key in doc["vlan_id"]["suboptions"] and key in spec["vlan_id"]["options"]
    assert doc["direction"]["choices"] == spec["direction"]["choices"]


class TestBridgesGaps(_Base):
    def _run(self, state, config, facts_text=""):
        class FactsConn:
            def get(self, command):
                return facts_text

        self.get_resource_connection_facts.return_value = FactsConn()
        set_module_args(dict(state=state, config=config, _ansible_check_mode=True), True)
        try:
            self.module.main()
        except AnsibleExitJson as exc:
            return exc.args[0]
        except AnsibleFailJson as exc:
            raise AssertionError(exc.args[0].get("msg"))
        raise AssertionError("module did not exit")

    def _full_config(self):
        vlans = [dict({"id": "10", "tag": "single-tagged", "l2fwder_vlan": "710", "vlan_scope": "local"}, **NEW_VLAN),
                 {"id": "99"}]
        return {"port": [dict({"port": "1/1/8/1", "pvid": 99, "max_unicast_mac": 5, "vlan_id": vlans}, **NEW_PORT)]}

    def test_rendered_forms(self):
        rendered = self._run("rendered", self._full_config())["rendered"]
        assert P + " max-unicast-mac 5 outervlancapture 100 direction ingress default-tpid 9100" in rendered
        assert P + " vlan-tpid0 0 tpid 88a8" in rendered
        assert P + " vlan-tpid1 1 tpid 9100" in rendered
        assert (P + " vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local tpid 8100 inner-pbit-remark remark"
                " groupid 7 usacceptframetype untagged oltregenprofile enabled") in rendered

    def test_round_trip_rendered_reparses(self):
        rendered = self._run("rendered", self._full_config())["rendered"]
        port = _port("\n".join(rendered))
        for key, value in NEW_PORT.items():
            assert port[key] == value, key
        vlan10 = [v for v in port["vlan_id"] if v["id"] == "10"][0]
        for key, value in NEW_VLAN.items():
            assert vlan10[key] == value, key

    def test_gathered_detail_is_merged_idempotent(self):
        for text in (DETAIL_SET, DETAIL_DEFAULTS):
            gathered = self._run("gathered", {"port": [{"port": "1/1/8/1"}]}, text)["gathered"]
            assert self._run("merged", gathered, text)["commands"] == []
            assert self._run("replaced", gathered, text)["commands"] == []
        assert self._run("merged", self._full_config(), DETAIL_SET)["commands"] == []

    def test_merged_changes_only_the_new_value(self):
        # merged replaces a named VLAN entry as a whole (existing behaviour): name it fully.
        vlan10 = dict({"id": "10", "tag": "single-tagged", "l2fwder_vlan": "710", "vlan_scope": "local"}, **NEW_VLAN)
        vlan10["groupid"] = "8"
        config = {"port": [{"port": "1/1/8/1", "default_tpid": "88a8", "vlan_tpid1": {"tpid": "88a8"},
                            "vlan_id": [vlan10]}]}
        commands = self._run("merged", config, DETAIL_SET)["commands"]
        assert commands == [P + " default-tpid 88a8", P + " vlan-tpid1 1 tpid 88a8", P + " vlan-id 10 groupid 8"]

    def test_replaced_resets_new_attributes(self):
        config = {"port": [{"port": "1/1/8/1", "pvid": 99, "max_unicast_mac": 5,
                            "vlan_id": [{"id": "10", "tag": "single-tagged", "l2fwder_vlan": "710",
                                         "vlan_scope": "local"}, {"id": "99"}]}]}
        commands = self._run("replaced", config, DETAIL_SET)["commands"]
        assert commands == [
            P + " no outervlancapture no direction no default-tpid",
            P + " vlan-tpid0 0 no tpid",
            P + " vlan-tpid1 1 no tpid",
            P + " vlan-id 10 no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile",
        ]

    def test_replaced_on_detail_defaults_does_not_turn_flags_on(self):
        # "no mac-learn-off" / "no prior-*" are read as False; they must not render
        # "mac-learn-off" or "prior-best-effort False".
        config = {"port": [{"port": "1/1/8/1", "pvid": 99, "max_unicast_mac": 5,
                            "vlan_id": [{"id": "10", "tag": "single-tagged", "l2fwder_vlan": "710",
                                         "vlan_scope": "local"}, {"id": "99"}]}]}
        assert self._run("replaced", config, DETAIL_DEFAULTS)["commands"] == []
        on = DETAIL_DEFAULTS.replace("no mac-learn-off", "mac-learn-off")
        commands = self._run("replaced", config, on)["commands"]
        assert commands == [P + " no mac-learn-off"]
        explicit = {"port": [{"port": "1/1/8/1", "mac_learn_off": True}]}
        assert self._run("merged", explicit, DETAIL_DEFAULTS)["commands"] == [P + " mac-learn-off"]
        assert self._run("merged", {"port": [{"port": "1/1/8/1", "mac_learn_off": False}]}, on)["commands"] == [
            P + " no mac-learn-off"]

    def test_deleted_named_new_attributes(self):
        config = {"port": [{"port": "1/1/8/1", "default_tpid": "9100", "outervlancapture": 100,
                            "vlan_tpid0": {"tpid": "88a8"}}]}
        commands = self._run("deleted", config, DETAIL_SET)["commands"]
        assert commands == [P + " no outervlancapture no default-tpid", P + " vlan-tpid0 0 no tpid"]


# Gap report of the lab capture --------------------------------------------------------

from . import lab_captures

_capture = lab_captures.read


def test_capture_gap_report_empty():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam import config_tree

    tree = config_tree.parse_config_tree(_capture("root-detail-flat.txt"))
    entry = config_tree.gap_report(tree)["families"]["bridges"]
    # The only value-like tokens are the "static-user ip-address <ip>" addresses
    # (modelled as vlan_id[].static_user[].ip_address, checked below).
    assert entry["unmodelled"] == {}


def _names(options):
    names = set()
    for key, option in options.items():
        names |= {n.replace("-", "_") for n in [key] + list(option.get("aliases") or [])}
    return names


def _walk(tokens, flags):
    """(cli_key, value or None, negated) for every token; nothing is skipped."""
    out, i = [], 0
    while i < len(tokens):
        negated = tokens[i] == "no"
        j = i + 1 if negated else i
        key = tokens[j]
        if negated or key in flags:
            out.append((key, None if negated else True, negated))
            i = j + 1
        else:
            assert j + 1 < len(tokens), ("value missing", tokens)
            out.append((key, tokens[j + 1], False))
            i = j + 2
    return out


@pytest.mark.parametrize("name", lab_captures.NAMES)
def test_capture_every_token_is_modelled_and_read_into_its_field(name):
    """Each "configure bridge" token of the capture belongs to a modelled option, and
    each non-default value lands in that option of the facts (no skipped tokens, no
    sub-node value in a wrong field)."""
    import re

    text = _capture(name)
    port_spec = BridgesArgs.argument_spec["config"]["options"]["port"]["options"]
    vlan_spec = port_spec["vlan_id"]["options"]
    port_names, vlan_names = _names(port_spec), _names(vlan_spec)
    facts = BridgesFacts(module=None)._parse_bridge_config(text)
    ports = {p["port"]: p for p in facts["port"]}
    checked = 0
    for line in text.splitlines():
        if not line.startswith("configure bridge port "):
            continue
        tokens = line.split()[3:]
        port = ports[tokens[0]]
        rest = tokens[1:]
        if rest[:1] == ["vlan-id"]:
            vlan = [v for v in port["vlan_id"] if v["id"] == rest[1]][0]
            rest = rest[2:]
            if rest[:2] == ["static-user", "ip-address"]:
                assert len(rest) == 3 and {"ip_address": rest[2]} in vlan["static_user"]
                checked += 1
                continue
            entry, names, flags = vlan, vlan_names, {"prior-best-effort", "prior-background", "prior-spare",
                                                     "prior-exc-effort", "prior-ctrl-load", "prior-less-100ms",
                                                     "prior-less-10ms", "prior-nw-ctrl"}
        elif rest and re.match(r"^vlan-tpid\d+$", rest[0]):
            sub = port.get(rest[0].replace("-", "_"), {})
            assert rest[0].replace("-", "_") in port_names
            entry, names, flags, rest = sub, {"tpid"}, set(), rest[2:]
        else:
            entry, names, flags = port, port_names, {"mac-learn-off"}
        for key, value, negated in _walk(rest, flags):
            field = key.replace("-", "_")
            assert field in names, (line, key)
            if negated:
                assert entry.get(field) in (None, False), (line, key)
            else:
                assert str(entry.get(field)) == str(value), (line, key, entry.get(field))
            checked += 1
    assert checked > 1000 if "detail" in name else checked > 100



class TestBridgesMergeAndFlags(TestBridgesGaps):
    DEVICE = "\n".join([
        "configure bridge port 1/1/5/1/3/1/1 max-unicast-mac 5",
        "configure bridge port 1/1/5/1/3/1/1 vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local",
        "configure bridge port 1/1/5/1/3/1/1 vlan-id 99",
        "configure bridge port 1/1/5/1/3/1/1 pvid 99",
    ])

    def test_merged_partial_vlan_entry_keeps_the_rest_of_the_vlan(self):
        result = self._run("merged", {"port": [{"port": "1/1/5/1/3/1/1", "vlan_id": [{"id": "10", "qos": "priority:3"}]}]}, self.DEVICE)
        assert result["commands"] == ["configure bridge port 1/1/5/1/3/1/1 vlan-id 10 qos priority:3"], result["commands"]

    def test_merged_identical_partial_vlan_is_idempotent(self):
        result = self._run("merged", {"port": [{"port": "1/1/5/1/3/1/1", "vlan_id": [{"id": "10", "tag": "single-tagged"}]}]}, self.DEVICE)
        assert result["commands"] == []

    def test_prior_flags_render_as_bare_keywords(self):
        result = self._run("rendered", {"port": [{"port": "1/1/5/1/3/1/1", "vlan_id": [
            {"id": "10", "prior_best_effort": True, "prior_nw_ctrl": False}]}]})
        text = " ".join(result["rendered"])
        assert "prior-best-effort" in text and "prior-best-effort True" not in text
        assert "True" not in text and "False" not in text


class TestBridgesDeletedNamedAttributes(TestBridgesGaps):
    """deleted: a VLAN entry naming attributes resets only them; the port is removed
    only for its identity alone or a whole entry (state contract)."""

    U = "configure bridge port 1/1/1/1"
    DEVICE = "\n".join([
        U + " max-unicast-mac 5",
        U + " vlan-id 100 tag single-tagged usacceptframetype untagged groupid 7",
        U + " vlan-id 100 static-user ip-address 10.0.0.1",
        U + " pvid 100",
    ])

    def test_naming_a_vlan_attribute_resets_only_that_attribute(self):
        config = {"port": [{"port": "1/1/1/1", "vlan_id": [{"id": "100", "usacceptframetype": "all"}]}]}
        assert self._run("deleted", config, self.DEVICE)["commands"] == [self.U + " vlan-id 100 no usacceptframetype"]
        config = {"port": [{"port": "1/1/1/1", "vlan_id": [{"id": "100", "groupid": "7", "tag": "single-tagged"}]}]}
        assert self._run("deleted", config, self.DEVICE)["commands"] == [self.U + " vlan-id 100 no tag no groupid"]

    def test_naming_a_static_user_removes_only_that_address(self):
        config = {"port": [{"port": "1/1/1/1", "vlan_id": [{"id": "100", "static_user": [{"ip_address": "10.0.0.1"}]}]}]}
        assert self._run("deleted", config, self.DEVICE)["commands"] == [
            self.U + " vlan-id 100 static-user no ip-address 10.0.0.1"]

    def test_a_port_field_with_all_vlans_resets_the_field_and_removes_the_named_vlans(self):
        config = {"port": [{"port": "1/1/1/1", "max_unicast_mac": 5, "vlan_id": [{"id": "100"}]}]}
        assert self._run("deleted", config, self.DEVICE)["commands"] == [
            self.U + " no max-unicast-mac", self.U + " no vlan-id 100"]

    def test_identity_alone_and_whole_entry_remove_the_port(self):
        removal = ["configure bridge no port 1/1/1/1"]
        assert self._run("deleted", {"port": [{"port": "1/1/1/1"}]}, self.DEVICE)["commands"] == removal
        gathered = self._run("gathered", {"port": [{"port": "1/1/1/1"}]}, self.DEVICE)["gathered"]
        assert self._run("deleted", gathered, self.DEVICE)["commands"] == removal
        # every VLAN by its identity alone and no port setting named
        assert self._run("deleted", {"port": [{"port": "1/1/1/1", "vlan_id": [{"id": "100"}]}]},
                         "\n".join([self.U + " vlan-id 100", self.U + " pvid 100"]))["commands"] == removal


class TestBridgesDefaultsAreUnset(TestBridgesGaps):
    """CLI guide defaults (default-tpid 8100, usacceptframetype all, ...) and False flags
    count as unset: not reported, not reset, an explicit default sends nothing when the
    device has it."""

    U = "configure bridge port 1/1/1/1"
    EXPLICIT_DEFAULTS = "\n".join([
        U + " no mac-learn-off max-unicast-mac 5 outervlancapture 0 direction bidirection default-tpid 8100",
        U + " vlan-tpid0 0 tpid 8100",
        U + " vlan-tpid1 1 tpid 0",
        U + " vlan-id 100 tag single-tagged no prior-best-effort inner-pbit-remark untouched groupid 0"
        " usacceptframetype all oltregenprofile disabled",
        U + " pvid 100",
    ])

    def test_defaults_are_not_reported(self):
        for state, key in (("gathered", "gathered"),):
            port = self._run(state, {"port": [{"port": "1/1/1/1"}]}, self.EXPLICIT_DEFAULTS)[key]["port"][0]
            assert port == {"port": "1/1/1/1", "max_unicast_mac": 5, "pvid": 100,
                            "vlan_id": [{"id": "100", "tag": "single-tagged"}]}
        assert "mac_learn_off" not in _port(DETAIL_DEFAULTS)

    def test_replaced_does_not_reset_defaults_the_device_prints(self):
        config = {"port": [{"port": "1/1/1/1", "max_unicast_mac": 5, "pvid": 100,
                            "vlan_id": [{"id": "100", "tag": "single-tagged"}]}]}
        assert self._run("replaced", config, self.EXPLICIT_DEFAULTS)["commands"] == []

    def test_an_explicit_default_is_idempotent_and_resets_a_non_default(self):
        config = {"port": [{"port": "1/1/1/1", "default_tpid": "8100", "vlan_tpid0": {"tpid": "8100"},
                            "vlan_id": [{"id": "100", "usacceptframetype": "all"}]}]}
        assert self._run("merged", config, self.EXPLICIT_DEFAULTS)["commands"] == []
        changed = self.EXPLICIT_DEFAULTS.replace("default-tpid 8100", "default-tpid 9100").replace(
            "usacceptframetype all", "usacceptframetype untagged")
        assert self._run("merged", config, changed)["commands"] == [
            self.U + " default-tpid 8100", self.U + " vlan-id 100 usacceptframetype all"]
