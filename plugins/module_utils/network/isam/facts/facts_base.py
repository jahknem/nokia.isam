# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from contextlib import contextmanager
import copy
import re

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


RESOURCE_CONFIG_PREFIXES = {
    "alarm": ("configure alarm ",),
    "ani_onts": ("configure ani ont ",),
    "bridges": ("configure bridge ",),
    "dhcp_server": ("configure dhcp-server ",),
    "equipment_onts": ("configure equipment ont ",),
    "equipment_replan": ("configure equipment replan ",),
    "ethernet_line": ("configure ethernet line ",),
    "ethernet_onts": ("configure ethernet ont ",),
    "generic_pon": ("configure generic-pon ",),
    "interface_alarms": ("configure interface alarm ",),
    "interface_cages": ("configure interface cage ",),
    "interfaces": ("configure interface port ",),
    "iphost": ("configure iphost",),
    "isam_equipment": ("configure equipment ",),
    "isam_traps": ("configure trap ",),
    "isam_vlan_global": (
        "configure vlan broadcast-frames ",
        "configure vlan priority-regen ",
        "configure vlan tpid ",
        "configure vlan vmac-address-format ",
    ),
    "li_vlan": ("configure li_vlan ",),
    "link_agg": ("configure link-agg ",),
    "mcast_general": ("configure mcast general ",),
    "igmp": ("configure igmp ",),
    "mcast_control": ("configure mcast-control ",),
    "ntp_onts": ("configure ntp ont ",),
    "pon_interfaces": ("configure pon interface ",),
    "qos_interfaces": ("configure qos interface ",),
    "qos_maps": (
        "configure qos tc-map-dot1p ",
        "configure qos dscp-map-dot1p ",
        "configure qos up-ctrl-pkt ",
        "configure qos dn-ctrl-pkt ",
    ),
    "qos_profiles": ("configure qos profiles ",),
    "software_mngt": ("configure software-mngt ",),
    "system": ("configure system ",),
    "vlans": ("configure vlan id ",),
    "voice_sip": ("configure voice sip ",),
    "xdsl_boards": ("configure xdsl board ", "configure xdsl vp-board "),
    "xdsl_bonding": ("configure xdsl-bonding ",),
    "xdsl_lines": ("configure xdsl line ",),
    "xdsl_profiles": (
        "configure xdsl dpbo-profile ",
        "configure xdsl service-profile ",
        "configure xdsl spectrum-profile ",
        "configure xdsl vce-profile ",
        "configure xdsl vect-profile ",
    ),
    "xstp": ("configure xstp ",),
}

RESOURCE_CONFIG_EXCLUDES = {
    "isam_equipment": (
        "configure equipment ont ",
        "configure equipment replan ",
    ),
}

RESOURCE_ALIASES = {
    "isam_dhcp_server": "dhcp_server",
}

RESOURCE_AGGREGATES = {
    "multicast": ("igmp", "mcast_control"),
}


def validate_resource_config_ownership(resource_prefixes=None, resource_excludes=None):
    """Validate that configured prefixes have one unambiguous owner."""
    prefixes = RESOURCE_CONFIG_PREFIXES if resource_prefixes is None else resource_prefixes
    excludes = RESOURCE_CONFIG_EXCLUDES if resource_excludes is None else resource_excludes
    owners = {}
    collisions = []

    for resource, resource_values in prefixes.items():
        for prefix in resource_values:
            previous = owners.get(prefix)
            if previous and previous != resource:
                collisions.append((prefix, previous, resource))
            owners[prefix] = resource

    for resource, resource_values in excludes.items():
        if resource not in prefixes:
            raise ValueError("resource exclusion is registered for unknown resource %s" % resource)
        for prefix in resource_values:
            if not any(prefix.startswith(parent) or parent.startswith(prefix) for parent in prefixes[resource]):
                raise ValueError("resource exclusion %s does not belong to %s" % (prefix, resource))

    if resource_prefixes is None:
        for resource, members in RESOURCE_AGGREGATES.items():
            if resource in prefixes:
                raise ValueError("aggregate resource must not own command prefixes: %s" % resource)
            if any(member not in prefixes for member in members):
                raise ValueError("aggregate resource %s references an unknown member" % resource)

    if collisions:
        details = ", ".join("%s (%s, %s)" % collision for collision in collisions)
        raise ValueError("resource config prefix collision: %s" % details)

    return True


validate_resource_config_ownership()
def select_resource_config(config, resource):
    """Select flat configure lines belonging to one resource family."""
    resource = RESOURCE_ALIASES.get(resource, resource)
    if resource in RESOURCE_AGGREGATES:
        return "\n".join(
            selected
            for member in RESOURCE_AGGREGATES[resource]
            for selected in [select_resource_config(config, member)]
            if selected
        )
    config = unwrap_response(config)
    if isinstance(config, (list, tuple)):
        config = "\n".join(str(line) for line in config)
    if not config or resource not in RESOURCE_CONFIG_PREFIXES:
        return config

    prefixes = RESOURCE_CONFIG_PREFIXES[resource]
    excludes = RESOURCE_CONFIG_EXCLUDES.get(resource, ())
    selected = []
    for raw_line in str(config).splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("echo"):
            continue
        if any(line.startswith(prefix) for prefix in prefixes) and not any(
            line.startswith(prefix) for prefix in excludes
        ):
            selected.append(line)
    return "\n".join(selected)


