# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Several reads on one MSAN in one module call, each with its own outcome (isam_read).

A read names one family: a configuration family (``kind: configuration``, the facts
registry plus the module-direct pppoe families) or an operational subset
(``kind: operational``). Without ``ids`` it reads the whole family; with ``ids`` only
those instances of one instance list (``section``, see targeted.py), through the same
targeted gathering the family module uses with ``state: gathered``.

Every read is isolated: a read that fails, or a family the MSAN does not support,
becomes an error entry and the next read runs. The result of a read says what was
found, what the device confirmed absent, and what stays unverified; only a confirmed
absence may ever remove cached configuration. Credentials are removed from the data
(the fields the family argspec marks ``no_log``, by path, and SENSITIVE_KEYS); warnings
are reduced to stable categories, never the device's own text.
"""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
import time

KINDS = ("configuration", "operational")

# Credential names removed from every read's data, in addition to the fields the
# family argspec marks no_log.
SENSITIVE_KEYS = frozenset("""
    auth_pwd log_auth_pwd priv_pwd passwd password secret community
    snmp_community snmp_auth_password snmp_priv_password vault_password
    token access_token private_key private_key_data auth_key encryption_key
    secret_key
""".split())

# An identity value goes into a CLI read command: no whitespace, no CLI metacharacters.
_ID_PATTERN = re.compile(r"[A-Za-z0-9_.:/@+=-]{1,128}")

# Configuration families outside the facts registry, read through their resource
# module with state gathered: resource -> (module_utils path, class, constructor args).
MODULE_DIRECT = {
    "pppoe_client_interface": ("config.pppoe_client.pppoe_client", "PppoeClient", ("interface",),
                               "argspec.pppoe_client.pppoe_client", "PppoeClientArgs"),
    "pppoe_client_ppp_profile": ("config.pppoe_client.pppoe_client", "PppoeClient", ("profile",),
                                 "argspec.pppoe_client.pppoe_client", "PppoeClientArgs"),
    "pppoel2_statistics": ("config.pppoel2.pppoel2", "Pppoel2", (),
                           "argspec.pppoel2.pppoel2", "Pppoel2Args"),
}

# Families whose facts class serves several public resources and tells them apart
# by the calling module's argspec (facts/multicast: module_resource).
FAMILY_ARGSPECS = {
    "igmp": ("argspec.igmp.igmp", "IgmpArgs"),
    "mcast_control": ("argspec.mcast_control.mcast_control", "Mcast_controlArgs"),
    "multicast": ("argspec.multicast.multicast", "MulticastArgs"),
}

_BASE = "ansible_collections.nokia.isam.plugins.module_utils.network.isam."


class ReadRequestError(ValueError):
    """A read request the module cannot serve; reported on that read only."""


class _ReadFailed(Exception):
    """A family's fail_json during one read; ends that read, not the module."""


class _ReadModule(object):
    """The real module, seen by one read with its own params.

    Facts classes and resource modules take their request from ``module.params``
    (state, config) and report through ``fail_json``/``warn``; this stand-in gives each
    read its own params, turns fail_json into an exception for that read and collects
    its warnings. Everything else (connection, socket path, check mode) is the real
    module's. Targeted read outcomes are stashed on this object, so they belong to
    this read only.
    """

    def __init__(self, module, params, argument_spec=None):
        self.__dict__["_real"] = module
        self.params = params
        self.argument_spec = argument_spec or {}
        self.read_warnings = []

    def __getattr__(self, name):
        return getattr(self.__dict__["_real"], name)

    def fail_json(self, **kwargs):
        raise _ReadFailed(str(kwargs.get("msg") or "read failed"))

    def warn(self, warning):
        self.read_warnings.append(str(warning))

    def exit_json(self, **kwargs):  # pragma: no cover - a read never exits the module
        raise AssertionError("a read must not exit the module")


def _import(path, name):
    module = __import__(_BASE + path, fromlist=[name])
    return getattr(module, name)


def _registries():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
        FACT_LEGACY_SUBSETS,
        FACT_RESOURCE_SUBSETS,
    )
    return FACT_RESOURCE_SUBSETS, FACT_LEGACY_SUBSETS


def configuration_resources():
    resources, _legacy = _registries()
    return frozenset(resources) | frozenset(MODULE_DIRECT)


def operational_resources():
    _resources, legacy = _registries()
    return frozenset(legacy)


def safe_warnings(warnings):
    """Stable warning classes, never the device's original warning text."""
    categories = []
    for warning in warnings or []:
        value = str(warning).lower()
        if "not supported" in value or "invalid token" in value:
            category = "unsupported_resource"
        elif "unmatched configuration" in value:
            category = "unmatched_configuration"
        elif "no output" in value or "empty" in value:
            category = "empty_response"
        else:
            category = "collection_warning"
        if category not in categories:
            categories.append(category)
    return categories


