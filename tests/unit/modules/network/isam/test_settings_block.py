"""Compatibility contract for the settings-block wrappers over the attribute core."""
import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    SettingsBlockTemplate,
    make_parsers,
    parse_clauses,
    settings_commands,
)


ATTRS = (("timer", "timer", "int", 120), ("mode", "mode", "str", "disable"))


class DemoTemplate(SettingsBlockTemplate):
    NODE = "demo"
    ATTRS = ATTRS
    PARSERS = make_parsers("demo", NODE, ATTRS)


@pytest.mark.parametrize("state", ["merged", "replaced", "overridden", "rendered"])
def test_explicit_default_resets_only_a_nondefault_value(state):
    assert DemoTemplate.commands(state, {"timer": 120}, {"timer": 60}) == ["configure demo no timer"]
    assert DemoTemplate.commands(state, {"timer": 120}, {}) == []
    assert DemoTemplate.commands(state, {"timer": 120}, {"timer": 120}) == []


@pytest.mark.parametrize("state", ["replaced", "overridden", "deleted"])
def test_reset_commands_stay_separate_and_in_table_order(state):
    assert DemoTemplate.commands(state, {}, {"timer": 60, "mode": "enable"}) == [
        "configure demo no timer", "configure demo no mode"]
    assert DemoTemplate.commands(state, {}, {"timer": 120, "mode": "disable"}) == []


def test_merged_and_legacy_rendered_keep_omitted_values():
    for state in ("merged", "rendered"):
        assert DemoTemplate.commands(state, {"timer": 60}, {"mode": "enable"}) == ["configure demo timer 60"]
        assert DemoTemplate.commands(state, {}, {"timer": 60}) == []


def test_deleted_ignores_want_and_keeps_the_render_callback_contract():
    assert settings_commands("deleted", {"timer": 999}, {"timer": 60}, ATTRS,
                             lambda option, value: (option, value)) == [("timer", None)]


def test_parse_clauses_types_values_and_drops_defaults():
    assert parse_clauses("timer 60 mode enable", ATTRS) == {"timer": 60, "mode": "enable"}
    assert parse_clauses("timer 120 no mode", ATTRS) == {}
    assert parse_clauses("timer mode enable", ATTRS) == {"mode": "enable"}


def test_parse_accepts_optional_configure_and_later_default_clears_value():
    template = DemoTemplate(lines=[
        "configure demo timer 60 mode enable",
        "demo no timer",
        "configure demo interface timer 999 mode disable",
    ])
    assert template.parse() == {"mode": "enable"}
