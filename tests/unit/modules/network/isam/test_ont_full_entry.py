"""Gathered ONT configuration must be usable directly as merged/deleted input.

Real modules and real parsers, synthetic device replies, no SSH or credentials.
edit_config raises even when a test expects changes: all comparisons run in check
mode. No NOC dependency; this is the collection's own round-trip contract.
"""
import copy
import importlib
import json
import sys

import pytest
from ansible.module_utils import basic

from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleExitJson
from .isam_module import set_module_args


ONT = "1/1/5/1/3"
UNI = ONT + "/1/1"
TARGET = "1/1/5/2/50"
SIBLING = "1/1/5/1/30"

CONFIGS = {
    "equipment_onts": "\n".join([
        "configure equipment ont interface %s sw-ver-pland auto sernum XXXX:00000003 admin-state up log-auth-pwd plain:******" % ONT,
        "configure equipment ont slot %s/1 planned-card-type ethernet plndnumdataports 1 plndnumvoiceports 0" % ONT,
    ]),
    "ethernet_onts": 'configure ethernet ont %s cust-info "Example customer" auto-detect auto admin-state up' % UNI,
    "interfaces": "\n".join([
        "configure interface port ont:%s admin-up link-updown-trap" % ONT,
        'configure interface port uni:%s admin-up user "Example customer"' % UNI,
        "configure interface port vlan-port:%s:10 admin-up severity no-value" % UNI,
    ]),
    "bridges": "\n".join([
        "configure bridge port %s max-unicast-mac 5 pvid 99" % UNI,
        "configure bridge port %s vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local" % UNI,
        "configure bridge port %s vlan-id 99" % UNI,
    ]),
    "qos_interfaces": "\n".join([
        "configure qos interface %s scheduler-node name:Example oper-weight 50 oper-rate 0" % UNI,
        "configure qos interface %s queue 0 priority 6 weight 34 oper-weight 34 queue-profile name:Example" % UNI,
        "configure qos interface %s upstream-queue 0 weight 5 bandwidth-profile name:Example bandwidth-sharing uni-sharing" % UNI,
        "configure qos interface %s upstream-queue 1 weight 6 bandwidth-profile name:Sibling" % UNI,
        "configure qos interface %s ds-rem-queue 0 priority 6 weight 34" % UNI,
    ]),
    "ntp_onts": "configure ntp ont %s" % ONT,
    "ani_onts": "configure ani ont tca-thresh %s" % ONT,
}


def call_module(monkeypatch, family, config=None, state="gathered", running=None):
    module = importlib.import_module("ansible_collections.nokia.isam.plugins.modules.isam_" + family)
    # Load fact readers before patching names imported directly into them.
    importlib.import_module("ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts")
    text = CONFIGS[family] if running is None else running

    class Connection:
        def get(self, command, *args, **kwargs):
            assert command.startswith("info configure "), command
            # Include an unrelated ONT in every reply to exercise targeted deletion.
            return text + "\n" + text.replace(ONT, SIBLING) if text else ""

        def edit_config(self, *args, **kwargs):
            raise AssertionError("check mode must never call edit_config")

    warnings = []

    def exit_json(self, **result):
        result["warnings"] = warnings
        raise AnsibleExitJson(result)

    def fail_json(self, **result):
        raise AssertionError(result.get("msg"))

    with monkeypatch.context() as patch:
        connection = Connection()
        fact_module = importlib.import_module(
            "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.%s.%s" % (family, family)
        )
        # Older unittest classes leave patched get_config methods behind; isolate
        # the transport explicitly, while retaining every real parser/comparator.
        for loaded in vars(fact_module).values():
            if isinstance(loaded, type) and loaded.__module__ == fact_module.__name__ and hasattr(loaded, "get_config"):
                patch.setattr(loaded, "get_config", lambda self, conn: connection.get("info configure fixture"))
        for name, loaded in tuple(sys.modules.items()):
            if name.startswith("ansible_collections.") and hasattr(loaded, "get_resource_connection"):
                patch.setattr(loaded, "get_resource_connection", lambda *a, **kw: connection)
        patch.setattr(basic.AnsibleModule, "exit_json", exit_json)
        patch.setattr(basic.AnsibleModule, "fail_json", fail_json)
        patch.setattr(basic.AnsibleModule, "warn", lambda self, message: warnings.append(message))
        args = {"state": state, "_ansible_check_mode": True}
        if state == "parsed":
            args["running_config"] = text
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        with pytest.raises(AnsibleExitJson) as result:
            module.main()
        return result.value.args[0]


