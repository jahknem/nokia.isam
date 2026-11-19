"""Replay actual Ansible-redacted facts, not the unsanitized test-runner result."""
from copy import deepcopy

import pytest
from ansible.module_utils.common.parameters import remove_values

from .module_runner import run_module


DEVICE = '''\
configure system security snmp community example-community host-address 192.0.2.1 privilege read-only
configure system security snmp notify-profile example snmp-version v1:example-community
configure system security radius auth-server example ip-address 192.0.2.2 secret plain:example-radius
configure system security radius dyn-auth-client example ip-address 192.0.2.3 secret plain:example-dynamic
configure system security operator example password encrypted:example-password profile admin
configure system security ssh sftp-user example password plain:example-sftp auth-type password-based
configure system security filetransfer server 192.0.2.4 password plain:example-transfer user-name example
'''
MARKERS = ("********", "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER", "plain:********",
           "encrypted:VALUE_SPECIFIED_IN_NO_LOG_PARAMETER")


@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_redacted_gathered_facts_are_safe_to_replay(monkeypatch, state):
    gathered = run_module(monkeypatch, "isam_system_security", {"state": "gathered"}, DEVICE)
    sanitized = remove_values(gathered["gathered"], gathered["_no_log_values"])
    result = run_module(monkeypatch, "isam_system_security", {"state": state, "config": sanitized}, DEVICE)
    assert not result.get("failed"), result.get("msg")
    assert result["commands"] == []
    assert any("redacted identity left unchanged" in warning for warning in result["_warnings"])


@pytest.mark.parametrize("marker", MARKERS)
@pytest.mark.parametrize("state", ["merged", "replaced"])
def test_masked_password_is_preserved_but_not_rendered_with_other_changes(monkeypatch, marker, state):
    config = {"operators": [{"name": "example", "password": marker, "profile": "readonly"}]}
    before = deepcopy(config)
    result = run_module(monkeypatch, "isam_system_security", {"state": state, "config": config}, DEVICE)
    assert result["commands"] == ["configure system security operator example profile readonly"]
    assert config == before


@pytest.mark.parametrize("state", ["merged", "rendered"])
def test_cannot_create_or_render_a_placeholder_secret(monkeypatch, state):
    result = run_module(monkeypatch, "isam_system_security", {"state": state, "config": {
        "operators": [{"name": "new", "password": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"}]}}, DEVICE)
    assert result.get("failed") and "redacted password" in result["msg"]


@pytest.mark.parametrize("state", ["deleted", "overridden", "rendered", "gathered"])
def test_redacted_identity_fails_closed_in_destructive_render_and_targeted_read_states(monkeypatch, state):
    result = run_module(monkeypatch, "isam_system_security", {"state": state, "config": {
        "snmp_communities": [{"name": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"}]}}, DEVICE)
    assert result.get("failed") and "identit" in result["msg"]
    if state == "gathered":
        assert result["_sent"] == []


def test_redacted_identity_cannot_create_or_change_a_community(monkeypatch):
    result = run_module(monkeypatch, "isam_system_security", {"state": "merged", "config": {
        "snmp_communities": [{"name": "********", "privilege": "read-write"}]}}, DEVICE)
    assert result["commands"] == []
    assert any("concrete identity" in warning for warning in result["_warnings"])


def test_concrete_community_identity_still_updates(monkeypatch):
    result = run_module(monkeypatch, "isam_system_security", {"state": "merged", "config": {
        "snmp_communities": [{"name": "example-community", "host_address": "192.0.2.1", "privilege": "read-write"}]}}, DEVICE)
    assert result["commands"] == [
        "configure system security snmp community example-community host-address 192.0.2.1 privilege read-write"]


@pytest.mark.parametrize("version", ["v1:********", "v1:VALUE_SPECIFIED_IN_NO_LOG_PARAMETER"])
def test_embedded_masked_community_is_idempotent(monkeypatch, version):
    result = run_module(monkeypatch, "isam_system_security", {"state": "merged", "config": {
        "snmp_notify_profiles": [{"name": "example", "snmp_version": version}]}}, DEVICE)
    assert result["commands"] == []


@pytest.mark.parametrize("state", ["merged", "rendered"])
def test_unknown_or_changed_notify_version_needs_concrete_community(monkeypatch, state):
    result = run_module(monkeypatch, "isam_system_security", {"state": state, "config": {
        "snmp_notify_profiles": [{"name": "new", "snmp_version": "v1:********"}]}}, DEVICE)
    assert result.get("failed") and "concrete community" in result["msg"]
    result = run_module(monkeypatch, "isam_system_security", {"state": state, "config": {
        "snmp_notify_profiles": [{"name": "example", "snmp_version": "v2c:********"}]}}, DEVICE)
    assert result.get("failed") and "concrete community" in result["msg"]


def test_explicit_password_update_still_emits_a_command_and_registers_redaction(monkeypatch):
    result = run_module(monkeypatch, "isam_system_security", {"state": "merged", "config": {
        "operators": [{"name": "example", "password": "plain:replacement-example"}]}}, DEVICE)
    assert len(result["commands"]) == 1
    assert "password plain:replacement-example" in result["commands"][0]
    assert "plain:replacement-example" in result["_no_log_values"]


def test_existing_device_mask_never_leaks_into_an_unrelated_update(monkeypatch):
    device = "configure system security operator example password encrypted:******** profile admin\n"
    result = run_module(monkeypatch, "isam_system_security", {"state": "merged", "config": {
        "operators": [{"name": "example", "profile": "readonly"}]}}, device)
    assert result["commands"] == ["configure system security operator example profile readonly"]


def test_view_wildcard_is_a_real_identity_not_a_masked_credential(monkeypatch):
    result = run_module(monkeypatch, "isam_system_security", {"state": "rendered", "config": {
        "snmp_views": [{"name": "example", "subtree": "*", "type": "include"}]}})
    assert result["rendered"] == ["configure system security snmp view example subtree * type include"]
