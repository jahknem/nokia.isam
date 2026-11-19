"""System's compatibility adapters over the shared attribute grammar."""
import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import Attr
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.system import (
    ID_ATTRS,
    SETTINGS,
    SETTINGS_LISTS,
    SYSTEM_DEFAULTS,
    parse_settings,
    render_settings,
)


def test_all_system_settings_use_shared_attribute_definitions():
    groups = [attrs for _node, attrs, _other in SETTINGS.values()]
    groups.extend(attrs for _node, _identity, attrs, _other in SETTINGS_LISTS.values())
    assert all(isinstance(attr, Attr) for attrs in groups for attr in attrs)
    assert SYSTEM_DEFAULTS[("id", "system_40gkr4")] == "disable"
    assert SYSTEM_DEFAULTS[("auto_switch", "xdsl_stepup_delay")] == 3600


def test_reserved_keywords_never_become_attribute_values():
    target = {"customer_id": "keep"}
    parse_settings(["customer-id", "name", "example"], ID_ATTRS, target, ("name",))
    assert target == {"customer_id": "keep"}


def test_system_preserves_legacy_default_and_bad_integer_parse_rules():
    target = {"periph_mgnt_vlan": 10, "en_snmp_auth_trap": True}
    parse_settings(["periph-mgnt-vlan", "invalid", "no", "en-snmp-auth-trap"], ID_ATTRS, target)
    assert target == {}
    parse_settings(["periph-mgnt-vlan", "0", "en-snmp-auth-trap"], ID_ATTRS, target)
    assert target == {"periph_mgnt_vlan": 0, "en_snmp_auth_trap": True}


@pytest.mark.parametrize("value", ["plain", "with spaces", "#comment-like", 'embedded"quote', ""])
def test_rendered_string_values_use_shared_quoting(value):
    import shlex

    rendered = render_settings(ID_ATTRS, {"customer_id": value})
    assert len(rendered) == 1
    tokens = shlex.split(rendered[0])
    target = {}
    parse_settings(tokens, ID_ATTRS, target)
    assert target == {"customer_id": value}


def test_system_reset_and_false_flags_keep_their_cli_forms():
    assert render_settings(ID_ATTRS, {"en_snmp_auth_trap": False}) == ["no en-snmp-auth-trap"]
    assert render_settings(ID_ATTRS, {"customer_id": "example"}, reset=True) == ["no customer-id"]