def selected(data):
    """Only the source ONT, not its sibling (3 vs 30)."""
    def items(entries):
        return [entry for entry in entries if any(
            isinstance(value, str) and (value.endswith(ONT) or ONT + "/" in value or ONT + ":" in value)
            for value in entry.values()
        )]
    if isinstance(data, list):
        return items(data)
    return {key: items(value) for key, value in data.items() if isinstance(value, list) and items(value)}


@pytest.mark.parametrize("family", CONFIGS)
def test_gathered_full_entry_is_idempotent_and_can_be_deleted(monkeypatch, family):
    data = selected(call_module(monkeypatch, family)["gathered"])
    assert data, family
    unchanged = call_module(monkeypatch, family, data, "merged")
    assert not unchanged["changed"]
    assert unchanged["commands"] == []
    deleted = call_module(monkeypatch, family, data, "deleted")
    assert deleted["changed"]
    assert deleted["commands"]
    assert all("no configure " not in command and SIBLING not in command for command in deleted["commands"])
    assert call_module(monkeypatch, family, data, "deleted", running="")["commands"] == []
    if family == "equipment_onts":
        assert deleted["commands"] == [
            "configure equipment ont interface %s admin-state down" % ONT,
            "configure equipment ont slot %s/1 admin-state down" % ONT,
            "configure equipment ont no slot %s/1" % ONT,
            "configure equipment ont no interface %s" % ONT,
        ]
    elif family == "ethernet_onts":
        assert deleted["commands"] == ["configure ethernet ont %s no cust-info no admin-state" % UNI]
        assert any("ont.auto_detect has no standalone removal form" in warning for warning in deleted["warnings"])
    elif family == "interfaces":
        assert set(deleted["commands"]) == {
            "configure interface port ont:%s no admin-up no link-updown-trap" % ONT,
            "configure interface port uni:%s no admin-up no user" % UNI,
            # Detail's severity no-value is already unset, not a reset to send.
            "configure interface port vlan-port:%s:10 no admin-up" % UNI,
        }
    elif family == "bridges":
        assert deleted["commands"] == ["configure bridge no port %s" % UNI]
    elif family == "ntp_onts":
        assert deleted["commands"] == ["configure ntp no ont %s" % ONT]
    elif family == "qos_interfaces":
        commands = deleted["commands"]
        # a UNI with queues keeps its scheduler node (the device refuses to remove it)
        assert "configure qos interface %s no scheduler-node" % UNI not in commands
        assert "configure qos interface %s upstream-queue 0 no weight" % UNI in commands
        assert "configure qos interface %s upstream-queue 0 no bandwidth-profile" % UNI in commands
        assert "configure qos interface %s ds-rem-queue 0 no priority" % UNI in commands
        assert all(" no " in command for command in commands)
        assert not any(" oper-" in command or " queue " in command for command in commands)


def test_bridge_creation_bootstraps_pvid_before_service_vlans(monkeypatch):
    data = selected(call_module(monkeypatch, "bridges")["gathered"])
    copied = copy.deepcopy(data)
    copied["port"][0]["port"] = TARGET + "/1/1"
    commands = call_module(monkeypatch, "bridges", copied, "merged", running="")["commands"]
    prefix = "configure bridge port %s/1/1" % TARGET
    assert commands.index(prefix + " vlan-id 99") < commands.index(prefix + " pvid 99")
    service = prefix + " vlan-id 10 tag single-tagged l2fwder-vlan 710 vlan-scope local"
    assert commands.index(prefix + " pvid 99") < commands.index(service)


