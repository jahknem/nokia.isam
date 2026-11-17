"""vlans against `info configure detail flat` of a real ISAM.

Every "vlan id" attribute of the capture is modelled (argspec keys keep the CLI
spelling, so the gap report's snake_case lookup lists them all as false positives).
Detail lines parse to the same values as the configured-only read, and merged is
idempotent on them ("no new-broadcast" is the default, inherit).
"""
import os

import pytest

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
    "configure vlan id 99 mode residential-bridge name TR69-1 no sntp-proxy no priority no vmac-not-in-opt61"
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
    "configure vlan id 99 mode residential-bridge name TR69-1 new-secure-fwd enable in-qos-prof-name name:Default_TC0"
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
    assert detail["new-broadcast"] == "inherit"
    assert detail["protocol-filter"] == "pass-all"


def test_explicit_new_broadcast_values_still_parse():
    for value in ("enable", "disable", "inherit"):
        assert _facts("configure vlan id 5 new-broadcast %s" % value)["5"]["new-broadcast"] == value


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
        config = [{"id": "99", "mode": "residential-bridge", "name": "TR69-1", "new-secure-fwd": "enable",
                   "in-qos-prof-name": "name:Default_TC0", "dhcp-opt82-ext": "add-or-forward",
                   "circuit-id-dhcp": "physical-id", "remote-id-dhcp": "customer-id"}]
        for text in (DETAIL, CONFIGURED):
            assert self._run("merged", config, text)["commands"] == []
        assert self._run("merged", [{"id": "99", "new-broadcast": "disable"}], DETAIL)["commands"] == [
            "configure vlan id 99 new-broadcast disable"]


# Gap report of the lab capture --------------------------------------------------------

CAPTURES = os.environ.get("ISAM_ROOT_CAPTURES") or os.path.join(
    os.path.dirname(os.path.realpath(__file__)),
    *([os.pardir] * 6 + ["pon-migration-planner", ".local"])
)


def _capture(name):
    path = os.path.join(CAPTURES, name)
    if not os.path.exists(path):
        pytest.skip("lab capture not available")
    with open(path, errors="replace") as handle:
        return handle.read()


def test_capture_gap_report_empty():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam import config_tree

    tree = config_tree.parse_config_tree(_capture("root-detail-flat.txt"))
    entry = config_tree.gap_report(tree)["families"]["vlans"]
    assert entry["unmodelled"] == {} and not entry.get("value_like")


@pytest.mark.parametrize("name", ["root-detail-flat.txt", "root-flat.txt"])
def test_capture_every_token_is_modelled_and_read_into_its_field(name):
    """Each "configure vlan id" token of the capture belongs to a modelled option and
    each value lands in that option of the facts; "no X" reads as False or the default."""
    import shlex

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.vlans import (
        _VLAN_BOOLEAN_FIELDS,
    )

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
            key = tokens[i + 1] if negated else tokens[i]
            assert key in spec, (line, key)
            if key in _VLAN_BOOLEAN_FIELDS:
                assert entry.get(key) is (not negated), (line, key)
                i += 2 if negated else 1
            elif negated:
                assert entry.get(key) in (None, spec[key].get("default")), (line, key, entry.get(key))
                i += 2
            else:
                expected = int(tokens[i + 1]) if spec[key]["type"] == "int" else tokens[i + 1]
                assert entry.get(key) == expected, (line, key, entry.get(key))
                i += 2
            checked += 1
    assert checked > 1000 if "detail" in name else checked > 100