def no_log_paths(spec, prefix=""):
    """Paths of the fields an argspec marks no_log ("snmp_communities[].name")."""
    found = set()
    for name, option in (spec or {}).items():
        if not isinstance(option, dict):
            continue
        path = prefix + name + ("[]" if option.get("type") == "list" else "")
        if option.get("no_log"):
            found.add(prefix + name)
        found |= no_log_paths(option.get("options"), path + ".")
    return found


def redact(value, spec=None):
    """Data without credentials.

    ``spec`` is the family's ``config`` option: a field it marks no_log is removed
    where the argspec puts it (an SNMP community is a ``name``). Fields named in
    SENSITIVE_KEYS are removed everywhere.
    """
    spec = spec if isinstance(spec, dict) else {}
    if isinstance(value, list):
        return [redact(item, spec) for item in value]
    if isinstance(value, dict):
        options = spec.get("options") or {}
        kept = {}
        for key, item in value.items():
            option = options.get(key)
            option = option if isinstance(option, dict) else {}
            if option.get("no_log") or str(key).lower().replace("-", "_") in SENSITIVE_KEYS:
                continue
            kept[key] = redact(item, option)
        return kept
    return value


class _NoModule(object):
    params = {}  # type: dict


def family_argspec(resource):
    """The argspec of a configuration family's module, or None when it declares none."""
    if resource in MODULE_DIRECT:
        _path, _name, _args, spec_path, spec_name = MODULE_DIRECT[resource]
        return _import(spec_path, spec_name).argument_spec
    if resource in FAMILY_ARGSPECS:
        return _import(*FAMILY_ARGSPECS[resource]).argument_spec
    resources, _legacy = _registries()
    return getattr(resources[resource](_NoModule()), "argument_spec", None)


def family_spec(resource):
    """The ``config`` option of a family's argspec (what its gathered data follows), or None."""
    option = (family_argspec(resource) or {}).get("config")
    return option if isinstance(option, dict) else None


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _identity_fields(resource, section):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    sections = TARGETED_GATHER.get(resource) or {}
    if section not in sections:
        raise ReadRequestError(
            "%s has no instance list %r that can be read by identity (known: %s)"
            % (resource, section, ", ".join(sorted(sections)) or "none"))
    field = sections[section]
    return [field] if isinstance(field, str) else list(field)


def _entry(fields, identity):
    """The config entry naming one instance: {field: value} for every identity field."""
    if isinstance(identity, dict):
        missing = [name for name in fields if identity.get(name) in (None, "")]
        if missing or set(identity) - set(fields):
            raise ReadRequestError("identity %r must name exactly the fields %s" % (identity, fields))
        entry = dict((name, identity[name]) for name in fields)
    elif len(fields) == 1:
        entry = {fields[0]: identity}
    else:
        raise ReadRequestError("composite identity %s needs a mapping per id" % fields)
    for value in entry.values():
        if not isinstance(value, (str, int)) or isinstance(value, bool) or not _ID_PATTERN.fullmatch(str(value)):
            raise ReadRequestError("invalid identity value %r (no whitespace or CLI metacharacters)" % (value,))
    return entry


def _key(fields, entry):
    """The selector of one instance, as the read outcomes name it (see selector_key)."""
    return "/".join(str(entry[name]) for name in fields)


def _nest(section, entries):
    """The module config naming ``entries`` in one instance list (dotted for nested lists)."""
    if section == "config":
        return entries
    config = entries
    for part in reversed(section.split(".")):
        config = {part: config}
    return config


def _section_items(data, section):
    if section == "config":
        return data if isinstance(data, list) else []
    for part in section.split("."):
        data = data.get(part) if isinstance(data, dict) else None
    return data if isinstance(data, list) else []


def _empty(resource):
    """The empty value of a family: a list, or one empty list per instance list."""
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.targeted import TARGETED_GATHER

    sections = TARGETED_GATHER.get(resource) or {}
    if not sections or "config" in sections:
        return []
    empty = {}
    for section in sections:
        _nest_into(empty, section.split("."))
    return empty


def _nest_into(target, parts):
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target.setdefault(parts[-1], [])


def normalize(read, configuration=None, operational=None):
    """One read request, checked: {kind, resource, section, ids}. Raises ReadRequestError."""
    if not isinstance(read, dict):
        raise ReadRequestError("a read must be a mapping")
    kind = read.get("kind") or "configuration"
    resource = read.get("resource")
    ids = read.get("ids") or []
    section = read.get("section")
    if kind not in KINDS:
        raise ReadRequestError("kind must be one of %s" % ", ".join(KINDS))
    allowed = (configuration if configuration is not None else configuration_resources()) if kind == "configuration" \
        else (operational if operational is not None else operational_resources())
    if not isinstance(resource, str) or resource not in allowed:
        raise ReadRequestError("unsupported %s resource %r" % (kind, resource))
    if not isinstance(ids, list):
        raise ReadRequestError("ids must be a list")
    if ids:
        if kind != "configuration":
            raise ReadRequestError("operational subsets are read whole; ids are not supported")
        if not section:
            raise ReadRequestError("ids need the instance list (section) they name")
        fields = _identity_fields(resource, section)
        entries = [_entry(fields, identity) for identity in ids]
        keys = [_key(fields, entry) for entry in entries]
        if len(set(keys)) != len(keys):
            raise ReadRequestError("duplicate id in one read")
    elif section not in (None, ""):
        raise ReadRequestError("section without ids: leave both out to read the whole family")
    return {"kind": kind, "resource": resource, "section": section or None, "ids": ids}


