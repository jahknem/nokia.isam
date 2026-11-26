"""vlans against `info configure detail flat` of a real ISAM.

Every "vlan id" attribute of the capture is modelled (options use snake_case, the
CLI spelling is accepted as alias). Detail lines parse to the same values as the
configured-only read, and merged is idempotent on them ("no new-broadcast" is the
default, inherit).
"""
import os
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import VLAN_DEFAULTS

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.vlans.vlans import (
    VlansArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.vlans.vlans import (
    VlansFacts,
)
from ansible_collections.nokia.isam.tests.unit.compat.mock import MagicMock
from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson, AnsibleFailJson

from .isam_module import set_module_args
from .test_isam_vlans import TestIsamVlansModule as _Base

# Lab capture format (`info configure detail flat` prints each VLAN on two lines).
DETAIL = "\n".join([
    "configure vlan id 99 mode residential-bridge name MGMT-1 no sntp-proxy no priority no vmac-not-in-opt61"
    " no new-broadcast no protocol-filter no pppoe-relay-tag no drly-srv-usr-side new-secure-fwd enable"
    " no aging-time no l2cp-transparent in-qos-prof-name name:Default_TC0 no ipv4-mcast-ctrl no ipv6-mcast-ctrl"
    " no mac-mcast-ctrl no dis-proto-rip no proto-ntp no dis-ip-antispoof no unknown-unicast no pt2ptgem-flooding"
    " no mac-movement-ctrl no cvlan4095passthru no arp-snooping no arp-polling no arp-polling-ip no mac-unauth",
    "configure vlan id 99 no vmac-translation no vmac-dnstr-filter dhcp-opt82-ext add-or-forward no dhcp-opt82-nni"
    " no dhcp-opt82-uplink circuit-id-dhcp physical-id remote-id-dhcp customer-id no relay-id-dhcp no dhcp-linerate"
    " no pppoe-linerate no dhcpv6-linerate no pppoe-l2-encaps no dhcp-l2-encaps no dhcpv6-l2-encaps no l2-encaps1"
    " no pppoer-vlanaware no dhcpr-vlanaware no dhcpv6r-vlanaware no circuit-id-pppoe no remote-id-pppoe"
    " no dhcpv6-itf-id no dhcpv6-remote-id no dhcpv6-relay-id no dhcpv6-trst-port no enterprise-number"
    " no icmpv6-sec-fltr",
])
CONFIGURED = (
    "configure vlan id 99 mode residential-bridge name MGMT-1 new-secure-fwd enable in-qos-prof-name name:Default_TC0"
    " dhcp-opt82-ext add-or-forward circuit-id-dhcp physical-id remote-id-dhcp customer-id"
)


def _facts(text):
    facts = {"ansible_network_resources": {}}
    VlansFacts(MagicMock()).populate_facts(None, facts, data=text)
    return {v["id"]: v for v in facts["ansible_network_resources"]["vlans"]}


def test_detail_values_match_configured_read():
    detail = _facts(DETAIL)["99"]
    configured = _facts(CONFIGURED)["99"]
    # Detail adds explicit False for the "no <flag>" defaults; values agree otherwise.
    assert {k: v for k, v in detail.items() if v is not False} == {k: v for k, v in configured.items() if v is not False}
    # device defaults are not reported (detail prints them explicitly, flat omits them)
    assert "new-broadcast" not in detail and "protocol-filter" not in detail


def test_explicit_new_broadcast_values_still_parse():
    for value in ("enable", "disable"):
        assert _facts("configure vlan id 5 new-broadcast %s" % value)["5"]["new_broadcast"] == value
    assert "new-broadcast" not in _facts("configure vlan id 5 new-broadcast inherit")["5"]  # the default


class TestVlansGaps(_Base):
    def _run(self, state, config, facts_text):
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

    def test_merged_idempotent_on_detail(self):
        config = [{"id": "99", "mode": "residential-bridge", "name": "MGMT-1", "new-secure-fwd": "enable",
                   "in-qos-prof-name": "name:Default_TC0", "dhcp-opt82-ext": "add-or-forward",
                   "circuit-id-dhcp": "physical-id", "remote-id-dhcp": "customer-id"}]
        for text in (DETAIL, CONFIGURED):
            assert self._run("merged", config, text)["commands"] == []
        assert self._run("merged", [{"id": "99", "new-broadcast": "disable"}], DETAIL)["commands"] == [
            "configure vlan id 99 new-broadcast disable"]


# Gap report of the lab capture --------------------------------------------------------

from . import lab_captures

_capture = lab_captures.read


def test_capture_gap_report_empty():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam import config_tree

    tree = config_tree.parse_config_tree(_capture("root-detail-flat.txt"))
    entry = config_tree.gap_report(tree)["families"]["vlans"]
    assert entry["unmodelled"] == {} and not entry.get("value_like")


@pytest.mark.parametrize("name", lab_captures.NAMES)
def test_capture_every_token_is_modelled_and_read_into_its_field(name):
    """Each "configure vlan id" token of the capture belongs to a modelled option and
    each value lands in that option of the facts; "no X" reads as False or the default."""
    import shlex

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import VLAN_ATTRS

    option_of = dict((cli, option) for option, cli, _kind, _default in VLAN_ATTRS)
    flags = set(cli for _option, cli, kind, _default in VLAN_ATTRS if kind == "flag")

    text = _capture(name)
    spec = VlansArgs.argument_spec["config"]["options"]
    facts = _facts(text)
    checked = 0
    for line in text.splitlines():
        if not line.startswith("configure vlan id "):
            continue
        tokens = shlex.split(line)[3:]
        entry = facts[tokens[0]]
        i = 1
        while i < len(tokens):
            negated = tokens[i] == "no"
            cli = tokens[i + 1] if negated else tokens[i]
            assert cli in option_of, (line, cli)
            key = option_of[cli]
            if cli in flags:
                expected = True if not negated else None  # a flag that is off is the default
                assert entry.get(key) is expected, (line, key)
                i += 2 if negated else 1
            elif negated:
                assert entry.get(key) is None, (line, key, entry.get(key))
                i += 2
            else:
                expected = int(tokens[i + 1]) if spec[key]["type"] == "int" else tokens[i + 1]
                if VLAN_DEFAULTS.get(key) == expected:
                    expected = None  # a device default is not reported
                assert entry.get(key) == expected, (line, key, entry.get(key))
                i += 2
            checked += 1
    assert checked > 1000 if "detail" in name else checked > 100


ALL_VLANS = pathlib.Path(__file__).parents[4] / "fixtures" / "vlans" / "r6.2.04m-all-vlans"


def test_rendering_the_parsed_lab_vlans_reproduces_the_device_lines(monkeypatch):
    """One grammar for reading and writing: parse -> render gives the device's own lines."""
    from .module_runner import run_module

    flat = (ALL_VLANS / "output.txt").read_text()
    parsed = run_module(monkeypatch, "isam_vlans", {"state": "parsed", "running_config": flat})["parsed"]
    detail = run_module(monkeypatch, "isam_vlans", {"state": "parsed", "running_config": (ALL_VLANS / "output-detail.txt").read_text()})["parsed"]
    assert len(parsed) == 47 and parsed == detail
    rendered = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": parsed})["rendered"]
    assert rendered == flat.splitlines()


def test_table_argspec_and_documentation_agree():
    import yaml

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import VLAN_ATTRS
    from ansible_collections.nokia.isam.plugins.modules import isam_vlans

    options = VlansArgs.argument_spec["config"]["options"]
    documented = yaml.safe_load(isam_vlans.DOCUMENTATION)["options"]["config"]["suboptions"]
    assert set(options) == set(documented) == set(["id"] + [option for option, _cli, _kind, _default in VLAN_ATTRS])
    for option, cli, _kind, default in VLAN_ATTRS:
        assert "default" not in options[option], option  # device defaults are not injected
        if cli != option:
            assert options[option]["aliases"] == [cli] and documented[option]["aliases"] == [cli], option


def test_old_cli_spelled_options_still_work_and_new_vlans_need_a_mode(monkeypatch):
    from .module_runner import run_module

    running = "configure vlan id 110 mode residential-bridge name Internet\n"
    result = run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": [{"id": 110, "protocol-filter": "pass-pppoe"}]}, running)
    assert result["commands"] == ["configure vlan id 110 protocol-filter pass-pppoe"]
    result = run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": [{"id": 3999, "name": "x"}]}, running)
    assert result.get("failed") and "mode is required" in result["msg"]


def test_a_name_with_spaces_is_sent_in_double_quotes(monkeypatch):
    """Lab ISAM: single quotes are an invalid token; the device prints such names in double quotes."""
    from .module_runner import run_module

    rendered = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": [
        {"id": 3991, "mode": "residential-bridge", "name": "zztest 3991"}, {"id": 3990, "mode": "residential-bridge", "name": "a-b_c"}]})["rendered"]
    assert rendered == ['configure vlan id 3991 mode residential-bridge name "zztest 3991"',
                        "configure vlan id 3990 mode residential-bridge name a-b_c"]


