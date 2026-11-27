"""isam_system_security: overridden refuses to remove a RADIUS server or policy still referenced."""
from ansible_collections.nokia.isam.plugins.modules import isam_system_security
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args

ignore_provider_arg = True

_SEC = "configure system security "
DEVICE = [
    _SEC + "radius auth-server RADAuthServ1 router-instance base ip-address 192.0.2.1 secret encrypted:aa:bb",
    _SEC + "radius auth-server RADAuthServ2 router-instance base ip-address 192.0.2.2 secret encrypted:cc:dd",
    _SEC + "radius auth-server RADAuthServ3 router-instance base ip-address 192.0.2.3 secret encrypted:ee:ff",
    _SEC + "radius policy RADPol servers 1 auth-server name:RADAuthServ1 auth-router-inst base priority 128",
    _SEC + "radius policy RADPol servers 2 auth-server name:RADAuthServ2 auth-router-inst base priority 162",
    _SEC + "radius policy DomPol servers 1 auth-server name:RADAuthServ1 auth-router-inst base",
    _SEC + "radius policy Spare nas-id spare",
    _SEC + "radius auth-super-user operator-policy name:RADPol",
    _SEC + "domain Dom1 authenticator radius:DomPol",
]

RADPOL = {"name": "RADPol", "servers": [
    {"index": 1, "auth_server": "name:RADAuthServ1", "auth_router_inst": "base", "priority": 128},
    {"index": 2, "auth_server": "name:RADAuthServ2", "auth_router_inst": "base", "priority": 162}]}
DOMPOL = {"name": "DomPol", "servers": [{"index": 1, "auth_server": "name:RADAuthServ1", "auth_router_inst": "base"}]}
SPARE = {"name": "Spare", "nas_id": "spare"}


