"""isam_system_security: attribute gaps against the lab capture (radius policy servers, dyn-auth-client admin-down)."""
import pathlib

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_system_security
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    Isam_system_securityTemplate,
    normalize_policy,
)

from .isam_module import TestIsamModule, set_module_args
from . import lab_captures

ignore_provider_arg = True
CAPTURE = lab_captures.DETAIL

# realistic 'info configure detail flat' lines (secrets replaced)
DEVICE = [
    "configure system security radius dyn-auth-client DynAuth1 router-instance base ip-address 10.0.0.1 secret encrypted:aa:bb no admin-down",
    "configure system security radius dyn-auth-client DynAuth2 router-instance base ip-address 10.0.0.2 secret encrypted:cc:dd admin-down",
    "configure system security radius policy RADPol nas-id iSAM nas-ip-address 10.0.0.9 no keep-domain-name disable-accnt-msg no acc-interval disable-eap",
    "configure system security radius policy RADPol servers 1 auth-server name:RADAuthServ1 auth-router-inst base priority 128 no acc-server no acc-router-inst",
    "configure system security radius policy RADPol servers 2 auth-server name:RADAuthServ2 auth-router-inst base priority 162 no acc-server no acc-router-inst",
]

POLICY = {
    "name": "RADPol", "nas_id": "iSAM", "nas_ip_address": "10.0.0.9", "keep_domain_name": False,
    "disable_accnt_msg": True, "disable_eap": True,
    "servers": [
        {"index": 1, "auth_server": "name:RADAuthServ1", "auth_router_inst": "base", "priority": 128},
        {"index": 2, "auth_server": "name:RADAuthServ2", "auth_router_inst": "base", "priority": 162},
    ],
}


def _parse(lines):
    tmplt = Isam_system_securityTemplate(lines=lines, module=None)
    return tmplt.parse(), tmplt.unparsed


def test_parses_policy_servers_and_dyn_auth_admin_down():
    got, unparsed = _parse(DEVICE)
    assert unparsed == []
    assert got["radius_policies"] == [POLICY]
    assert [c["admin_down"] for c in got["radius_dyn_auth_clients"]] == [False, True]


def test_servers_line_before_policy_line():
    got, _unparsed = _parse([DEVICE[3], DEVICE[2]])
    assert got["radius_policies"][0]["servers"] == POLICY["servers"][:1]
    assert got["radius_policies"][0]["nas_id"] == "iSAM"


def test_render_round_trip():
    got, _unparsed = _parse(DEVICE)
    commands = []
    for section in ("radius_dyn_auth_clients", "radius_policies"):
        for entry in got[section]:
            commands.extend(Isam_system_securityTemplate.render_entry(section, entry))
    assert "configure system security radius policy RADPol servers 2 auth-server name:RADAuthServ2 auth-router-inst base priority 162" in commands
    assert any(c.endswith("DynAuth2 router-instance base ip-address 10.0.0.2 secret encrypted:cc:dd admin-down") for c in commands)
    again, unparsed = _parse(commands)
    assert unparsed == []
    assert again == got


def test_nested_remove_and_reset_forms():
    tmplt = Isam_system_securityTemplate
    assert tmplt.render_nested_remove("radius_policies", {"name": "RADPol"}, "servers", 2) == \
        "configure system security radius policy RADPol no servers 2"
    assert tmplt.render_nested_reset("radius_policies", {"name": "RADPol"}, "servers", {"index": 1, "priority": 128}) == [
        "configure system security radius policy RADPol servers 1 no priority"]
    assert tmplt.render_remove("radius_policies", {"name": "RADPol"}) == "configure system security radius no policy RADPol"