@contextmanager
def track_network_template_matches():
    """Track lines accepted by shared and custom NetworkTemplate parsers.

    The common parser exposes parser regexes, but resource templates are also
    allowed to override ``parse``.  For those parsers, compare parses of
    progressively longer input copies after the normal parse has completed.
    A line which changes the result was consumed by the parser.
    """
    class MatchedLines(list):
        observed = False

    matched_lines = MatchedLines()
    original_parse = NetworkTemplate.parse
    original_init = NetworkTemplate.__init__
    templates = []

    def parse(template):
        matched_lines.observed = True
        for line in template._lines:
            if any(re.match(parser["getval"], line) for parser in template._tmplt.PARSERS):
                matched_lines.append(line)
        return original_parse(template)

    def init(template, *args, **kwargs):
        original_init(template, *args, **kwargs)
        templates.append(template)

    NetworkTemplate.parse = parse
    NetworkTemplate.__init__ = init
    try:
        yield matched_lines
    finally:
        for template in templates:
            parser = type(template).parse
            if parser is original_parse or parser is parse:
                continue
            try:
                empty_replay = copy.copy(template)
                empty_replay._lines = []
                previous = parser(empty_replay)
                for index, line in enumerate(template._lines):
                    replay = copy.copy(template)
                    replay._lines = template._lines[: index + 1]
                    current = parser(replay)
                    if current != previous:
                        matched_lines.append(line)
                    previous = current
                matched_lines.observed = True
            except Exception:
                # Tracking must never alter the result or error handling of a
                # resource parser that cannot be safely replayed.
                continue
        NetworkTemplate.__init__ = original_init
        NetworkTemplate.parse = original_parse


def unmatched_resource_config_lines(config, resource, matched_lines):
    """Return owned configure lines not accepted by a resource parser."""
    selected = select_resource_config(config, resource)
    if not selected or not matched_lines:
        return [] if not selected else selected.splitlines()

    return [
        line
        for line in selected.splitlines()
        if not any(
            line == matched
            or line.endswith(" " + matched)
            or matched.endswith(" " + line)
            for matched in matched_lines
        )
    ]


def unwrap_response(data):
    """Return the payload from connection responses that are wrapped in a tuple."""
    if isinstance(data, tuple):
        return data[0]
    if data is None:
        return None
    return data


def count_indent(line):
    """Return the number of leading space characters in a line."""
    return len(line) - len(line.lstrip(" "))


def _parse_config_to_tree(config):
    """Parse indented ISAM configuration into an anytree tree."""
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
            if count_indent(line) < last_spaces:
                parent_node = parent_node.parent
            else:
                continue
        elif count_indent(line) > last_spaces:
            parent_node = prev_node
            prev_node = Node(line.split("#", 1)[0].strip(), parent=prev_node)
        else:
            prev_node = Node(line.split("#", 1)[0].strip(), parent=parent_node)

        last_spaces = count_indent(line)
    return root


def flatten_indented_tree(config):
    """Flatten indented ISAM configuration exactly like ethernet_line facts.

    The implementation intentionally preserves the original tree parsing quirks:
    echo and full-line hash comments are ignored, inline hash comments are
    stripped with ``split('#', 1)[0].strip()``, ``exit`` only adjusts the parent
    when its indentation decreases, and each leaf is rendered as its path joined
    with single spaces.
    """
    if not config:
        return None
    flat_config = []
    root = _parse_config_to_tree(config)
    for leave in root.leaves:
        line = []
        for node in leave.path:
            line.append(node.name)
        flat_config.append(" ".join(line))
    return flat_config


def strip_noise_lines(config, keep_prefix):
    """Strip comments/noise and keep lines whose stripped form starts with a prefix."""
    lines = []
    if not config:
        return lines

    for raw_line in config.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("echo") or stripped.startswith("#"):
            continue
        if stripped.startswith(keep_prefix):
            lines.append(stripped)

    return lines


def validate_config_safe(argument_spec, data):
    """Validate config while supporting netcommon versions with different signatures.

    Existing facts wrappers only pass ``argument_spec`` and ``data`` and retry
    without ``redact`` when older ``utils.validate_config`` implementations raise
    ``TypeError``.  If validation is unavailable (``AttributeError``), the input
    data is returned unchanged.  The signature intentionally omits unused
    template/module parameters so callers can share one minimal helper.
    """
    try:
        return utils.validate_config(argument_spec, data, redact=True)
    except TypeError:
        return utils.validate_config(argument_spec, data)
    except AttributeError:
        return data