@pytest.mark.parametrize("family", CONFIGS)
def test_copied_full_entry_commands_round_trip_and_merge_idempotently(monkeypatch, family):
    data = selected(call_module(monkeypatch, family)["gathered"])
    copied = json.loads(json.dumps(data).replace(ONT, TARGET))
    created = call_module(monkeypatch, family, copied, "merged", running="")
    assert created["commands"]
    running = "\n".join(created["commands"])
    assert call_module(monkeypatch, family, copied, "merged", running)["commands"] == []
    assert not any("plain:******" in command for command in created["commands"])


def test_qos_partial_delete_never_sets_values_or_touches_queue_siblings(monkeypatch):
    result = call_module(monkeypatch, "qos_interfaces", [{
        "name": UNI, "upstream_queue": [{"id": 0, "weight": 5}],
    }], "deleted")
    assert result["commands"] == ["configure qos interface %s upstream-queue 0 no weight" % UNI]
    # An identity at the nested level removes every removable setting of that queue.
    result = call_module(monkeypatch, "qos_interfaces", [{
        "name": UNI, "upstream_queue": [{"id": 0}],
    }], "deleted")
    assert all("upstream-queue 0 no " in command for command in result["commands"])
    assert len(result["commands"]) == 3


def test_qos_identity_deletion_clears_removable_fields(monkeypatch):
    result = call_module(monkeypatch, "qos_interfaces", [{"name": UNI}], "deleted")
    assert "configure qos interface %s no scheduler-node" % UNI not in result["commands"]
    assert "configure qos interface %s upstream-queue 1 no weight" % UNI in result["commands"]
    assert all(" no " in command for command in result["commands"])


def test_masked_password_is_not_copied_but_an_explicit_password_is_rendered(monkeypatch):
    data = selected(call_module(monkeypatch, "equipment_onts")["gathered"])
    entry = data["interfaces"][0]
    entry["ont_idx"] = TARGET
    data.pop("slots")
    result = call_module(monkeypatch, "equipment_onts", data, "merged", running="")
    assert all("log-auth-pwd" not in command for command in result["commands"])
    entry["log_auth_pwd"] = "plain:synthetic-example"
    result = call_module(monkeypatch, "equipment_onts", data, "merged", running="")
    assert any("log-auth-pwd plain:synthetic-example" in command for command in result["commands"])


def test_ntp_full_entry_and_partial_delete(monkeypatch):
    running = CONFIGS["ntp_onts"] + " client-state on config-mode manual server1-ip-addr 192.0.2.1"
    data = selected(call_module(monkeypatch, "ntp_onts", running=running)["gathered"])
    assert call_module(monkeypatch, "ntp_onts", data, "deleted", running)["commands"] == ["configure ntp no ont %s" % ONT]
    result = call_module(monkeypatch, "ntp_onts", [{"ont_id": ONT, "client_state": "on"}], "deleted", running)
    assert result["commands"] == ["configure ntp ont %s no client-state" % ONT]


def test_ntp_bare_object_is_created(monkeypatch):
    assert call_module(monkeypatch, "ntp_onts", [{"ont_id": TARGET}], "merged", running="")["commands"] == [
        "configure ntp ont %s" % TARGET,
    ]


def test_ntp_masked_key_is_not_copied(monkeypatch):
    result = call_module(monkeypatch, "ntp_onts", [{"ont_id": TARGET, "key": "plain:******"}], "merged", running="")
    assert result["commands"] == ["configure ntp ont %s" % TARGET]
    result = call_module(monkeypatch, "ntp_onts", [{"ont_id": TARGET, "key": "synthetic-example"}], "merged", running="")
    assert "configure ntp ont %s key synthetic-example" % TARGET in result["commands"]


