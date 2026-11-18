"""isam_system_security: operators, profiles, SNMP, RADIUS (slice 1)."""
import pathlib
from textwrap import dedent

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.plugins.modules import isam_system_security
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (
    Isam_system_securityTemplate,
)

from . import lab_captures
from .isam_module import TestIsamModule, set_module_args

ignore_provider_arg = True
CAPTURE = lab_captures.DETAIL


def test_template_parses_subregions():
    lines = [
        'configure system security operator isadmin password encrypted:aa:bb profile admin description "default administrator" no more',
        'configure system security profile admin description "admin group" slot-numbering type-based aaa write atm read no liadmin',
        'configure system security snmp community public host-address 10.0.0.1/32 read-view everything',
        'configure system security snmp view everything subtree * type include',
        'configure system security snmp manager tl1 destination 127.0.0.1:161 notify-profile tl1 nt no ihub',
        'configure system security radius auth-server RAD1 router-instance base ip-address 10.0.0.1 secret encrypted:cc:dd timeout-limit 5',
        'configure system security radius policy RADPol nas-id iSAM nas-ip-address 10.0.0.2 disable-eap',
        'configure system security radius auth-super-user operator-policy name:RADPol',
    ]
    got = Isam_system_securityTemplate(lines=lines, module=None).parse()
    assert got["operators"][0]["name"] == "isadmin"
    assert got["operators"][0]["profile"] == "admin"
    assert got["operators"][0]["more"] is False
    assert got["profiles"][0]["permissions"] == {"aaa": "write", "atm": "read", "liadmin": "none"}
    assert got["snmp_communities"][0]["host_address"] == "10.0.0.1/32"
    assert got["snmp_views"][0]["subtree"] == "*"
    assert got["snmp_managers"][0]["nt"] is True
    assert got["snmp_managers"][0]["ihub"] is False
    assert got["radius_auth_servers"][0]["timeout_limit"] == 5
    assert got["radius_policies"][0]["disable_eap"] is True
    assert got["radius_auth_super_user"]["operator_policy"] == "name:RADPol"


def test_render_round_trip():
    entry = {"name": "isadmin", "profile": "admin", "more": False}
    cmd = Isam_system_securityTemplate.render_entry("operators", entry)[0]
    assert cmd == "configure system security operator isadmin profile admin no more"
    again = Isam_system_securityTemplate(lines=[cmd], module=None).parse()
    assert again["operators"][0]["profile"] == "admin"
    assert again["operators"][0]["more"] is False


class TestIsamSystemSecurityModule(TestIsamModule):
    module = isam_system_security

    def setUp(self):
        super(TestIsamSystemSecurityModule, self).setUp()
        self.mock_get_resource_connection = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
        )
        self.get_resource_connection = self.mock_get_resource_connection.start()
        self.mock_get_resource_connection_config = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
        )
        self.get_resource_connection_config = self.mock_get_resource_connection_config.start()
        self.mock_get_resource_connection_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )
        self.get_resource_connection_facts = self.mock_get_resource_connection_facts.start()

    def tearDown(self):
        super(TestIsamSystemSecurityModule, self).tearDown()
        self.mock_get_resource_connection.stop()
        self.mock_get_resource_connection_config.stop()
        self.mock_get_resource_connection_facts.stop()

    def test_rendered_snmp_view(self):
        set_module_args(dict(state="rendered", config={
            "snmp_views": [{"name": "everything", "subtree": "*", "type": "include"}],
        }), ignore_provider_arg)
        rendered = self.execute_module(changed=False)["rendered"]
        assert "configure system security snmp view everything subtree * type include" in rendered

    def test_merged_idempotent(self):
        class FakeConn:
            def get(self, cmd):
                return "configure system security snmp view everything subtree * type include\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="merged", config={
            "snmp_views": [{"name": "everything", "subtree": "*", "type": "include"}],
        }), ignore_provider_arg)
        self.execute_module(changed=False)

    def test_deleted_removes_object(self):
        class FakeConn:
            def get(self, cmd):
                return "configure system security snmp view everything subtree * type include\n"
        self.get_resource_connection_facts.return_value = FakeConn()
        set_module_args(dict(state="deleted", config={"snmp_views": [{"name": "everything"}]}), ignore_provider_arg)
        result = self.execute_module(changed=True)
        # 'no' goes in front of the list node inside its parent; the subtree is part of the identity
        assert "configure system security snmp no view everything subtree *" in result["commands"]


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_registers_secrets_for_redaction():
    # validate_config(redact=True) records no_log values; Ansible masks them in exit_json.
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import Isam_system_securityArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.system_security.system_security import Isam_system_securityFacts
    lines = [l for l in CAPTURE.read_text().splitlines() if l.startswith("configure system security ")]
    set_module_args(dict(running_config="\n".join(lines), state="parsed"), ignore_provider_arg)
    module = basic.AnsibleModule(argument_spec=Isam_system_securityArgs.argument_spec, supports_check_mode=True)
    facts = {"ansible_network_resources": {}}
    Isam_system_securityFacts(module).populate_facts(None, facts, "\n".join(lines))
    parsed = facts["ansible_network_resources"]["isam_system_security"]
    assert parsed.get("operators")
    assert parsed.get("snmp_communities")
    # the plaintext community strings are registered as no_log (masked in module output)
    assert "public" in module.no_log_values
    assert "NETMAN" in module.no_log_values


