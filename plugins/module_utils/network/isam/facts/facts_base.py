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
    "isam_dhcp_relay": ("configure dhcp-relay ",),
    "equipment_onts": ("configure equipment ont ",),
    "equipment_replan": ("configure equipment replan ",),
    "ethernet_line": ("configure ethernet line ",),
    "ethernet_onts": ("configure ethernet ont ",),
    "generic_pon": ("configure generic-pon ",),
    "interface_alarms": ("configure interface alarm ",),
    "interface_cages": ("configure interface cage ",),
    "interfaces": ("configure interface port ",),
    "iphost": ("configure iphost",),
    "isam_arp_relay": ("configure arp-relay ",),
    "isam_cfm": ("configure cfm ",),
    "efm_oam_interface": ("configure efm-oam interface ",),
    "isam_ipv6_antispoofing_slot": ("configure ipv6-antispoofing slot ",),
    "isam_dist_service": ("configure dist-service ",),
    "l2cp": ("configure l2cp ",),
    "l2cp_session": ("configure l2cp session ",),
    "l2cp_user_port": ("configure l2cp user-port ",),
    "linetest": ("configure linetest ",),
    "ngpon2_channel_groups": ("configure channel-group ",),
    "epon_interfaces": ("configure epon interface ",),
    "channel_pair_pm": ("configure channel-pair interface ",),
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
    "qos_tca": ("configure qos tca ",),
    "software_mngt": ("configure software-mngt ",),
    "system": ("configure system ",),
    "isam_system_security": ("configure system security ",),
    "xdsl_inm": ("configure xdsl imp-noise-sensor ",),
    "xdsl_onts": ("configure xdsl ont interface ",),
    "xdsl_system": ("configure xdsl system ",),
    "l2uni_onts": ("configure l2uni ont ",),
    "uni_onts": ("configure uni ont ",),
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
    "system": (
        "configure system security ",
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


def get_scoped_config(module, connection, config, fallback_command, commands, safe_states=None):
    """Read only explicitly addressed resource identities when it is safe.

    Resource modules can compare merged/replaced/explicitly deleted entries
    without discovering unrelated family members.  Overridden and unqualified
    deletion still require the complete family to identify entries to remove.
    """
    if module is None:
        return connection.get(fallback_command)
    state = module.params.get("state", "merged")
    # gathered: config selects the instances to read (targeted gathering, targeted.py).
    safe_states = safe_states or ("merged", "replaced", "deleted", "gathered")
    if not commands or state not in safe_states:
        return connection.get(fallback_command)
    scoped_results = []
    for command in commands:
        try:
            response = connection.get(command)
        except Exception as exc:  # connection plugins surface device errors here
            normalized_error = str(exc).lower()
            if (
                "instance does not exist" in normalized_error
                or "specified instance does not exist" in normalized_error
                or "lower-interface does not exist" in normalized_error
            ):
                continue
            raise
        normalized_response = response.lower()
        if (
            "instance does not exist" in normalized_response
            or "specified instance does not exist" in normalized_response
            or "lower-interface does not exist" in normalized_response
        ):
            continue
        scoped_results.append(_targeted_reply(command, response))
    return "\n".join(scoped_results)


def _targeted_reply(command, response):
    """Clean a single-instance reply: drop echoed command text and header noise.

    An instance without configured attributes answers with only the header
    ('#---', 'echo ...'), exactly like a non-existing one; neither is returned.
    Echoed command text (the terminal wraps it mid-word) must not reach parsers.
    """
    if not command.startswith("info configure ") or " flat" not in command:
        return response
    path = command[len("info "):]
    path = re.sub(r"( detail)? flat( detail)?$", "", path)
    words = set(path.split())
    kept = []
    for line in response.splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped or stripped.startswith("echo"):
            continue
        if line.startswith("configure ") or line[:1].isspace():
            kept.append(line)
        elif not set(stripped.split()) - words:
            continue  # echoed command text, possibly wrapped by the terminal
        else:
            kept.append(line)
    if not kept:
        # The device answers an unset instance and a non-existing one alike with only
        # the header; they cannot be told apart, so neither is returned.
        return ""
    cleaned = "\n".join(kept)
    # Unchanged replies keep their exact form (parsers and tests rely on it).
    return response if cleaned == response.strip("\n") else cleaned + "\n"


def _section_items(config, section):
    """Entries of one instance list in config ("config": config itself, "a.b": nested)."""
    if section == "config":
        return config if isinstance(config, list) else []
    value = config
    for key in section.split("."):
        value = value.get(key) if isinstance(value, dict) else None
    return value if isinstance(value, list) else []


def requested_identities(module, resource, section="config"):
    """Identity values named in the module's config for one list of a resource.

    Follows TARGETED_GATHER (targeted.py): one value per entry, or a tuple of values
    for a composite identity. Empty when there is no module (isam_facts, parsing) or
    no config: then the whole resource is read.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    field = (TARGETED_GATHER.get(resource) or {}).get(section)
    params = getattr(module, "params", None) or {}
    config = params.get("config")
    if not field or not config:
        return []
    fields = [field] if isinstance(field, str) else list(field)
    found = []
    for item in _section_items(config, section):
        if not isinstance(item, dict):
            continue
        values = tuple(item.get(name) for name in fields)
        if all(value not in (None, "") for value in values):
            found.append(values[0] if isinstance(field, str) else values)
    return found


def targeted_commands(module, resource, formats):
    """Read commands for the instances named in config (targeted gathering).

    formats: instance list -> command format with one %s per identity field, or a
    callable returning the commands for one identity. Empty when config names no
    instance: then the caller reads the whole resource.
    """
    commands = []
    for section, form in formats.items():
        for identity in requested_identities(module, resource, section):
            if callable(form):
                commands.extend(form(identity))
            else:
                commands.append(form % (identity if isinstance(identity, tuple) else (identity,)))
    return commands


def get_targeted_config(module, connection, resource, fallback, formats, write_states=False):
    """The whole resource, or only the instances named in config with state gathered.

    fallback: command for the whole resource, or a callable(connection) reading it.
    write_states: also compare merged/replaced/deleted against only the named
    instances (only for resources made of instance lists, where that is exact).
    """
    states = ("merged", "replaced", "deleted", "gathered") if write_states else ("gathered",)
    commands = targeted_commands(module, resource, formats) if module is not None else []
    state = module.params.get("state", "merged") if module is not None else None
    if commands and state in states:
        return get_scoped_config(module, connection, None, None, commands, safe_states=states)
    return fallback(connection) if callable(fallback) else connection.get(fallback)


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
