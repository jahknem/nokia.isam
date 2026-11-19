"""The shared attribute-table core (module_utils/network/isam/attribute_table.py).

A synthetic table covers every feature; the families using it pin their device grammar
in their own tests."""
import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import (
    Attr,
    AttributeTable,
    Node,
    change,
    parse_clauses,
    quote_value,
)

TABLE = AttributeTable("configure demo", (
    Node((), "", (Attr("threshold", "threshold", "int", removable=False),)),
    Node("profile", "profile", (
        Attr("mode", "mode", "str", "auto", ["auto", "manual"]),
        Attr("timer", "timer", "int", 30),
        Attr("label", "label", "str"),
        Attr("enable", "enable", "flag"),
        Attr("domain", "domain", "str", removable=False),
    ), identity="name", mandatory=("domain",)),
    Node("stats", "stats", (
        Attr("cdr", "cdr", "str", "disable", ["disable", "enable"]),
        Attr("per_line", "per-line", "flag", node="stats config"),
    )),
    Node(("util",), "util", (Attr("collect", "collect", "str", "none"),)),
    Node(("util", "limits"), "util limits", (Attr("hi", "hi", "str", "disabled"),)),
    Node("db", "db", (
        Attr("version", "version", "str", removable=False, form="solo"),
        Attr("interval", "auto-intvl", "int", 24),
        Attr("admin", "admin-state", "flag", form="solo"),
    )),
    Node("mode", "mode", (Attr("value", "mode", "str", removable=False, form="scalar"),)),
))

DEVICE = """\
configure demo threshold 0
configure demo profile p1 mode manual no timer label "a b" enable domain example.org
configure demo profile p2 no mode timer 30 no enable domain x
configure demo stats no cdr
configure demo stats config per-line
configure demo util no collect
configure demo util limits hi 80
configure demo db no auto-intvl
configure demo mode upgrade
configure demo profile-list unrelated mode manual
configure demo stats unknown-word cdr enable
"""


def test_parse_raw():
    assert TABLE.parse(DEVICE) == {
        "threshold": 0,
        "profile": [
            {"name": "p1", "mode": "manual", "timer": None, "label": "a b", "enable": True, "domain": "example.org"},
            {"name": "p2", "mode": None, "timer": 30, "enable": False, "domain": "x"},
        ],
        "stats": {"cdr": None, "per_line": True},
        "util": {"collect": None, "limits": {"hi": "80"}},
        "db": {"interval": None},
        "mode": {"value": "upgrade"},
    }


def test_parse_keeps_sibling_nodes_out():
    # the first clause must be a keyword of the node; a later known keyword is not enough
    assert TABLE.parse("configure demo stats unknown-word cdr enable\n") == {}
    assert TABLE.parse("configure demo profile-list x mode manual\n") == {}


def test_parse_drops_comments_outside_quotes():
    assert TABLE.parse('configure demo profile p1 label "a # b" # set by hand\n') == {
        "profile": [{"name": "p1", "label": "a # b"}]}
    assert TABLE.parse('configure demo profile p1 label a#b\n') == {"profile": [{"name": "p1", "label": "a#b"}]}
    assert TABLE.parse('configure demo profile p1 label "#"\n') == {"profile": [{"name": "p1", "label": "#"}]}


def test_parse_bare_instance():
    assert TABLE.parse("configure demo profile p3\n") == {"profile": [{"name": "p3"}]}


def test_without_defaults_keeps_flags_and_drops_empty_sections():
    assert TABLE.without_defaults(TABLE.parse(DEVICE)) == {
        "threshold": 0,
        "profile": [
            {"name": "p1", "mode": "manual", "label": "a b", "enable": True, "domain": "example.org"},
            {"name": "p2", "enable": False, "domain": "x"},
        ],
        "stats": {"per_line": True},
        "util": {"limits": {"hi": "80"}},
        "mode": {"value": "upgrade"},
    }