def test_normalize_legacy_flat_server_fields():
    assert normalize_policy({"name": "P", "auth_server": "name:A", "priority": 5, "servers": None}) == {
        "name": "P", "servers": [{"index": 1, "auth_server": "name:A", "priority": 5}]}
    # an explicit servers[index=1] value wins over the legacy flat value
    assert normalize_policy({"name": "P", "priority": 5, "servers": [{"index": 1, "priority": 7}]}) == {
        "name": "P", "servers": [{"index": 1, "priority": 7}]}
    assert normalize_policy({"name": "P", "nas_id": "x"}) == {"name": "P", "nas_id": "x"}


class TestIsamSystemSecurityGaps(TestIsamModule):
    module = isam_system_security

    def setUp(self):
        super(TestIsamSystemSecurityGaps, self).setUp()
        self.mocks = [patch(target) for target in (
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )]
        started = [m.start() for m in self.mocks]
        device = "\n".join(DEVICE) + "\n"

        class FakeConn:
            def get(self, cmd):
                return device
        started[2].return_value = FakeConn()

    def tearDown(self):
        super(TestIsamSystemSecurityGaps, self).tearDown()
        for mock in self.mocks:
            mock.stop()

    def _run(self, state, config, changed):
        set_module_args(dict(state=state, config=config), ignore_provider_arg)
        return self.execute_module(changed=changed)

    def test_merged_idempotent(self):
        got, _unparsed = _parse(DEVICE)
        self._run("merged", got, changed=False)

    def test_merged_legacy_flat_fields_idempotent(self):
        self._run("merged", {"radius_policies": [{
            "name": "RADPol", "auth_server": "name:RADAuthServ1", "auth_router_inst": "base", "priority": 128}]},
            changed=False)

    def test_merged_legacy_flat_fields_render_servers_1(self):
        result = self._run("merged", {"radius_policies": [{"name": "RADPol", "priority": 100}]}, changed=True)
        assert result["commands"] == [
            "configure system security radius policy RADPol",
            "configure system security radius policy RADPol servers 1 priority 100",
        ]

    def test_merged_adds_and_changes_servers_only(self):
        result = self._run("merged", {"radius_policies": [{"name": "RADPol", "servers": [
            {"index": 2, "priority": 170},
            {"index": 3, "auth_server": "name:RADAuthServ3", "auth_router_inst": "base"},
        ]}]}, changed=True)
        assert result["commands"] == [
            "configure system security radius policy RADPol",
            "configure system security radius policy RADPol servers 2 priority 170",
            "configure system security radius policy RADPol servers 3 auth-server name:RADAuthServ3 auth-router-inst base",
        ]

    def test_merged_dyn_auth_admin_down(self):
        result = self._run("merged", {"radius_dyn_auth_clients": [{"name": "DynAuth1", "admin_down": True}]}, changed=True)
        assert result["commands"] == ["configure system security radius dyn-auth-client DynAuth1 admin-down"]
        self._run("merged", {"radius_dyn_auth_clients": [{"name": "DynAuth2", "admin_down": True}]}, changed=False)

    def test_replaced_removes_and_resets_servers(self):
        result = self._run("replaced", {"radius_policies": [dict(POLICY, servers=[
            {"index": 1, "auth_server": "name:RADAuthServ1", "auth_router_inst": "base"}])]}, changed=True)
        assert result["commands"] == [
            "configure system security radius policy RADPol no servers 2",
            "configure system security radius policy RADPol servers 1 no priority",
        ]

    def test_replaced_resets_dyn_auth_admin_down(self):
        result = self._run("replaced", {"radius_dyn_auth_clients": [
            {"name": "DynAuth2", "router_instance": "base", "ip_address": "10.0.0.2", "secret": "********"}]}, changed=True)
        assert result["commands"] == ["configure system security radius dyn-auth-client DynAuth2 no admin-down"]

    def test_deleted_policy_removes_whole_policy(self):
        result = self._run("deleted", {"radius_policies": [{"name": "RADPol"}]}, changed=True)
        assert result["commands"] == ["configure system security radius no policy RADPol"]


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_policy_servers_parsed():
    lines = [l for l in CAPTURE.read_text(errors="replace").splitlines() if l.startswith("configure system security radius")]
    got, unparsed = _parse(lines)
    assert not unparsed
    servers = got["radius_policies"][0]["servers"]
    assert [s["index"] for s in servers] == [1, 2]
    assert all(s.get("auth_server") and s.get("priority") for s in servers)
    assert "priority" not in got["radius_policies"][0]
    assert all(c["admin_down"] is False for c in got["radius_dyn_auth_clients"])