# ----------------------------------------------------------------------------- slice 2

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import remove_empties  # noqa: E402
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system_security import (  # noqa: E402
    LISTS,
    SETTINGS,
)

CONFIGURED = CAPTURE.parent / "root-flat.txt"

# non-default lines covering every slice-2 node (no real secrets)
SLICE2 = [
    'configure system security oper-policy-prio local-radius login-banner "hello world" welcome-banner "Slot\\tKVz\\n1/1/1" unauth-fwd',
    'configure system security default-profile prompt "%n>" terminal-timeout 30 liadmin none liuser read ai read no aaa',
    'configure system security password min-length 8 min-num-numeric-char 1 min-num-special-char 2 mixed-case',
    'configure system security ssh server-profile server-retries 3 idle-timeout 600 dis-hmac-md5 dis-des-56 server-host-key rsa',
    'configure system security ssh access protocol sftp cli ssh tl1 none debug',
    'configure system security ssh sftp-user sftpuser password encrypted:00:11 auth-type password',
    'configure system security tacacs auth-super-user name:TacPol operator-policy name:TacPol',
    'configure system security li separate',
    'configure system security slot nt-a debug-usb',
    'configure system security domain Dom1 authenticator radius:RADPol vlan-id 100 sess-timeout 3600 admin-down',
    'configure system security filetransfer protocol sftp tftp-rollovr',
    'configure system security filetransfer server 10.0.0.9 user-name ftpuser password encrypted:22:33 key-type rsa',
    'configure system security snmp notify-view everything subtree * type include',
    'configure system security snmp notify-view everything subtree snmpUsmMIB type exclude',
    'configure system security peripheral-mgnt mac-filter 3 filter 00:11:22:33:44:55',
    'configure system security pae port-access',
    'configure system security pae port 1/1/4/19 initialize',
    'configure system security pae authenticator 1/1/4/19 controlled-port force-authorized quiet-period 30 re-auth-enabled',
    'configure system security pae ext-authenticator 1/1/4/19 authentication handshake-period 10 mab-auth',
]


def _parse(lines):
    tmplt = Isam_system_securityTemplate(lines=lines, module=None)
    return tmplt.parse(), tmplt.unparsed


def _render_all(config):
    """Render a parsed config back to commands, section by section."""
    commands = []
    for section in list(LISTS) + SETTINGS:
        value = config
        for part in section.split("."):
            value = (value or {}).get(part) if isinstance(value, dict) else None
        if section in LISTS:
            for entry in value or []:
                commands.extend(Isam_system_securityTemplate.render_entry(section, entry))
        elif value:
            own = dict((k, v) for k, v in value.items() if not isinstance(v, list))
            commands.extend(Isam_system_securityTemplate.render_entry(section, own))
    return commands


def _comparable(config):
    """Drop fixed instances without attributes ('mac-filter 1 no filter'): nothing to render."""
    config = remove_empties(config)
    for section, (ident, kind) in LISTS.items():
        if kind != "fixed":
            continue
        parent = config
        parts = section.split(".")
        for part in parts[:-1]:
            parent = parent.get(part) or {}
        if parts[-1] in parent:
            parent[parts[-1]] = [e for e in parent[parts[-1]] if set(e) - set(ident)]
    return remove_empties(config)


