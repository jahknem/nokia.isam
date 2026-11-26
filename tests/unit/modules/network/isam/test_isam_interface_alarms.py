import os

import yaml

from ansible_collections.nokia.isam.plugins.modules import isam_interface_alarms
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_alarms.interface_alarms import (
    Interface_alarmsFacts,
)


class _Module(object):
    no_log_values = set()
    params = {"state": "parsed"}


def test_isam_interface_alarms_default_severity_is_parsed():
    """The catch-all name parser used to swallow 'default-severity' lines (parse() stops at the first match)."""
    facts = {"ansible_network_resources": {}}
    data = "configure interface alarm ont default-severity major\nconfigure interface alarm epon no default-severity\n"
    Interface_alarmsFacts(module=_Module()).populate_facts(None, facts, data=(data, ""))
    assert sorted(facts["ansible_network_resources"]["interface_alarms"], key=lambda item: item["name"]) == [
        {"name": "epon"}, {"name": "ont", "default_severity": "major"},
    ]


def test_isam_interface_alarms_description_is_a_list():
    doc = yaml.safe_load(isam_interface_alarms.DOCUMENTATION)
    assert isinstance(doc["description"], list)
    assert not any(line.lstrip().startswith("- ") for line in doc["description"])
    assert doc["description"][0].startswith("Manages C(configure interface alarm)")


def test_isam_interface_alarms_has_no_dead_module_description():
    assert not hasattr(isam_interface_alarms, "MODULE_DESCRIPTION")


def test_isam_interface_alarms_capture_lines_are_parsed():
    """Every 'configure interface alarm' line of the lab capture is gathered, nothing is dropped."""
    from . import lab_captures

    lines = [line.rstrip() for line in lab_captures.configured().splitlines() if line.startswith("configure interface alarm ")]
    assert lines
    facts = {"ansible_network_resources": {}}
    Interface_alarmsFacts(module=_Module()).populate_facts(None, facts, data="\n".join(lines))
    expected = [{"name": line.split()[3], "default_severity": line.split()[5]} for line in lines]
    key = lambda item: item["name"]  # noqa: E731
    assert sorted(facts["ansible_network_resources"]["interface_alarms"], key=key) == sorted(expected, key=key)


def test_device_header_form_is_parsed():
    """Real reply of 'info configure interface alarm': header + 'alarm <name>' blocks."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.interface_alarms.interface_alarms import Interface_alarmsFacts

    text = (
        "configure interface\n"
        "#-------------------------------------------------------------------------------\n"
        'echo "interface"\n'
        "#-------------------------------------------------------------------------------\n"
        "alarm epon\n"
        "  default-severity indeterminate\n"
        "exit\n"
        "alarm eont\n"
        "  default-severity critical\n"
        "exit\n"
    )
    facts = Interface_alarmsFacts.__new__(Interface_alarmsFacts)
    assert facts._flatten_config(text) == [
        "configure interface alarm epon default-severity indeterminate",
        "configure interface alarm eont default-severity critical",
    ]