def test_dhcp_opt82_nni_and_uplink_are_values_sent_with_their_dependency(monkeypatch):
    """Lab ISAM: the bare keyword is 'not complete'; enable/add-or-* need circuit-id-dhcp,
    remote-id-dhcp or relay-id-dhcp in the same command (error 657); not settable at creation."""
    from .module_runner import run_module

    running = "configure vlan id 3990 mode residential-bridge name zztest\n"
    want = [{"id": 3990, "dhcp_opt82_nni": "add-or-forward", "dhcp_opt82_uplink": "add-or-replace", "circuit_id_dhcp": "physical-id"}]
    assert run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": want}, running)["commands"] == [
        "configure vlan id 3990 dhcp-opt82-nni add-or-forward dhcp-opt82-uplink add-or-replace circuit-id-dhcp physical-id"]
    configured = running + "configure vlan id 3990 dhcp-opt82-nni transparent\n"
    assert run_module(monkeypatch, "isam_vlans", {"state": "gathered"}, configured)["gathered"][0]["dhcp_opt82_nni"] == "transparent"
    created = run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": [
        {"id": 3991, "mode": "residential-bridge", "dhcp_opt82_nni": "enable", "relay_id_dhcp": "relay-id"}]}, "")["commands"]
    assert created == ["configure vlan id 3991 mode residential-bridge", "configure vlan id 3991 dhcp-opt82-nni enable relay-id-dhcp relay-id"]