def test_slice2_parses_every_node():
    got, unparsed = _parse(SLICE2)
    assert unparsed == []
    assert got["general"] == {"oper_policy_prio": "local-radius", "login_banner": "hello world",
                              "welcome_banner": "Slot\\tKVz\\n1/1/1", "unauth_fwd": True}
    assert got["default_profile"] == {"prompt": "%n>", "terminal_timeout": "30",
                                      "permissions": {"liadmin": "none", "liuser": "read", "ai": "read"}}
    assert got["password"] == {"min_length": 8, "min_num_numeric_char": 1, "min_num_special_char": 2, "mixed_case": True}
    assert got["ssh"]["server_profile"]["dis_hmac_md5"] is True
    assert got["ssh"]["access"] == {"protocol": "sftp", "cli": "ssh", "tl1": "none", "debug": True}
    assert got["ssh"]["sftp_users"][0]["name"] == "sftpuser"
    assert got["tacacs"]["operator_policy"] == "name:TacPol"
    assert got["li"] == {"separate": True}
    assert got["slots"] == [{"slot": "nt-a", "debug_usb": True}]
    assert got["domains"][0]["vlan_id"] == 100 and got["domains"][0]["admin_down"] is True
    assert got["filetransfer"]["protocol"] == "sftp" and got["filetransfer"]["servers"][0]["user_name"] == "ftpuser"
    assert [v["subtree"] for v in got["snmp_notify_views"]] == ["*", "snmpUsmMIB"]
    assert got["peripheral_mgnt"]["mac_filters"] == [{"index": 3, "filter": "00:11:22:33:44:55"}]
    assert got["pae"]["port_access"] is True
    assert got["pae"]["ports"] == [{
        "port": "1/1/4/19", "initialize": True,
        "authenticator": {"controlled_port": "force-authorized", "quiet_period": 30, "re_auth_enabled": True},
        "ext_authenticator": {"authentication": True, "handshake_period": 10, "mab_auth": True},
    }]


def test_slice2_render_round_trip():
    got, _unparsed = _parse(SLICE2)
    again, unparsed = _parse(_render_all(got))
    assert unparsed == []
    assert again == got


def test_view_and_community_composite_identity():
    got, _unparsed = _parse([
        "configure system security snmp view protected subtree * type include",
        "configure system security snmp view protected subtree snmpUsmMIB type exclude",
        "configure system security snmp community c1 host-address 10.0.0.1/32",
        "configure system security snmp community c1 host-address 10.0.0.2/32 context ihub",
    ])
    assert len(got["snmp_views"]) == 2
    assert [c["host_address"] for c in got["snmp_communities"]] == ["10.0.0.1/32", "10.0.0.2/32"]
    assert Isam_system_securityTemplate.render_remove("snmp_communities", got["snmp_communities"][1]) == \
        "configure system security snmp no community c1 host-address 10.0.0.2/32"


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
@pytest.mark.parametrize("name", ["root-detail-flat.txt", "root-flat.txt"])
def test_capture_every_security_line_is_parsed(name):
    lines = [l for l in (CAPTURE.parent / name).read_text().splitlines() if l.startswith("configure system security ")]
    got, unparsed = _parse(lines)
    # no silent drops: every line maps to a node (only the count is shown, lines may hold secrets)
    missed = len(unparsed)
    assert missed == 0, "%d unparsed lines" % missed
    again, unparsed = _parse(_render_all(got))
    missed = len(unparsed)
    assert missed == 0, "%d rendered lines not parsed back" % missed
    same = _comparable(again) == _comparable(got)  # a bool: a diff could show secrets
    assert same, "render round trip differs"
    if name == "root-detail-flat.txt":
        assert len(lines) == 679
        assert len(got["pae"]["ports"]) == 204
        assert len(got["peripheral_mgnt"]["mac_filters"]) == 20
        assert len(got["snmp_views"]) == 7 and len(got["snmp_notify_views"]) == 2
        assert len(got["snmp_communities"]) == 5
        assert len(got["slots"]) == 2 and len(got["domains"]) == 1


@pytest.mark.skipif(not CAPTURE.exists(), reason="lab capture not available")
def test_capture_registers_slice2_secrets_for_redaction():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import Isam_system_securityArgs
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.system_security.system_security import Isam_system_securityFacts
    lines = [l for l in CAPTURE.read_text().splitlines() if l.startswith("configure system security ")]
    set_module_args(dict(running_config="\n".join(lines), state="parsed"), ignore_provider_arg)
    module = basic.AnsibleModule(argument_spec=Isam_system_securityArgs.argument_spec, supports_check_mode=True)
    facts = {"ansible_network_resources": {}}
    Isam_system_securityFacts(module).populate_facts(None, facts, "\n".join(lines))
    parsed = facts["ansible_network_resources"]["isam_system_security"]
    secrets = [u["password"] for u in parsed["ssh"]["sftp_users"]] + [s["password"] for s in parsed["filetransfer"]["servers"]]
    registered = bool(secrets) and all(secret in module.no_log_values for secret in secrets)
    assert registered, "slice-2 passwords are not registered as no_log values"