def test_unknown_attribute_is_skipped_and_counted():
    tmplt = Isam_system_securityTemplate(lines=[
        "configure system security radius dyn-auth-client D1 ip-address 10.0.0.1 future-flag admin-down"], module=None)
    got = tmplt.parse()
    assert got["radius_dyn_auth_clients"][0]["admin_down"] is True
    assert tmplt.skipped == {"radius_dyn_auth_clients": 1}


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
@pytest.mark.parametrize("name", ["root-detail-flat.txt", "root-flat.txt"])
def test_capture_no_attribute_token_is_skipped(name):
    lines = [l for l in (CAPTURE.parent / name).read_text(errors="replace").splitlines()
             if l.startswith("configure system security ")]
    tmplt = Isam_system_securityTemplate(lines=lines, module=None)
    tmplt.parse()
    assert tmplt.skipped == {}  # section names and counts only


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_gap_report_only_false_positives():
    """Every name the gap report still lists for the family is modelled under another option.

    Asserts only booleans/sets of node names: attribute names of some nodes are values
    (an sftp-user's encrypted password), so they must never appear in a failure message.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
        gap_report,
        parse_config_tree,
    )
    text = CAPTURE.read_text(errors="replace")
    report = gap_report(parse_config_tree(text))["families"]["isam_system_security"]["unmodelled"]
    parsed, _unparsed = _parse([l for l in text.splitlines() if l.startswith("configure system security ")])
    profiles = dict((p["name"], p) for p in parsed["profiles"])

    def values(entries, *fields):
        return set(str(e.get(f)) for e in entries for f in fields)

    expected_nodes = set(["system security default-profile", "system security filetransfer protocol",
                          "system security password", "system security snmp notify-view",
                          "system security snmp view", "system security ssh sftp-user"]
                         + ["system security profile %s" % name for name in profiles])
    unexpected = sorted(set(report) - expected_nodes)
    assert unexpected == []  # node names only
    # permission area names ('<area> read|write|none' / 'no <area>') -> permissions dict keys
    areas = set(k for p in profiles.values() for k in p.get("permissions", {}))
    for node, attrs in report.items():
        attrs = set(attrs)
        if node == "system security default-profile":
            # default_profile.permissions (an unset area prints 'no <area>' and is not returned)
            mapped = areas | set(parsed["default_profile"].get("permissions", {}))
        elif node.startswith("system security profile "):
            mapped = set(profiles[node.split()[-1]].get("permissions", {}))  # -> profiles[].permissions keys
        elif node == "system security filetransfer protocol":
            mapped = set([parsed["filetransfer"]["protocol"]])  # value of filetransfer.protocol
        elif node == "system security password":
            mapped = set(str(v) for v in parsed["password"].values())  # values of password.min_length & co.
        elif node == "system security snmp view":
            mapped = values(parsed["snmp_views"], "name", "subtree", "type")  # snmp_views[] identity/type values
        elif node == "system security snmp notify-view":
            mapped = values(parsed["snmp_notify_views"], "name", "subtree", "type")
        else:  # ssh sftp-user: user name and (encrypted) password value -> ssh.sftp_users[].name/password
            mapped = values(parsed["ssh"]["sftp_users"], "name", "password")
        ok = attrs <= mapped
        assert ok, "unexpected unmodelled attribute(s) under %s (%d)" % (node, len(attrs - mapped))
