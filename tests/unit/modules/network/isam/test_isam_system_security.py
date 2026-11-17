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

from .isam_module import TestIsamModule, set_module_args

ignore_provider_arg = True
CAPTURE = pathlib.Path("/path/to/pon-migration-planner/.local/root-detail-flat.txt")


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
        assert "configure system security no snmp view everything" in result["commands"]


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
    assert "example-ro" in module.no_log_values