def _server(index):
    return {"name": "RADAuthServ%d" % index, "router_instance": "base", "ip_address": "192.0.2.%d" % index,
            "secret": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"}


class TestIsamSystemSecurityReferences(TestIsamModule):
    module = isam_system_security

    def setUp(self):
        super(TestIsamSystemSecurityReferences, self).setUp()
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
        super(TestIsamSystemSecurityReferences, self).tearDown()
        for mock in self.mocks:
            mock.stop()

    def _run(self, config, failed=False):
        set_module_args(dict(state="overridden", config=config), ignore_provider_arg)
        if failed:
            return self.execute_module(failed=True)
        return self.execute_module(changed=True)

    def test_refuses_to_remove_a_server_a_device_policy_uses(self):
        # radius_policies is not named: every device policy is kept with its servers
        result = self._run({"radius_auth_servers": [_server(1)]}, failed=True)
        assert "RADAuthServ2 (policy RADPol)" in result["msg"]
        assert "RADAuthServ3" not in result["msg"]
        assert "192.0.2" not in result["msg"] and "encrypted" not in result["msg"]

    def test_removes_an_unreferenced_server(self):
        result = self._run({"radius_auth_servers": [_server(1), _server(2)]})
        assert result["commands"] == [_SEC + "radius no auth-server RADAuthServ3"]

    def test_refuses_a_server_a_kept_policy_still_references_on_the_device(self):
        # The policy drops servers 2 in the same run, but the server removal is sent
        # first, while the device policy still references it.
        result = self._run({"radius_auth_servers": [_server(1), _server(3)],
                            "radius_policies": [dict(RADPOL, servers=RADPOL["servers"][:1]), DOMPOL, SPARE]},
                           failed=True)
        assert "RADAuthServ2 (policy RADPol)" in result["msg"]

    def test_refuses_a_server_a_requested_policy_references(self):
        result = self._run({"radius_auth_servers": [_server(1), _server(2)],
                            "radius_policies": [RADPOL, DOMPOL, dict(SPARE, servers=[
                                {"index": 1, "auth_server": "RADAuthServ3"}])]}, failed=True)
        assert "RADAuthServ3 (policy Spare)" in result["msg"]

    def test_removes_an_unreferenced_policy(self):
        result = self._run({"radius_policies": [RADPOL, DOMPOL]})
        assert result["commands"] == [_SEC + "radius no policy Spare"]

    def test_refuses_to_remove_the_auth_super_user_operator_policy(self):
        result = self._run({"radius_policies": [DOMPOL, SPARE]}, failed=True)
        assert "RADPol (auth-super-user operator-policy)" in result["msg"]

    def test_refuses_to_remove_a_policy_a_kept_domain_uses(self):
        result = self._run({"radius_policies": [RADPOL, SPARE]}, failed=True)
        assert "DomPol (domain Dom1)" in result["msg"]

    def test_refuses_a_policy_a_kept_domain_moves_away_from_in_the_same_run(self):
        result = self._run({"radius_policies": [RADPOL, SPARE],
                            "domains": [{"name": "Dom1", "authenticator": "radius:Spare"}]}, failed=True)
        assert "DomPol (domain Dom1)" in result["msg"]


    def test_an_accounting_server_reference_does_not_block_an_auth_server_removal(self):
        # Review of #19: acc_server names a radius acc-server, a different object than
        # the auth servers this module manages; an auth server of the same name may go.
        device = "\n".join([
            _SEC + "radius auth-server RADAuthServ1 router-instance base ip-address 192.0.2.1 secret encrypted:aa:bb",
            _SEC + "radius auth-server RADAuthServ3 router-instance base ip-address 192.0.2.3 secret encrypted:ee:ff",
            _SEC + "radius policy AccPol servers 1 acc-server name:RADAuthServ3 acc-router-inst base",
        ]) + "\n"

        class Conn:
            def get(self, cmd):
                return device
        with patch("ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts."
                   "get_resource_connection") as conn:
            conn.return_value = Conn()
            # name a different server, so the auth-server list is overridden
            set_module_args(dict(state="overridden", config={"radius_auth_servers": [_server(1)]}),
                            ignore_provider_arg)
            result = self.execute_module(changed=True)
        assert "configure system security radius no auth-server RADAuthServ3" in result["commands"], result["commands"]


# -- removal order: a referrer before what it refers to --------------------------------------

from .module_runner import run_module  # noqa: E402


def _order(commands, *fragments):
    positions = []
    for fragment in fragments:
        hits = [i for i, c in enumerate(commands) if c.endswith(fragment)]
        assert hits, (fragment, commands)
        positions.append(hits[0])
    return positions


def test_overridden_removes_a_policy_before_the_server_it_uses(monkeypatch):
    # The gap: P1 and the server S1 it uses both go in one overridden run. Rendered in
    # list order (auth servers before policies), 'no auth-server S1' came first and the
    # device refused it while P1 still named S1. Removals of policies and servers now go
    # last, policies first.
    device = "\n".join([
        _SEC + "radius auth-server S1 router-instance base ip-address 192.0.2.1 secret encrypted:aa:bb",
        _SEC + "radius auth-server S2 router-instance base ip-address 192.0.2.2 secret encrypted:cc:dd",
        _SEC + "radius policy P1 servers 1 auth-server name:S1 auth-router-inst base",
    ]) + "\n"
    config = {"radius_auth_servers": [{"name": "S2", "router_instance": "base", "ip_address": "192.0.2.2",
                                       "secret": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"}],
              "radius_policies": [{"name": "P2", "servers": [
                  {"index": 1, "auth_server": "name:S2", "auth_router_inst": "base"}]}]}
    result = run_module(monkeypatch, "isam_system_security", {"state": "overridden", "config": config}, device)
    assert not result.get("failed"), result.get("msg")
    commands = result["commands"]
    create, policy, server = _order(commands, "radius policy P2 servers 1 auth-server name:S2 auth-router-inst base",
                                    "radius no policy P1", "radius no auth-server S1")
    assert create < policy < server, commands
    assert commands[-2:] == [commands[policy], commands[server]], commands


def test_deleting_everything_removes_referrers_first(monkeypatch):
    result = run_module(monkeypatch, "isam_system_security", {"state": "deleted"}, "\n".join(DEVICE) + "\n")
    assert not result.get("failed"), result.get("msg")
    commands = result["commands"]
    domain, policy, server = _order(commands, "no domain Dom1", "radius no policy DomPol",
                                    "radius no auth-server RADAuthServ1")
    assert domain < policy < server, commands
    super_user = [i for i, c in enumerate(commands) if "auth-super-user" in c and " no " in c]
    assert super_user and super_user[0] < policy, commands
