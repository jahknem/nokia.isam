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
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.cli_safety import check_cli_commands
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read_outcomes import (
    ReadOutcomeCollector,
    error_class,
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
    "pon_global": ("configure pon pwrbrst-mode ", "configure pon no pwrbrst-mode", "configure pon range-mode ", "configure pon no range-mode"),
    "trouble_shooting_pon": ("configure trouble-shooting pon ",),
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
    "l2uni_onts": ("configure l2uni ont ",),
    "uni_onts": ("configure uni ont ",),
    "cwmp_plt": ("configure cwmp plt ",),
    "error": ("configure error ",),
    "nat": ("configure nat ",),
    "pppox_relay_global": ("configure pppox-relay cross-connect global-session ",),
    "xdsl_inm": ("configure xdsl imp-noise-sensor ",),
    "xdsl_onts": ("configure xdsl ont interface ",),
    "xdsl_system": ("configure xdsl system ",),
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


_QUOTED = re.compile(r'"[^"]*"')

# Missing-dependency phrases -> the dependency_gap label recorded in read_outcomes.
# "interface index cannot be calculated": dhcp-relay/arp-relay answer a port that the
# device cannot resolve to an interface this way (live, DS-LIN-TEST-01, commit
# 5ea59f6b). The evidence shows the PORT could not be resolved, not that the relay
# instance on an existing port is absent, so it is a dependency signal: the relay
# instance's existence stays unknown. Write-state reads drop such a reply
# (_is_absent_error) instead of failing on it.
_DEPENDENCY_GAPS = (
    ("lower-interface does not exist", "lower-interface"),
    ("interface index cannot be calculated", "interface-index"),
)


def _device_message_lines(text):
    """The lines of a reply or error text that can carry a device message, lower-cased.

    Configuration content is never a device message: flat configuration lines
    ('configure ...'), indented hierarchical lines, comments and echo lines are skipped,
    and quoted values (descriptions, names) are blanked, so an instance whose description
    reads "instance does not exist" is not mistaken for the device's error. Device errors
    are printed unindented ('Error : instance does not exist'; a raised transport error
    may carry the bare phrase, tests/fixtures/bridges/targeted-absent).
    """
    for raw in str(text or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        lowered = line.lower()
        if raw[:1].isspace() and not lowered.startswith("error"):
            continue
        if lowered.startswith(("configure ", "#", "echo")):
            continue
        yield _QUOTED.sub('""', lowered)


def _device_says(text, phrase):
    return any(phrase in line for line in _device_message_lines(text))


def _is_instance_absent(text):
    """The device says the ADDRESSED instance does not exist -- a confirmed absence of
    that instance."""
    return _device_says(text, "instance does not exist")


def _dependency_gap(text):
    """The dependency_gap label when the device reports a MISSING DEPENDENCY (e.g. a
    lower-interface), else None. The addressed instance's own existence is NOT
    established by this reply: it stays unknown, never confirmed absent."""
    for phrase, label in _DEPENDENCY_GAPS:
        if _device_says(text, phrase):
            return label
    return None


def _is_dependency_absent(text):
    """Whether the device reports a missing dependency (see _dependency_gap)."""
    return _dependency_gap(text) is not None


def _is_absent_error(text):
    """Union of the absence signals, kept for the read control flow (a reply matching
    any is dropped from the read output; write-state reads rely on this). Do not use
    this to label an instance absent: use _is_instance_absent / _dependency_gap."""
    return _is_instance_absent(text) or _is_dependency_absent(text)


def _is_unsupported_node(text):
    """The device rejected the addressed node/selector ("invalid token"). The cause is not
    disambiguated: the firmware may not know the node, or the selector/command may be
    invalid. For a read that means 'nothing configured here' (existence unknown), not a
    failure; a write must still surface it."""
    return _device_says(text, "invalid token")


def _record_absence(outcomes, entries, text, unobservable=False):
    """Record the outcome of an absence reply for every selector a command serves.

    unobservable: the section answers the same whether it is set or not
    (targeted.ABSENCE_POLICY), so even "instance does not exist" proves nothing.
    """
    gap = _dependency_gap(text)
    for section, selector in entries:
        if gap is None and unobservable:
            outcomes.record(section, selector, "ok", "unknown")
        elif gap is None:
            outcomes.record(section, selector, "ok", "confirmed_absent")
        else:
            outcomes.record(section, selector, "ok", "unknown", dependency_gap=gap)


def _failure_message(resource, kind, cls, entries=()):
    """A sanitized failure message: the resource, the selectors and the error class --
    never raw device or transport text (read_outcomes is documented as safe to
    publish, and the module message travels with it)."""
    names = ", ".join(
        "%s %s" % (section, selector) if section else str(selector)
        for section, selector in entries if selector is not None)
    return "%s of %s failed (%s)%s" % (kind, resource, cls, " for " + names if names else "")


def _probe_detail(connection, command, policy=None):
    """Decide a header-only single-instance reply with 'flat detail'.

    Returns (reply, existence). 'flat' prints only values that differ from the
    default, so an instance with defaults only answers like a missing one; 'flat
    detail' prints every existing instance with its defaults (DS-LIN-TEST-01,
    2026-11-27: 67 of 67 default-only instances in 35 sections; every missing one
    answered "instance does not exist" or the header only, docs/targeted-read-contract.md).

    - the instance line in the detail reply: present (the bare path is returned,
      the defaults are not)
    - "instance does not exist": confirmed_absent
    - the header only: confirmed_absent -- unless policy is "silent" (a switch
      without attributes, which prints nothing when present; there only the
      explicit error proves absence, so the header means present) or
      "unobservable" (every read answers the same in both states: unknown)
    - a rejection ("invalid token"): rejected; any other reply: unknown
    """
    if not command.startswith("info configure ") or not command.endswith(" flat") or " detail" in command:
        return "", "unknown"
    bare = command[len("info "):-len(" flat")]
    try:
        response = connection.get(command + " detail")
    except Exception as exc:
        if _is_instance_absent(str(exc)):
            return "", "unknown" if policy == "unobservable" else "confirmed_absent"
        if _is_absent_error(str(exc)):
            return "", "unknown"  # a missing dependency (lower interface): not this instance
        if _is_unsupported_node(str(exc)):
            return "", "rejected"
        raise
    if _is_instance_absent(response):
        return "", "unknown" if policy == "unobservable" else "confirmed_absent"
    if _is_absent_error(response):
        return "", "unknown"
    if _is_unsupported_node(response):
        return "", "rejected"
    for line in response.splitlines():
        line = line.strip()
        if line == bare or line.startswith(bare + " "):
            return bare + "\n", "present"
    if _targeted_reply(command + " detail", response).strip():
        return "", "unknown"  # content, but not this instance's line
    if policy == "silent":
        return bare + "\n", "present"
    if policy == "unobservable":
        return "", "unknown"
    return "", "confirmed_absent"


def _bare_instance(connection, command, silent=False):
    """The bare path of a default-only instance, or "" (see _probe_detail)."""
    reply, existence = _probe_detail(connection, command, "silent" if silent else None)
    return reply if existence == "present" else ""


def get_scoped_config(module, connection, config, fallback_command, commands, safe_states=None,
                      bare_commands=(), silent_bare_commands=(), outcomes=None, selectors=None,
                      require_targeted=False, instance_checks=None, empty_absent_commands=(),
                      unobservable_commands=()):
    """Read only explicitly addressed resource identities when it is safe.

    Resource modules can compare merged/replaced/explicitly deleted entries
    without discovering unrelated family members.  Overridden and unqualified
    deletion still require the complete family to identify entries to remove.

    Gathered single-instance flat reads automatically probe a header-only reply
    with flat detail (_probe_detail). An exact instance path proves presence; the
    header only or "instance does not exist" proves absence; a gathered
    single-instance read that is already 'flat detail' proves absence by its
    header alone (docs/targeted-read-contract.md). Defaults are not copied into
    desired configuration. Shared-node reads with instance_checks retain their
    explicit per-instance semantics.

    bare_commands: the single reads of lists whose whole read shows an instance
    without configured attributes as its bare path; for these an empty reply is
    re-checked with 'flat detail' (see _bare_instance); silent_bare_commands likewise,
    for nodes whose detail read prints nothing either.
    Identical commands are sent once (several identities can share one read).

    outcomes: an optional ReadOutcomeCollector; when given, each read records its
    command/existence outcome (sanitized) for every selector it serves. The returned
    string is unchanged, so existing callers that pass no collector are byte-for-byte
    unaffected.
    selectors: optional {command: [(section, selector), ...]} labeling each command with
    the config sections and instance identities it addresses (one recorded outcome per
    selector; a single (section, selector) tuple is accepted for one selector).
    instance_checks: optional {(section, selector): callable(reply) -> bool} deciding
    the existence of an instance from its command's reply when the reply alone does not
    (a command that reads a whole node for an instance list): present when the check
    holds, else unknown -- never confirmed_absent. A command serving several selectors
    without checks cannot attribute a non-empty reply to any one of them, so they are
    recorded unknown rather than present.
    require_targeted: when True, a targeted read that produces no targeted commands
    raises instead of silently widening to the whole-family fallback read.
    empty_absent_commands: explicit evidence-backed policy for single-instance
    commands whose instances always print a line (mandatory attributes). An
    empty successful reply confirms absence without a detail probe. Never use
    this policy for shared-node commands or default-only instances.
    """
    if module is None:
        return connection.get(fallback_command)
    state = module.params.get("state", "merged")
    # gathered: config selects the instances to read (targeted gathering, targeted.py).
    safe_states = safe_states or ("merged", "replaced", "deleted", "gathered")
    if not commands:
        if require_targeted:
            raise RuntimeError(
                "targeted read requested but no targeted commands could be generated; "
                "refusing to widen to a whole-family read")
        return connection.get(fallback_command)
    if state not in safe_states:
        return connection.get(fallback_command)
    check_cli_commands(commands, "scoped read")
    selectors = selectors or {}
    instance_checks = instance_checks or {}
    resource = getattr(outcomes, "resource", None)
    scoped_results = []
    reading = state == "gathered"
    for command in list(dict.fromkeys(commands)):
        entries = selectors.get(command, [(None, None)])
        if isinstance(entries, tuple):
            entries = [entries]
        entries = list(dict.fromkeys(entries))
        try:
            response = connection.get(command)
        except Exception as exc:  # connection plugins surface device errors here
            text = str(exc)
            if _is_absent_error(text):
                if outcomes is not None:
                    _record_absence(outcomes, entries, text, command in unobservable_commands)
                continue
            if reading and _is_unsupported_node(text):
                if outcomes is not None:
                    for section, selector in entries:
                        outcomes.record(section, selector, "rejected", "unknown")
                continue
            if outcomes is not None:
                cls = error_class(text)
                for section, selector in entries:
                    outcomes.record(section, selector, "failed", "unknown", error_class_value=cls)
                # A recorded failure must not be silently lost: fail the module carrying the
                # sanitized per-selector outcomes. fail_json raises SystemExit, which no
                # `except Exception` in a facts get_facts can swallow, so the outcomes reach
                # the result even when a family has its own exception handling. The message
                # is sanitized like the outcomes: no raw device/transport text.
                module.fail_json(msg=_failure_message(resource, "targeted read", cls, entries),
                                 read_outcomes=_finalize_collector(outcomes))
            raise
        if _is_absent_error(response):
            if outcomes is not None:
                _record_absence(outcomes, entries, response, command in unobservable_commands)
            continue
        if reading and _is_unsupported_node(response):
            if outcomes is not None:
                for section, selector in entries:
                    outcomes.record(section, selector, "rejected", "unknown")
            continue
        reply = _targeted_reply(command, response)
        # For gathered single-instance reads, presence with default values is a
        # shared read semantic, not a per-family opt-in. Shared-node reads need
        # their instance checks instead; their path is not an instance identity.
        single = len(entries) == 1 and not instance_checks
        empty_absent = command in empty_absent_commands and single
        probe = reading and single and not empty_absent
        probed = None
        detail_read = command.startswith("info configure ") and command.endswith((" flat detail", " detail flat"))
        if not reply.strip() and detail_read:
            # Already the second step of the rule: 'flat detail' prints every existing
            # instance, so the header alone proves absence (not for the silent and
            # unobservable policies, whose header is no evidence).
            if probe and command not in silent_bare_commands and command not in unobservable_commands:
                probed = "confirmed_absent"
        elif not reply.strip() and (probe or command in bare_commands or command in silent_bare_commands):
            policy = ("silent" if command in silent_bare_commands
                      else "unobservable" if command in unobservable_commands else None)
            try:
                reply, probed = _probe_detail(connection, command, policy)
            except Exception as exc:
                # The bare-instance detail probe is a read like any other: a failure
                # there must be recorded and fail the module carrying the outcomes, not
                # bypass the failure-outcome handling.
                if outcomes is not None:
                    cls = error_class(str(exc))
                    for section, selector in entries:
                        outcomes.record(section, selector, "failed", "unknown", error_class_value=cls)
                    module.fail_json(msg=_failure_message(resource, "targeted read", cls, entries),
                                     read_outcomes=_finalize_collector(outcomes))
                raise
        if outcomes is not None:
            shared = len(entries) > 1
            for section, selector in entries:
                check = instance_checks.get((section, selector))
                if check is not None:
                    present = bool(reply.strip()) and bool(check(reply))
                else:
                    present = bool(reply.strip()) and not shared
                if present:
                    existence = "present"
                elif not reply.strip() and single and (empty_absent or probed == "confirmed_absent"):
                    existence = "confirmed_absent"
                else:
                    existence = "unknown"
                outcomes.record(section, selector, "rejected" if probed == "rejected" else "ok", existence)
        scoped_results.append(reply)
    return "\n".join(scoped_results)


def _strip_echo(command, lines):
    """Drop the echoed command at the top of a reply.

    The terminal wraps the echo at its width, also in the middle of a word
    ('... 1/1/2/1/100 fl' + 'at'), so the leading lines are removed while their
    plain concatenation is still a prefix of the command that was sent.
    """
    lines = [line.rstrip("\r") for line in lines]
    joined = ""
    for index, line in enumerate(lines):
        joined += line
        text = joined.strip()
        if text == command:
            return lines[index + 1:]
        if not text or not command.startswith(text):
            return lines
    return lines


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
    for line in _strip_echo(command, response.splitlines()):
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
    # An identity with a new line would inject a second CLI command into a read
    # (UnsafeCliCommandError, a ValueError: the facts layer fails the module).
    return check_cli_commands(commands, "targeted read of %s" % resource)


def _finalize_collector(collector):
    """The collector's sanitized result, recording the default parse outcome if the
    parser recorded none. Returns None for a whole-family (non-targeted) read."""
    if collector is None:
        return None
    if not collector.has_parse():
        collector.record_parse("unverified")
    return collector.to_result()


def targeted_outcomes(module, resource):
    """A ReadOutcomeCollector for a targeted gathered read, else None.

    Only ``state: gathered`` reads report per-selector outcomes; write-state reads
    (merged/replaced/deleted), whole-family reads, and reads with no module (isam_facts,
    offline parsing) carry none, exactly as before.
    """
    if module is None:
        return None
    if (module.params or {}).get("state") != "gathered":
        return None
    return ReadOutcomeCollector(resource)


def finish_targeted_outcomes(module, collector):
    """Finalize a targeted read's collector and stash it on the module for the result.

    Records the default parse outcome (unverified) when none was recorded, and stashes
    the sanitized result on ``module._isam_read_outcomes`` (surfaced centrally by the
    resource module's result). A no-op when there is no collector (whole-family or
    non-gathered read). Returns the sanitized result, or None.

    Named instances the device rejected ("invalid token") are missing from
    ``gathered`` exactly like absent ones; only read_outcomes tells them apart. So
    that a consumer of ``gathered`` alone is not misled, a module warning names the
    rejected selectors (user-supplied identities, no device text). The read does not
    fail: callers rely on the per-selector outcomes.
    """
    result = _finalize_collector(collector)
    if module is not None and result is not None:
        module._isam_read_outcomes = result
        _warn_rejected(module, result)
    return result


def _warn_rejected(module, result):
    rejected = [outcome for outcome in result.get("outcomes", ())
                if outcome.get("command") == "rejected" and outcome.get("selector") is not None]
    warn = getattr(module, "warn", None)
    if not rejected or not callable(warn):
        return
    names = ", ".join(
        "%s %s" % (outcome["section"], outcome["selector"]) if outcome.get("section") else str(outcome["selector"])
        for outcome in rejected)
    warn("targeted read of %s: the device rejected the read of %s (invalid token); their existence "
         "is unknown and they are missing from gathered (see read_outcomes)" % (result.get("resource"), names))


def targeted_explicit(module, section="config"):
    """Whether a gathered read's config names at least one instance in ``section`` --
    an explicit targeted request -- regardless of whether the identities became read
    commands. False for write states and for reads with no module (isam_facts, parsing)."""
    if module is None:
        return False
    params = getattr(module, "params", None) or {}
    if params.get("state") != "gathered":
        return False
    return bool(_section_items(params.get("config"), section))


def _has_targeted_entries(module, sections):
    """Whether config names at least one instance in any of ``sections`` -- an explicit
    targeted request -- regardless of whether the identities became read commands."""
    return any(targeted_explicit(module, section) for section in sections)


def targeted_read_gaps(module, resource, sections):
    """Config entries of an explicit gathered request that cannot be read.

    An entry is a gap when it is not a mapping, or any of its identity fields
    (TARGETED_GATHER) is missing or empty: no read command can be built for it.
    Returns one (section, index, missing fields or None) per gap; empty for
    write states and for requests without entries.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    params = getattr(module, "params", None) or {}
    if params.get("state") != "gathered":
        return []
    config = params.get("config")
    gaps = []  # type: list
    for section in sections:
        field = (TARGETED_GATHER.get(resource) or {}).get(section)
        if not field:
            continue
        fields = [field] if isinstance(field, str) else list(field)
        for index, item in enumerate(_section_items(config, section)):
            if not isinstance(item, dict):
                gaps.append((section, index, None))
                continue
            missing = [name for name in fields if item.get(name) in (None, "")]
            if missing:
                gaps.append((section, index, missing))
    return gaps


def assert_targeted_request(module, resource, sections):
    """Fail (RuntimeError, surfaced as module fail_json) when an explicit gathered
    request names instances that cannot be read.

    An explicit targeted request is never served partially and never silently
    widens to the whole-family read: when any named instance lacks a full
    identity, the whole read fails and no command is sent. A no-op for write
    states and for requests without entries.
    """
    gaps = targeted_read_gaps(module, resource, sections)
    if not gaps:
        return
    parts = []
    for section, index, missing in gaps:
        if missing:
            parts.append("%s[%d] has no value for identity field%s %s" % (
                section, index, "s" if len(missing) > 1 else "",
                ", ".join("'%s'" % name for name in missing)))
        else:
            parts.append("%s[%d] is not an instance mapping" % (section, index))
    raise RuntimeError(
        "targeted read of %s: %s; refusing to proceed with a partial targeted read"
        % (resource, "; ".join(parts)))


def selector_key(identity):
    """The sanitized selector for one identity: a composite identity (a tuple or list
    of fields) joined by '/', a single identity rendered as-is."""
    return "/".join(str(value) for value in identity) if isinstance(identity, (tuple, list)) else str(identity)


def _identity_commands(form, identity):
    """The read commands one format produces for one identity."""
    if callable(form):
        return list(form(identity))
    return [form % (identity if isinstance(identity, tuple) else (identity,))]


def _targeted_selectors(module, resource, formats):
    """A {command: [(section, selector), ...]} map labeling each targeted read command
    with every config section and instance identity it addresses. Several identities
    can share one read command (a section read through its whole node); each keeps its
    own entry, so one outcome is recorded per selector."""
    selectors = {}  # type: dict
    for section, form in formats.items():
        for identity in requested_identities(module, resource, section):
            entry = (section, selector_key(identity))
            for command in _identity_commands(form, identity):
                entries = selectors.setdefault(command, [])
                if entry not in entries:
                    entries.append(entry)
    return selectors


def _targeted_instance_checks(module, resource, instance_checks):
    """{(section, selector): callable(reply) -> bool} from per-section checks
    {section: callable(reply, identity) -> bool}."""
    checks = {}
    for section, check in (instance_checks or {}).items():
        for identity in requested_identities(module, resource, section):
            checks[(section, selector_key(identity))] = (
                lambda reply, _check=check, _identity=identity: _check(reply, _identity))
    return checks


def get_targeted_config(module, connection, resource, fallback, formats, write_states=False, bare_sections=(),
                        silent_bare_sections=(), instance_checks=None, empty_absent_sections=()):
    """The whole resource, or only the instances named in config with state gathered.

    fallback: command for the whole resource, or a callable(connection) reading it.
    formats: instance list -> command format with one %s per identity field, or a
    callable returning the commands for one identity.
    write_states: also compare merged/replaced/deleted against only the named
    instances (only for resources made of instance lists, where that is exact).
    bare_sections: lists whose whole read shows unconfigured instances as their bare
    path (see get_scoped_config bare_commands); silent_bare_sections likewise, for
    nodes whose detail read prints nothing either (silent_bare_commands).
    instance_checks: {section: callable(reply, identity) -> bool} for sections whose
    read command returns more than the addressed instance (a whole node shared by
    every identity of the section): the instance is present when the check finds it in
    the reply, else unknown (see get_scoped_config instance_checks).

    A targeted gathered read reports sanitized per-selector read outcomes: a collector
    is created for gathered reads, threaded into the read, and stashed on the module for
    the resource module to surface (see finish_targeted_outcomes). An explicit targeted
    request (config names instances) is never served partially: a named instance without
    a full identity, or a request that yields no read command, fails the read before
    anything is sent, rather than silently widening to the whole-family read.
    """
    states = ("merged", "replaced", "deleted", "gathered") if write_states else ("gathered",)
    if module is None:
        return fallback(connection) if callable(fallback) else connection.get(fallback)
    state = module.params.get("state", "merged")
    if state not in states:
        return fallback(connection) if callable(fallback) else connection.get(fallback)
    commands = targeted_commands(module, resource, formats)
    explicit = state == "gathered" and _has_targeted_entries(module, formats)
    if explicit:
        assert_targeted_request(module, resource, list(formats))
    if not commands and not explicit:
        # No instances named: the whole resource is read, as before.
        return fallback(connection) if callable(fallback) else connection.get(fallback)
    if not commands:
        # Instances were explicitly named but none became a read command: refuse to
        # silently widen to a whole-family read.
        raise RuntimeError(
            "targeted read requested but no targeted commands could be generated; "
            "refusing to widen to a whole-family read")

    def section_commands(sections):
        return targeted_commands(module, resource, dict((s, formats[s]) for s in sections if s in formats))

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import absence_policy

    silent = tuple(silent_bare_sections) + tuple(s for s in formats if absence_policy(resource, s) == "silent")
    unobservable = tuple(s for s in formats if absence_policy(resource, s) == "unobservable")
    collector = targeted_outcomes(module, resource)
    try:
        data = get_scoped_config(module, connection, None, None, commands, safe_states=states,
                                 bare_commands=section_commands(bare_sections),
                                 silent_bare_commands=section_commands(silent),
                                 unobservable_commands=section_commands(unobservable),
                                 empty_absent_commands=section_commands(empty_absent_sections),
                                 outcomes=collector,
                                 selectors=_targeted_selectors(module, resource, formats),
                                 instance_checks=_targeted_instance_checks(module, resource, instance_checks))
    finally:
        finish_targeted_outcomes(module, collector)
    return data


def _catalog_contains(catalog, resource, section, identity):
    """Whether one parsed full catalog lists the addressed instance.

    catalog: the family's parsed structure -- the instance list itself for a
    "config" section, the nested list for a dotted section. Identity
    comparison is str()-normalized, so parsed ints compare equal to requested
    ints (or strings): the vlan priority-regen ids are ints end-to-end.
    """
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    field = (TARGETED_GATHER.get(resource) or {}).get(section)
    if not field:
        return False
    fields = [field] if isinstance(field, str) else list(field)
    wanted = tuple(str(value) for value in identity) if isinstance(identity, (tuple, list)) else (str(identity),)
    for item in _section_items(catalog, section):
        if not isinstance(item, dict):
            continue
        if tuple(str(item.get(name)) for name in fields) == wanted:
            return True
    return False


def get_whole_node_targeted(module, connection, resource, command, sections, parse):
    """The whole node, read once, with per-instance outcomes for a targeted request.

    Some instance lists have no single-instance read: the device only exposes the
    whole node (interface_alarms; the vlan priority-regen profiles). For an
    explicit targeted request (state gathered, config names instances) the node is
    read once -- the only read the device exposes -- and each requested instance is
    reported from the parsed catalog: present when the catalog lists it, unknown
    when it does not. Absence from the catalog is NOT established absence: the
    parser's catalog completeness is unverified (the parse axis stays 'unverified'),
    and a reply line the parser does not recognize would make a configured
    instance vanish from the catalog. Only the device's own node-absence signal
    confirms absence, as in scoped reads. This is the documented exception to the
    scoped-read contract: no per-instance command is sent, and the returned
    string is the full catalog, unfiltered.

    The read's error taxonomy is the scoped read's: an explicit node absence
    confirms absence of every requested instance; an invalid-token rejection and
    a missing dependency leave them unknown; any other failure fails the module
    carrying the sanitized outcomes. parse is the family's catalog parser (raw
    reply -> parsed catalog); a reply it cannot process is classified before the
    module fails (parse axis 'failed', every requested instance unknown), and the
    failure then propagates, as a parse failure does for a whole-family read.
    No outcomes for module-less reads (isam_facts, parsing), write states, or
    requests without named instances: those read the node plainly, as before.
    """
    if module is None or (module.params or {}).get("state") != "gathered":
        return connection.get(command)
    if not _has_targeted_entries(module, sections):
        # No instances named: the whole node is read, as before, with no outcomes.
        return connection.get(command)
    assert_targeted_request(module, resource, sections)
    collector = targeted_outcomes(module, resource)
    requested = [(section, identity)
                 for section in sections
                 for identity in requested_identities(module, resource, section)]
    requested_keys = [(section, selector_key(identity)) for section, identity in requested]

    def record_all(command_status, existence, **kwargs):
        for section, identity in requested:
            collector.record(section, selector_key(identity), command_status, existence, **kwargs)

    try:
        try:
            response = unwrap_response(connection.get(command)) or ""
        except Exception as exc:  # connection plugins surface device errors here
            text = str(exc)
            if _is_absent_error(text):
                # The device says the node does not exist (nothing under it can be),
                # or that a dependency is missing (existence unknown).
                _record_absence(collector, requested_keys, text)
                return ""
            if _is_unsupported_node(text):
                record_all("rejected", "unknown")
                return ""
            cls = error_class(text)
            record_all("failed", "unknown", error_class_value=cls)
            # A recorded failure must not be silently lost: fail the module carrying
            # the sanitized per-selector outcomes (see get_scoped_config); the message
            # carries no raw device/transport text.
            module.fail_json(msg=_failure_message(resource, "whole-node read", cls, requested_keys),
                             read_outcomes=_finalize_collector(collector))
        if _is_absent_error(response):
            _record_absence(collector, requested_keys, response)
            return ""
        if _is_unsupported_node(response):
            record_all("rejected", "unknown")
            return ""
        try:
            catalog = parse(response)
        except Exception as exc:
            # The reply arrived but the family's parser could not process it:
            # classify the parse failure (parse axis 'failed', existence unknown
            # for every requested instance -- an unparseable reply establishes
            # no absence) before propagating it, as a parse failure does for a
            # whole-family read.
            collector.record_parse("failed")
            record_all("ok", "unknown")
            # The parser's message may quote reply lines: name its class only.
            module.fail_json(
                msg="whole-node read of %s: the device replied but the catalog "
                    "could not be parsed (%s)" % (resource, type(exc).__name__),
                read_outcomes=_finalize_collector(collector))
        for section, identity in requested:
            if _catalog_contains(catalog, resource, section, identity):
                collector.record(section, selector_key(identity), "ok", "present")
            else:
                # Absence from the parsed catalog is not established absence:
                # the parser's catalog completeness is unverified, and a reply
                # line it does not recognize would make a configured instance
                # vanish from the catalog. Only the device's own node-absence
                # signal above confirms absence.
                collector.record(section, selector_key(identity), "ok", "unknown")
        return response
    finally:
        finish_targeted_outcomes(module, collector)


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