def _gather_config(module, resource, config):
    """(data, warnings, read outcomes) of one configuration family."""
    if resource in MODULE_DIRECT:
        path, name, args, _spec_path, _spec_name = MODULE_DIRECT[resource]
        proxy = _ReadModule(module, {"state": "gathered", "config": config, "running_config": None},
                            family_argspec(resource))
        result = _import(path, name)(proxy, *args).execute_module()
        warnings = list(result.get("warnings") or []) + proxy.read_warnings
        return (result.get("gathered"), warnings,
                result.get("read_outcomes") or getattr(proxy, "_isam_read_outcomes", None), family_spec(resource))

    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts

    proxy = _ReadModule(module, {
        "state": "gathered", "config": config, "gather_subset": ["!all"],
        "gather_network_resources": [resource], "gather_configuration": False, "config_tree_detail": False,
    }, family_argspec(resource))
    facts, warnings = Facts(proxy).get_facts()
    warnings = list(warnings) + proxy.read_warnings
    resources = facts.get("ansible_network_resources") or {}
    if resource not in resources:
        raise _ReadFailed("unsupported_resource" if "unsupported_resource" in safe_warnings(warnings) else "missing")
    return resources[resource], warnings, getattr(proxy, "_isam_read_outcomes", None), family_spec(resource)


def _gather_operational(module, resource):
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts

    proxy = _ReadModule(module, {
        "gather_subset": ["!all", resource], "gather_network_resources": [],
        "gather_configuration": False, "config_tree_detail": False,
    })
    facts, warnings = Facts(proxy).get_facts()
    warnings = list(warnings) + proxy.read_warnings
    key = "ansible_net_%s" % resource
    if key not in facts:
        raise _ReadFailed("unsupported_resource" if "unsupported_resource" in safe_warnings(warnings) else "missing")
    return facts[key], warnings


def _outcome_records(read_outcomes):
    records = {}
    for record in (read_outcomes or {}).get("outcomes") or []:
        if isinstance(record, dict) and record.get("selector") is not None:
            records[record["selector"]] = record
    return records


def _error_category(exc):
    text = str(exc).lower()
    if "invalid token" in text or "not supported" in text or "unsupported_resource" in text:
        return "unsupported_resource"
    return "read_failed"


def read_one(module, read):
    """The result of one read request; never raises for a device or request problem."""
    result = dict(read) if isinstance(read, dict) else {"request": read}
    try:
        request = normalize(read)
    except ReadRequestError as exc:
        result.update({"status": "error", "error": "invalid_request", "error_detail": str(exc), "collected_at": _now()})
        return result
    result.update(request)
    ids = request["ids"]
    try:
        if request["kind"] == "operational":
            data, warnings = _gather_operational(module, request["resource"])
            outcomes, spec = None, None
        else:
            config = None
            if ids:
                fields = _identity_fields(request["resource"], request["section"])
                config = _nest(request["section"], [_entry(fields, identity) for identity in ids])
            data, warnings, outcomes, spec = _gather_config(module, request["resource"], config)
    except Exception as exc:  # each read is isolated: one failure never ends the others
        result.update({"status": "error", "error": _error_category(exc), "collected_at": _now(),
                       "unverified_ids": list(ids)})
        return result

    if data in (None, "", {}, []) and request["kind"] == "configuration":
        data = _empty(request["resource"])
    categories = safe_warnings(warnings)
    result.update({
        "status": "partial" if categories else "ok",
        "data": redact(data, spec),
        "returned_ids": [], "confirmed_absent_ids": [], "unverified_ids": [],
        "warnings": categories, "collected_at": _now(),
    })
    if ids:
        fields = _identity_fields(request["resource"], request["section"])
        found = set(_key(fields, item) for item in _section_items(data, request["section"])
                    if isinstance(item, dict) and all(item.get(name) not in (None, "") for name in fields))
        records = _outcome_records(outcomes)
        for identity in ids:
            key = _key(fields, _entry(fields, identity))
            if key in found:
                result["returned_ids"].append(identity)
            elif (records.get(key) or {}).get("existence") == "confirmed_absent":
                result["confirmed_absent_ids"].append(identity)
            else:
                result["unverified_ids"].append(identity)
        if outcomes and outcomes.get("parse"):
            result["parse"] = outcomes["parse"]
    return result


def read_all(module, reads):
    """The results of every read, in request order, and an overall status."""
    results = [read_one(module, read) for read in reads or []]
    statuses = set(item.get("status") for item in results)
    overall = "ok" if statuses <= {"ok"} else ("error" if statuses == {"error"} else "partial")
    return results, overall