class TestIsamSystemSecuritySlice2(TestIsamModule):
    module = isam_system_security

    def setUp(self):
        super(TestIsamSystemSecuritySlice2, self).setUp()
        self.mocks = [patch(target) for target in (
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.cfg.base.get_resource_connection",
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection",
        )]
        started = [m.start() for m in self.mocks]
        device = "\n".join(SLICE2 + [
            "configure system security operator isadmin profile admin",
            "configure system security snmp view everything subtree * type include",
        ]) + "\n"

        class FakeConn:
            def get(self, cmd):
                return device
        started[2].return_value = FakeConn()

    def tearDown(self):
        super(TestIsamSystemSecuritySlice2, self).tearDown()
        for mock in self.mocks:
            mock.stop()

    def _run(self, state, config, changed):
        set_module_args(dict(state=state, config=config), ignore_provider_arg)
        return self.execute_module(changed=changed)

    def test_merged_idempotent(self):
        got, _unparsed = _parse(SLICE2)
        self._run("merged", got, changed=False)

    def test_merged_masked_secret_is_idempotent(self):
        self._run("merged", {"ssh": {"sftp_users": [{"name": "sftpuser", "password": "********"}]}}, changed=False)

    def test_merged_renders_only_changes(self):
        result = self._run("merged", {
            "password": {"min_length": 10, "mixed_case": True},
            "pae": {"ports": [{"port": "1/1/4/19", "authenticator": {"quiet_period": 60, "re_auth_enabled": True}},
                              {"port": "1/1/4/20", "ext_authenticator": {"authentication": True}}]},
            "peripheral_mgnt": {"mac_filters": [{"index": 4, "filter": "00:11:22:33:44:66"}]},
            "domains": [{"name": "Dom2", "authenticator": "radius:RADPol"}],
        }, changed=True)
        assert result["commands"] == [
            "configure system security domain Dom2 authenticator radius:RADPol",
            "configure system security peripheral-mgnt mac-filter 4 filter 00:11:22:33:44:66",
            "configure system security pae authenticator 1/1/4/19 quiet-period 60",
            "configure system security pae ext-authenticator 1/1/4/20 authentication",
            "configure system security password min-length 10",
        ]

    def test_replaced_resets_stale_attributes(self):
        result = self._run("replaced", {
            "pae": {"ports": [{"port": "1/1/4/19", "authenticator": {"controlled_port": "force-authorized"}}]},
            "ssh": {"access": {"protocol": "sftp", "cli": "ssh"}},
        }, changed=True)
        assert sorted(result["commands"]) == sorted([
            "configure system security pae port 1/1/4/19 no initialize",
            "configure system security pae authenticator 1/1/4/19 no quiet-period no re-auth-enabled",
            "configure system security pae ext-authenticator 1/1/4/19 no authentication no handshake-period no mab-auth",
            "configure system security ssh access no tl1 no debug",
        ])

    def test_deleted_named_instances(self):
        result = self._run("deleted", {
            "domains": [{"name": "Dom1"}],
            "slots": [{"slot": "nt-a"}],
            "snmp_notify_views": [{"name": "everything"}],
            "filetransfer": {"servers": [{"server": "10.0.0.9"}]},
            "ssh": {"sftp_users": [{"name": "sftpuser"}]},
            "pae": {"ports": [{"port": "1/1/4/19"}]},
        }, changed=True)
        assert result["commands"] == [
            "configure system security snmp no notify-view everything subtree *",
            "configure system security snmp no notify-view everything subtree snmpUsmMIB",
            "configure system security ssh no sftp-user sftpuser",
            "configure system security slot nt-a no debug-usb",
            "configure system security no domain Dom1",
            "configure system security filetransfer no server 10.0.0.9",
            "configure system security pae port 1/1/4/19 no initialize",
            "configure system security pae authenticator 1/1/4/19 no controlled-port no quiet-period no re-auth-enabled",
            "configure system security pae ext-authenticator 1/1/4/19 no authentication no handshake-period no mab-auth",
        ]
        # sections not named are untouched (operators, views, settings blocks)

    def test_deleted_settings_block(self):
        result = self._run("deleted", {"li": {"separate": True}, "password": {"min_length": 8}}, changed=True)
        assert result["commands"] == [
            "configure system security password no min-length no min-num-numeric-char no min-num-special-char no mixed-case",
            "configure system security li no separate",
        ]

    def test_rendered_quotes_values_with_spaces(self):
        result = self._run("rendered", {"general": {"login_banner": "hello world"}}, changed=False)
        assert result["rendered"] == ['configure system security login-banner "hello world"']
