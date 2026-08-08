# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils


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
    "multicast": ("configure igmp ", "configure mcast-control "),
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

    if collisions:
        details = ", ".join("%s (%s, %s)" % collision for collision in collisions)
        raise ValueError("resource config prefix collision: %s" % details)

    return True


validate_resource_config_ownership()
def select_resource_config(config, resource):
    """Select flat configure lines belonging to one resource family."""
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