def test_parse_clauses_does_not_take_a_keyword_as_value():
    attrs = (Attr("a", "a", "str"), Attr("b", "b", "int"))
    assert parse_clauses(["a", "b", "5"], attrs) == {"b": 5}
    assert parse_clauses(["a", "no", "b"], attrs) == {"b": None}
    assert parse_clauses(["b", "soon"], attrs) == {"b": "soon"}  # a non-numeric int stays a string


@pytest.mark.parametrize("state,want,have,tokens", [
    # merged: only what differs; a default the device already has sends nothing
    ("merged", "manual", None, ["mode", "manual"]),
    ("merged", "manual", "manual", None),
    ("merged", "auto", None, None),
    ("merged", "auto", "manual", ["no", "mode"]),   # back to the default: reset
    ("merged", None, "manual", None),
    # replaced/overridden: an omitted removable attribute is reset
    ("replaced", None, "manual", ["no", "mode"]),
    ("overridden", None, None, None),
    # rendered: what is given, defaults included
    ("rendered", "auto", None, ["mode", "auto"]),
    ("rendered", None, None, None),
])
def test_change_value(state, want, have, tokens):
    assert change(Attr("mode", "mode", "str", "auto"), want, have, state) == tokens


def test_change_flag_and_unremovable():
    flag = Attr("enable", "enable", "flag")
    assert change(flag, True, None, "merged") == ["enable"]
    assert change(flag, False, True, "merged") == ["no", "enable"]
    assert change(flag, False, None, "merged") is None
    assert change(flag, False, None, "rendered") == ["no", "enable"]
    fixed = Attr("domain", "domain", "str", removable=False)
    assert change(fixed, None, "x", "replaced") is None
    assert change(fixed, "y", "x", "merged") == ["domain", "y"]


def test_diff_commands_packs_per_path_then_solo_and_scalar():
    stats = TABLE.node("stats")
    assert TABLE.diff_commands(stats, None, {"cdr": "enable", "per_line": True}, {}, "merged") == [
        "configure demo stats cdr enable", "configure demo stats config per-line"]
    db = TABLE.node("db")
    assert TABLE.diff_commands(db, None, {"version": "R6", "interval": 48, "admin": True}, {}, "merged") == [
        "configure demo db auto-intvl 48", "configure demo db version R6", "configure demo db admin-state"]
    assert TABLE.diff_commands(TABLE.node("mode"), None, {"value": "lt-by-lt"}, {}, "merged") == [
        "configure demo mode lt-by-lt"]
    root = TABLE.node(())
    assert TABLE.diff_commands(root, None, {"threshold": 5}, {"threshold": 0}, "merged") == [
        "configure demo threshold 5"]


def test_instance_commands_quote_names_and_values():
    profile = TABLE.node("profile")
    assert TABLE.diff_commands(profile, "p 1", {"label": "a b"}, {}, "merged") == [
        'configure demo profile "p 1" label "a b"']
    assert TABLE.removal_command(profile, "p1") == "configure demo no profile p1"
    assert TABLE.creation_command(profile, "p1") == "configure demo profile p1"
    assert quote_value("#") == '"#"' and quote_value("") == '""' and quote_value(5) == "5"


def test_argument_spec_is_nested_by_path():
    spec = TABLE.argument_spec()
    assert spec["threshold"] == {"type": "int"}
    assert spec["profile"]["type"] == "list" and spec["profile"]["elements"] == "dict"
    assert spec["profile"]["options"]["name"] == {"type": "str", "required": True}
    assert spec["profile"]["options"]["mode"] == {"type": "str", "choices": ["auto", "manual"]}
    assert spec["profile"]["options"]["enable"] == {"type": "bool"}
    assert spec["util"]["options"]["collect"] == {"type": "str"}
    assert spec["util"]["options"]["limits"]["options"]["hi"] == {"type": "str"}


def test_invalid_definitions_are_rejected():
    with pytest.raises(ValueError):
        Attr("x", "x", "bool")
    with pytest.raises(ValueError):
        Node(("a", "b"), "a b", (), identity="name")
    with pytest.raises(ValueError):
        Node("a", "a", (Attr("x", "x", "flag", node="a sub"),), identity="name")