def test_commands_are_packed_like_the_two_printed_lines(monkeypatch):
    """The device prints line 1 (mode .. mac-unauth) and line 2 (vmac-translation ..
    icmpv6-sec-fltr); DHCP and PPPoE ids and l2-encaps1 all belong to line 2."""
    from .module_runner import run_module

    config = [{"id": 3990, "mode": "residential-bridge", "name": "x", "priority": 3, "dhcp_opt82_ext": "enable",
               "circuit_id_dhcp": "physical-id", "l2_encaps1": "single-tagged", "circuit_id_pppoe": "physical-id",
               "dhcpv6_trst_port": "trusted"}]
    assert run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": config})["rendered"] == [
        "configure vlan id 3990 mode residential-bridge name x priority 3",
        "configure vlan id 3990 dhcp-opt82-ext enable circuit-id-dhcp physical-id l2-encaps1 single-tagged "
        "circuit-id-pppoe physical-id dhcpv6-trst-port trusted"]


# Explicit defaults and False name an attribute (state contract) ------------------------

NAMED_DEVICE = "configure vlan id 100 mode residential-bridge name foo protocol-filter pass-pppoe sntp-proxy\n"


@pytest.mark.parametrize("attribute, command", [
    ({"protocol_filter": "pass-all"}, "configure vlan id 100 no protocol-filter"),
    ({"sntp_proxy": False}, "configure vlan id 100 no sntp-proxy"),
])
def test_deleted_with_a_default_or_false_resets_only_that_attribute(monkeypatch, attribute, command):
    """Naming an attribute with its default value (or False) resets only it; the VLAN stays."""
    from .module_runner import run_module

    result = run_module(monkeypatch, "isam_vlans", {"state": "deleted", "config": [dict({"id": 100}, **attribute)]},
                        NAMED_DEVICE)
    assert result["commands"] == [command]
    # already at the default: nothing to reset
    done = NAMED_DEVICE.replace(" protocol-filter pass-pppoe sntp-proxy", "")
    assert run_module(monkeypatch, "isam_vlans", {"state": "deleted", "config": [dict({"id": 100}, **attribute)]},
                      done)["commands"] == []


