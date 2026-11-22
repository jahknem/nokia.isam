# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

import re

__metaclass__ = type

from anytree import Node
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    assert_targeted_request,
    finish_targeted_outcomes,
    get_scoped_config,
    selector_key,
    targeted_explicit,
    targeted_outcomes,
    unwrap_response,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_interfaces.qos_interfaces import Qos_interfacesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_interfaces import Qos_interfacesTemplate


class Qos_interfacesFacts(object):
    """The isam qos_interfaces facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Qos_interfacesArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the interfaces named in config (targeted gathering)."""
        config = self._module.params.get("config") or []
        assert_targeted_request(self._module, "qos_interfaces", ("config",))
        collector = targeted_outcomes(self._module, "qos_interfaces")
        commands = []
        selectors = {}
        for item in config:
            name = item["name"]
            command = "info configure qos interface %s flat" % name
            commands.append(command)
            selectors[command] = ("config", selector_key(name))
        data = get_scoped_config(
            self._module,
            connection,
            config,
            "info configure qos interface flat",
            commands,
            outcomes=collector,
            selectors=selectors,
            # An explicit gathered request that names instances must not silently widen
            # to the whole-family read when none of them became a read command.
            require_targeted=targeted_explicit(self._module, "config"),
        )
        finish_targeted_outcomes(self._module, collector)
        return data

    def populate_facts(self, connection, ansible_facts, data=None):
        facts = {}

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)
        data = self._flatten_config(data)

        parser = Qos_interfacesTemplate(lines=data, module=self._module)
        # Same result as parser.parse(), without one regex/Jinja pass per field and
        # line: the template parse took minutes on a full MSAN (tens of thousands of
        # lines after splitting compact flat output).
        objs = list(self._parse_lines(data).values())

        for item in objs:
            for key in ["queue", "upstream_queue", "ds_rem_queue"]:
                if isinstance(item.get(key), dict):
                    item[key] = list(item[key].values())

        ansible_facts["ansible_network_resources"].pop("qos_interfaces", None)
        params = utils.remove_empties(
            parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        )
        facts["qos_interfaces"] = params.get("config", [])
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts

    _SEGMENT = re.compile(
        r"^configure\s+qos\s+interface\s+(?P<name>\S+)\s+"
        r"(?:(?P<container>queue|upstream-queue|ds-rem-queue)\s+(?P<id>\d+)\s+)?"
        r"(?P<negate>no\s+)?(?P<field>\S+)(?:\s+(?P<value>\S+))?$"
    )

    @classmethod
    def _template_fields(cls):
        """Fields the template parses, per container (None: interface level), with
        whether the "no" form is part of the grammar."""
        if not hasattr(cls, "_fields_cache"):
            fields = {}
            for parser in Qos_interfacesTemplate.PARSERS:
                parts = parser["name"].split(".")[1:]
                container = parts[0] if len(parts) == 2 else None
                negatable = "(?P<negate>" in parser["getval"].pattern
                fields.setdefault(container, {})[parts[-1]] = negatable
            cls._fields_cache = fields
        return cls._fields_cache

    def _parse_lines(self, lines):
        """Flat, one-attribute-per-line QoS interface config -> {name: entry}.

        Exactly the template's result: only template fields, types from the argspec
        (int values must be digits), negated values None, flags True/False.
        """
        options = self.argument_spec["config"]["options"]
        known = self._template_fields()
        result = {}
        for line in lines or []:
            match = self._SEGMENT.match(line)
            if not match:
                continue
            container = match.group("container")
            container = container.replace("-", "_") if container else None
            field = match.group("field").replace("-", "_")
            negatable = known.get(container, {}).get(field)
            if negatable is None:
                continue
            spec = (options[container]["options"] if container else options)[field]
            negate, value = bool(match.group("negate")), match.group("value")
            if spec.get("type") == "bool":
                if container or value is not None:
                    continue
                parsed = not negate
            elif negate:
                if not negatable or value is not None:
                    continue
                parsed = None
            elif value is None:
                continue
            elif spec.get("type") == "int":
                if not value.isdigit():
                    continue
                parsed = int(value)
            else:
                parsed = value
            name = match.group("name")
            entry = result.setdefault(name, {"name": name})
            if container:
                number = int(match.group("id"))
                entry = entry.setdefault(container, {}).setdefault(number, {"id": number})
            # Like the template's merge: a negated (None) value never replaces a set one.
            if parsed is None:
                entry.setdefault(field, None)
            else:
                entry[field] = parsed
        return result

    def _count_spaces(self, line):
        return len(line) - len(line.lstrip(" "))

    def _parse_config_to_tree(self, config):
        if not config:
            return None
        last_spaces = 0
        root = None
        parent_node = None
        prev_node = None

        for line in config.splitlines():
            if line.startswith("echo") or line.startswith("#"):
                continue

            stripped = line.split("#", 1)[0].strip()
            if not stripped:
                continue

            if parent_node is None:
                root = Node(stripped)
                parent_node = root
                prev_node = root
            elif stripped == "exit":
                if self._count_spaces(line) < last_spaces and parent_node.parent:
                    parent_node = parent_node.parent
                else:
                    continue
            elif self._count_spaces(line) > last_spaces:
                parent_node = prev_node
                prev_node = Node(stripped, parent=prev_node)
            else:
                prev_node = Node(stripped, parent=parent_node)

            last_spaces = self._count_spaces(line)
        return root

    def _flatten_config(self, config):
        if not config:
            return []
        lines = [
            line.strip()
            for line in config.splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("echo")
        ]
        # Flat replies: use only the configuration lines. A scoped reply can carry
        # other lines (echo, prompt remnants); requiring every line to match sent
        # such replies to the tree parser, which produced nothing.
        flat = [line for line in lines if line.startswith("configure qos interface ")]
        if flat:
            return self._compact_lines(flat)
        root = self._parse_config_to_tree(config)
        if root is None:
            return []
        flat_config = []
        for leaf in root.leaves:
            line = []
            for node in leaf.path:
                line.append(node.name)
            flat_config.append(" ".join(line))
        return flat_config

    # Fields accepted directly on "configure qos interface <name> ..." with a
    # single value token (ground truth: _top_parser() calls in
    # rm_templates/qos_interfaces.py).
    _TOP_VALUE_FIELDS = frozenset((
        "scheduler-node", "ingress-profile", "cac-profile", "ext-cac",
        "ds-num-queue", "ds-num-rem-queue", "us-num-queue",
        "oper-weight", "oper-rate", "dsfld-shaper-prof",
        "bandwidth-profile", "bandwidth-sharing",
        "aggr-usq-profile", "aggr-dsq-profile", "gem-sharing",
        "scheduler-mode", "mc-scheduler-node", "bc-scheduler-node",
        "ds-schedule-tag",
    ))
    # Bare boolean flags with no value (ground truth: _top_bool_parser()
    # calls in rm_templates/qos_interfaces.py).
    _TOP_FLAG_FIELDS = frozenset((
        "ds-queue-sharing", "us-queue-sharing", "queue-stats-on",
        "autoschedule", "us-vlanport-queue",
    ))
    # Fields accepted on "... <container> <id> ..." with a single value
    # token (ground truth: _queue_parser() calls in
    # rm_templates/qos_interfaces.py).
    _CONTAINER_FIELDS = {
        "queue": frozenset((
            "priority", "weight", "oper-weight", "queue-profile", "shaper-profile",
        )),
        "upstream-queue": frozenset((
            "priority", "weight", "bandwidth-profile", "ext-bw",
            "bandwidth-sharing", "queue-profile", "shaper-profile",
        )),
        "ds-rem-queue": frozenset(("priority", "weight")),
    }

    @classmethod
    def _compact_lines(cls, lines):
        result = []
        for line in lines:
            match = re.match(r"(configure\s+qos\s+interface\s+\S+)\s+(.*)", line)
            if not match:
                result.append(line)
                continue
            prefix, rest = match.groups()
            result.extend(cls._split_qos_tokens(prefix, rest.split()))
        return result

    @classmethod
    def _split_qos_tokens(cls, prefix, tokens):
        # Live devices compact every simultaneously-set attribute for a QoS
        # interface (and each queue/upstream-queue/ds-rem-queue id) onto one
        # line, e.g. "scheduler-node X cac-profile Y us-num-queue Z ..." or
        # "queue 0 priority 6 weight 34 oper-weight 34 queue-profile P
        # shaper-profile S". This walks the token stream, tracking which
        # container (if any) is currently in scope, and re-emits one
        # "configure qos interface <name> [<container> <id>] <field>
        # [<value>]" line per attribute so the existing per-field regex
        # parsers in rm_templates/qos_interfaces.py can match each one.
        segments = []
        container = None
        n = len(tokens)
        i = 0
        while i < n:
            negate = tokens[i] == "no"
            field_idx = i + 1 if negate else i
            if field_idx >= n:
                break
            field = tokens[field_idx]
            value_idx = field_idx + 1

            if (
                not negate
                and field in cls._CONTAINER_FIELDS
                and value_idx < n
                and tokens[value_idx].isdigit()
            ):
                container = (field, tokens[value_idx])
                i = value_idx + 1
                continue

            if container and field in cls._CONTAINER_FIELDS[container[0]]:
                if negate:
                    segments.append(
                        "%s %s %s no %s" % (prefix, container[0], container[1], field)
                    )
                    i = field_idx + 1
                    continue
                value = tokens[value_idx] if value_idx < n else None
                if value is None:
                    i = field_idx + 1
                    continue
                segments.append(
                    "%s %s %s %s %s" % (prefix, container[0], container[1], field, value)
                )
                i = value_idx + 1
                continue

            if field in cls._TOP_FLAG_FIELDS:
                segments.append("%s %s%s" % (prefix, "no " if negate else "", field))
                container = None
                i = field_idx + 1
                continue

            if field in cls._TOP_VALUE_FIELDS:
                if negate:
                    segments.append("%s no %s" % (prefix, field))
                    container = None
                    i = field_idx + 1
                    continue
                value = tokens[value_idx] if value_idx < n else None
                if value is None:
                    i = field_idx + 1
                    continue
                segments.append("%s %s %s" % (prefix, field, value))
                container = None
                i = value_idx + 1
                continue

            # Unrecognized token (e.g. an attribute this collection does not
            # yet model). Skip it defensively rather than looping forever or
            # misattributing it to the wrong field/container.
            i = field_idx + 1
        return segments
