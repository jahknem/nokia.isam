# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


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