@pytest.mark.parametrize("attribute, command", [
    ({"protocol_filter": "pass-all"}, "configure vlan id 100 protocol-filter pass-all"),
    ({"sntp_proxy": False}, "configure vlan id 100 no sntp-proxy"),
])
def test_merged_with_a_default_or_false_resets_a_non_default_value(monkeypatch, attribute, command):
    from .module_runner import run_module

    config = [dict({"id": 100}, **attribute)]
    assert run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": config}, NAMED_DEVICE)["commands"] == [command]
    done = NAMED_DEVICE.replace(" protocol-filter pass-pppoe sntp-proxy", "")
    for state in ("merged", "replaced"):
        full = [dict({"id": 100, "mode": "residential-bridge", "name": "foo"}, **attribute)]
        assert run_module(monkeypatch, "isam_vlans", {"state": state, "config": full}, done)["commands"] == [], state


def test_replaced_with_explicit_defaults_is_idempotent(monkeypatch):
    from .module_runner import run_module

    config = [{"id": 100, "mode": "residential-bridge", "name": "foo", "protocol_filter": "pass-all", "sntp_proxy": False}]
    assert run_module(monkeypatch, "isam_vlans", {"state": "replaced", "config": config}, NAMED_DEVICE)["commands"] == [
        "configure vlan id 100 no sntp-proxy protocol-filter pass-all"]
    assert run_module(monkeypatch, "isam_vlans", {"state": "overridden", "config": config},
                      "configure vlan id 100 mode residential-bridge name foo\n")["commands"] == []


@pytest.mark.parametrize("name", ['say "hi"', 'end"', "back\\slash", "it's", 'a"b', "tab#?", "plain"])
def test_a_name_round_trips_through_render_and_gather(monkeypatch, name):
    """CLI guide: printable strings with " \\ ? # or spaces are double-quoted, " and \\ escaped."""
    from .module_runner import run_module

    config = [{"id": "100", "mode": "residential-bridge", "name": name}]
    rendered = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": config})["rendered"]
    gathered = run_module(monkeypatch, "isam_vlans", {"state": "gathered"}, rendered[0] + "\n")["gathered"]
    assert gathered == config
    assert run_module(monkeypatch, "isam_vlans", {"state": "merged", "config": config}, rendered[0] + "\n")["commands"] == []


def test_name_quoting_follows_the_cli_guide(monkeypatch):
    from .module_runner import run_module

    rendered = run_module(monkeypatch, "isam_vlans", {"state": "rendered", "config": [
        {"id": 1, "name": 'a "b" \\c'}]})["rendered"]
    assert rendered == ['configure vlan id 1 name "a \\"b\\" \\\\c"']
    parsed = run_module(monkeypatch, "isam_vlans", {"state": "parsed", "running_config":
                        'configure vlan id 1 mode residential-bridge name hallo" "world\n'})["parsed"]
    assert parsed[0]["name"] == "hallo world"
    # a single quote is no special character for the CLI (shlex refused this line)
    parsed = run_module(monkeypatch, "isam_vlans", {"state": "parsed", "running_config":
                        "configure vlan id 1 mode residential-bridge name it's\n"})["parsed"]
    assert parsed[0]["name"] == "it's"