def test_ntp_compact_negated_numeric_attribute_is_parseable(monkeypatch):
    data = call_module(monkeypatch, "ntp_onts", running="configure ntp ont %s no key-identifier client-state on" % ONT)["gathered"]
    assert data[0]["client_state"] == "on"
    assert "key_identifier" not in data[0]


def test_bridge_still_rejects_a_missing_pvid_vlan(monkeypatch):
    with pytest.raises(AssertionError, match="requires VLAN 99/PVID"):
        call_module(monkeypatch, "bridges", {"port": [{
            "port": UNI, "pvid": 99,
            "vlan_id": [{"id": "10", "tag": "single-tagged", "l2fwder_vlan": "710"}],
        }]}, "merged", running="")


def test_bridge_partial_delete_removes_named_fields_and_vlan_not_siblings(monkeypatch):
    result = call_module(monkeypatch, "bridges", {"port": [{
        "port": UNI, "max_unicast_mac": 5, "vlan_id": [{"id": "10"}],
    }]}, "deleted")
    assert result["commands"] == [
        "configure bridge port %s no max-unicast-mac" % UNI,
        "configure bridge port %s no vlan-id 10" % UNI,
    ]


@pytest.mark.parametrize("alias", ["max-committed-mac", "max_committed_mac", "max-commited-mac", "max_comitted_mac"])
def test_bridge_committed_mac_aliases_round_trip(monkeypatch, alias):
    running = "configure bridge port %s max-committed-mac 9" % UNI
    data = selected(call_module(monkeypatch, "bridges", running=running)["gathered"])
    assert data["port"][0]["max_committed_mac"] == 9
    assert call_module(monkeypatch, "bridges", data, "merged", running)["commands"] == []
    result = call_module(monkeypatch, "bridges", {"port": [{"port": UNI, alias: 10}]}, "merged", running)
    assert result["commands"] == ["configure bridge port %s max-committed-mac 10" % UNI]


def test_qos_derived_oper_values_are_parsed_but_never_rendered(monkeypatch):
    # Live DS-LIN-TEST-01: "Error: field oper-weight_ : instance can not be modified".
    data = selected(call_module(monkeypatch, "qos_interfaces")["gathered"])
    assert data[0]["oper_weight"] == 50 and data[0]["queue"][0]["oper_weight"] == 34
    copied = json.loads(json.dumps(data).replace(ONT, TARGET))
    commands = call_module(monkeypatch, "qos_interfaces", copied, "merged", running="")["commands"]
    assert commands and not any("oper-" in command for command in commands)
    deleted = call_module(monkeypatch, "qos_interfaces", data, "deleted")
    assert not any("oper-" in command for command in deleted["commands"])
    assert not any("oper_weight" in warning or "oper_rate" in warning for warning in deleted["warnings"])


def test_qos_scoped_reply_with_foreign_lines_is_parsed(monkeypatch):
    running = "\n".join([
        "info configure qos interface %s flat" % UNI,
        CONFIGS["qos_interfaces"],
        "DS-SANITIZED-ISAM:user>#",
    ])
    data = call_module(monkeypatch, "qos_interfaces", state="parsed", config=None, running=running)
    assert data["parsed"]


def test_bridge_detail_defaults_do_not_prevent_removing_a_full_port(monkeypatch):
    # A scoped "flat detail" read reports defaults (prior_* false, ...) a gathered
    # full-family read does not contain; naming every VLAN still means the whole port.
    detail = CONFIGS["bridges"] + "\n" + "configure bridge port %s no mac-learn-off no prior-best-effort" % UNI
    gathered = selected(call_module(monkeypatch, "bridges")["gathered"])
    assert call_module(monkeypatch, "bridges", gathered, "deleted", running=detail)["commands"] == [
        "configure bridge no port %s" % UNI,
    ]
