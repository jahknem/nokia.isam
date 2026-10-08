# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

# Bridge VLAN sub-tree aliases. Both entries are confirmed by the device's own
# help listing for "configure bridge port <port> vlan-id <id>".
BRIDGE_VLAN_SCOPE_ALIASES = {"network": "l2fwder"}


def canonical_key(key):
    return key.replace("-", "_")


def normalize_resource_keys(data, aliases=None):
    """Return a copy of data with canonical resource keys added.

    Resource args may arrive using CLI spellings such as ``admin-up`` while
    templates compare against Python identifiers such as ``admin_up``. Keep the
    original keys intact for compatibility and add canonical aliases once at the
    resource boundary.
    """
    if not isinstance(data, dict):
        return data

    result = dict(data)
    for key, value in data.items():
        result.setdefault(canonical_key(key), value)

    for source, target in aliases or ():
        if source in result and target not in result:
            result[target] = result[source]

    return result


def normalize_bridge_vlan_alias(data, strict=False):
    """Resolve obsolete bridge VLAN spellings onto their canonical form.

    The ISAM CLI keeps two backwards-compatible aliases in the bridge VLAN
    sub-tree, confirmed by the device's own ``help configure bridge port
    <port> vlan-id <id>`` listing:

    * ``network-vlan`` is documented as an "obsolete parameter replaced by
      parameter l2fwder-vlan" and shares its ``<Network::StackedVlan>`` type.
    * the ``vlan-scope`` value ``network`` is documented as an "obsolete
      alternative replaced by l2fwder".

    Resource inputs, parsed legacy config and rendered commands therefore
    share one internal representation: ``l2fwder_vlan`` as ``str`` and
    ``vlan_scope`` as the canonical scope. When ``strict`` is true,
    conflicting ``network_vlan``/``l2fwder_vlan`` values are rejected instead
    of silently choosing one.
    """
    result = normalize_resource_keys(data)
    if not isinstance(result, dict):
        return result

    legacy_value = result.pop("network_vlan", None)
    canonical_value = result.get("l2fwder_vlan")
    if canonical_value is None:
        if legacy_value is not None:
            result["l2fwder_vlan"] = str(legacy_value)
    elif legacy_value is not None and strict:
        if str(canonical_value) != str(legacy_value):
            raise ValueError(
                "network_vlan is an alias of l2fwder_vlan; conflicting values "
                "were provided"
            )
    else:
        result["l2fwder_vlan"] = str(canonical_value)

    vlan_scope = result.get("vlan_scope")
    if vlan_scope in BRIDGE_VLAN_SCOPE_ALIASES:
        result["vlan_scope"] = BRIDGE_VLAN_SCOPE_ALIASES[vlan_scope]
    return result


def normalize_resource_list(data, aliases=None):
    return [normalize_resource_keys(entry, aliases=aliases) for entry in data or []]


def parse_cli_fields(tokens, bool_fields=(), value_fields=None, none_for_negated_values=False):
    """Parse CLI token pairs into canonical resource keys.

    Handles compact ISAM syntax such as ``admin-up``, ``no admin-up`` and
    ``timer-b 500``. ``value_fields`` maps CLI field names to either ``str`` or
    ``int``. Unknown tokens are skipped, matching the existing parser behavior.
    """
    parsed = {}
    bool_field_set = set(bool_fields or ())
    value_field_map = value_fields or {}
    index = 0

    while index < len(tokens):
        token = tokens[index]
        negate = False
        if token == "no" and index + 1 < len(tokens):
            token = tokens[index + 1]
            negate = True
            index += 1

        if token in bool_field_set:
            parsed[canonical_key(token)] = not negate
        elif token in value_field_map and negate and none_for_negated_values:
            parsed[canonical_key(token)] = None
        elif token in value_field_map and index + 1 < len(tokens):
            value = _clean_cli_value(tokens[index + 1])
            parsed[canonical_key(token)] = _coerce_cli_value(value, value_field_map[token])
            index += 1
        index += 1

    return parsed


def _clean_cli_value(value):
    if isinstance(value, str):
        return value.strip('"')
    return value


def _coerce_cli_value(value, value_type):
    if value_type != "int":
        return value
    try:
        return int(value)
    except (TypeError, ValueError):
        return value


def parse_cli_key_values(
    tokens,
    bool_fields=(),
    int_fields=(),
    infer_numeric=False,
    bare_keys_as_true=False,
    negated_value=None,
):
    """Parse arbitrary CLI key/value tokens into canonical resource keys."""
    parsed = {}
    bool_field_set = set(bool_fields or ())
    int_field_set = {canonical_key(field) for field in int_fields or ()}
    index = 0

    while index < len(tokens):
        negate = tokens[index] == "no"
        key_index = index + 1 if negate else index
        if key_index >= len(tokens):
            break

        token = tokens[key_index]
        key = canonical_key(token)
        if key in bool_field_set:
            parsed[key] = not negate
            index = key_index + 1
        elif negate and negated_value is not None:
            parsed[key] = negated_value
            index = key_index + 1
        elif negate:
            index = key_index + 1
        elif key_index + 1 < len(tokens):
            value = _clean_cli_value(tokens[key_index + 1])
            if key in int_field_set or (infer_numeric and isinstance(value, str) and value.isdigit()):
                value = _coerce_cli_value(value, "int")
            parsed[key] = value
            index = key_index + 2
        elif bare_keys_as_true:
            parsed[key] = True
            index = key_index + 1
        else:
            index = key_index + 1

    return parsed


def iter_cli_fields(tokens, bool_fields=(), value_fields=(), negated_value_fields=()):
    """Yield ``(negate, key, value)`` triples from compact CLI field tokens."""
    bool_field_set = set(bool_fields or ())
    value_field_set = set(value_fields or ())
    negated_value_field_set = set(negated_value_fields or ())
    index = 0

    while index < len(tokens):
        token = tokens[index]
        negate = token == "no"
        key_index = index + 1 if negate else index
        if key_index >= len(tokens):
            break

        key = tokens[key_index]
        if negate and key in negated_value_field_set and key_index + 1 < len(tokens):
            yield True, key, tokens[key_index + 1]
            index = key_index + 2
        elif key in bool_field_set:
            yield negate, key, None
            index = key_index + 1
        elif key in value_field_set and key_index + 1 < len(tokens):
            yield negate, key, tokens[key_index + 1] if not negate else None
            index = key_index + (1 if negate else 2)
        else:
            index = key_index + 1


def compact_cli_commands(commands, scopes):
    """Combine adjacent commands that match an explicitly supported CLI scope.

    Each scope is a regular expression with named ``scope`` and ``suffix``
    groups. Resource modules define whether negated attributes are valid in
    that scope; this helper deliberately does not infer a scope from a shared
    text prefix.
    """
    compiled_scopes = []
    for rule in scopes:
        if isinstance(rule, tuple):
            scope, label = rule
        else:
            scope, label = rule, None
        compiled_scopes.append(
            (re.compile(scope) if isinstance(scope, str) else scope, label)
        )
    compacted = []
    previous_scope = None

    for command in commands:
        match = None
        label = None
        for compiled_scope, scope_label in compiled_scopes:
            candidate = compiled_scope.match(command)
            if candidate is not None:
                match = candidate
                label = scope_label
                break
        if match is None:
            compacted.append(command)
            previous_scope = None
            continue

        scope = (label, match.group("scope"))
        suffix = match.group("suffix")
        if scope == previous_scope:
            compacted[-1] += " " + suffix
        else:
            compacted.append(command)
            previous_scope = scope

    return compacted
