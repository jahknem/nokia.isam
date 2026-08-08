from textwrap import dedent

from anytree import Node

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts import facts_base
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.facts.facts import FactsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import FACT_RESOURCE_SUBSETS
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch


def _reference_count_spaces(line):
    spaces = 0
    for char in line:
        if char == " ":
            spaces += 1
        else:
            break
    return spaces


def _reference_parse_config_to_tree(config):
    if not config:
        return None
    last_spaces = 0
    root = None
    parent_node = None
    for line in config.splitlines():

        if line.startswith("echo") or line.startswith("#"):
            continue

        if parent_node is None:
            root = Node(line.split("#", 1)[0].strip())
            parent_node = root
            prev_node = root
        elif "exit" in line:
            if _reference_count_spaces(line) < last_spaces:
                parent_node = parent_node.parent
            else:
                continue
        elif _reference_count_spaces(line) > last_spaces:
            parent_node = prev_node
            prev_node = Node(line.split("#", 1)[0].strip(), parent=prev_node)
        else:
            prev_node = Node(line.split("#", 1)[0].strip(), parent=parent_node)

        last_spaces = _reference_count_spaces(line)
    return root


def _reference_flatten_config(config):
    if not config:
        return None
    flat_config = []
    root = _reference_parse_config_to_tree(config)
    for leave in root.leaves:
        line = []
        for node in leave.path:
            line.append(node.name)
        flat_config.append(" ".join(line))
    return flat_config


def test_unwrap_response():
    assert facts_base.unwrap_response(("payload", "metadata")) == "payload"
    assert facts_base.unwrap_response("payload") == "payload"
    assert facts_base.unwrap_response(None) is None


def test_count_indent():
    assert facts_base.count_indent("x") == 0
    assert facts_base.count_indent("  x") == 2
    assert facts_base.count_indent("    x") == 4


def test_flatten_indented_tree_matches_ethernet_line_reference():
    config = dedent(
        """\
        configure ethernet
        # comment is skipped
        echo "ethernet"
        line 1/1/8/1
          port-type uni # inline comment is stripped
          mau 1
            type 1000basebx10d
            power up
          exit
          admin-up
        exit
        """
    )
    expected = [
        "configure ethernet line 1/1/8/1 port-type uni",
        "configure ethernet line 1/1/8/1 mau 1 type 1000basebx10d",
        "configure ethernet line 1/1/8/1 mau 1 power up",
        "configure ethernet line 1/1/8/1 admin-up",
    ]

    assert facts_base.flatten_indented_tree(config) == expected
    assert facts_base.flatten_indented_tree(config) == _reference_flatten_config(config)


def test_strip_noise_lines():
    config = dedent(
        """\
        echo "system"
        # comment

        configure system id 1 # inline comment
          configure system sntp enable
        configure dhcp-server start-addr 192.0.2.1
        """
    )

    assert facts_base.strip_noise_lines(config, "configure system ") == [
        "configure system id 1",
        "configure system sntp enable",
    ]


def test_validate_config_safe_smoke():
    argument_spec = {"config": {"type": "dict"}}
    data = {"config": {}}

    assert facts_base.validate_config_safe(argument_spec, data) == utils.validate_config(argument_spec, data)


def test_validate_config_safe_type_error_fallback():
    calls = []
    data = {"config": {"name": "node"}}

    def fake_validate_config(argument_spec, validate_data, redact=False):
        calls.append(redact)
        if redact:
            raise TypeError("redact is unsupported")
        return validate_data

    with patch.object(facts_base.utils, "validate_config", side_effect=fake_validate_config):
        assert facts_base.validate_config_safe({}, data) == data

    assert calls == [True, False]


def test_select_resource_config_filters_shared_flat_configuration():
    config = "\n".join(
        [
            "configure equipment shelf 1/1 planned-type nfxs-b",
            "configure equipment ont interface 1/1/5/1/100 sernum TMBB:00000000",
            "configure equipment replan enable",
            "configure pon interface 1/1/5/1 admin-state up",
        ]
    )

    assert facts_base.select_resource_config(config, "isam_equipment") == (
        "configure equipment shelf 1/1 planned-type nfxs-b"
    )
    assert facts_base.select_resource_config(config, "pon_interfaces") == (
        "configure pon interface 1/1/5/1 admin-state up"
    )


def test_resource_config_ownership_rejects_duplicate_prefixes():
    prefixes = {"one": ("configure test ",), "two": ("configure test ",)}

    try:
        facts_base.validate_resource_config_ownership(prefixes, {})
    except ValueError as exc:
        assert "collision" in str(exc)
    else:
        raise AssertionError("duplicate resource prefixes were accepted")


def test_multicast_command_families_have_separate_owners():
    assert facts_base.select_resource_config(
        "configure igmp mcast-svc-context default\nconfigure mcast-control admin-state",
        "igmp",
    ) == "configure igmp mcast-svc-context default"
    assert facts_base.select_resource_config(
        "configure igmp mcast-svc-context default\nconfigure mcast-control admin-state",
        "mcast_control",
    ) == "configure mcast-control admin-state"


def test_dhcp_server_alias_uses_one_command_owner():
    config = "configure dhcp-server start-addr 192.0.2.10\nconfigure interface port 1/1/1"
    assert facts_base.select_resource_config(config, "dhcp_server") == "configure dhcp-server start-addr 192.0.2.10"
    assert facts_base.select_resource_config(config, "isam_dhcp_server") == "configure dhcp-server start-addr 192.0.2.10"


def test_facts_choices_are_registered_resources():
    assert set(FactsArgs.choices) - {"all"} <= set(FACT_RESOURCE_SUBSETS)
