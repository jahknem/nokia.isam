# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.multicast import (
    CDR_TYPE_FIELDS,
    PACKAGE_FIELDS,
    SYSTEM_FIELDS,
    MulticastTemplate,
    cli_family,
    render_attributes,
)

# Settings blocks and instance lists handled by package_system_commands, not the parsers.
BLOCK_KEYS = ("system", "packages")


def names_blocks(want):
    """True when config names packages or system settings (then deleted only resets those)."""
    return any((want or {}).get(key) for key in BLOCK_KEYS)


def strip_blocks(data):
    return dict((key, value) for key, value in (data or {}).items() if key not in BLOCK_KEYS)


def _keys(fields):
    return set(key for _cli, key, _kind in fields)


def _system_commands(resource, want, have, reset_all):
    """configure <family> system [cdr-type] lines; reset_all resets keys missing from want."""
    prefix = "configure %s system" % cli_family(resource)
    fields = SYSTEM_FIELDS[resource]
    commands = []
    words = render_attributes(fields, want, have, _keys(fields) if reset_all else ())
    if words:
        commands.append("%s %s" % (prefix, " ".join(words)))
    want_cdr, have_cdr = want.get("cdr_type") or {}, have.get("cdr_type") or {}
    words = render_attributes(CDR_TYPE_FIELDS, want_cdr, have_cdr, _keys(CDR_TYPE_FIELDS) if reset_all else ())
    if words:
        commands.append("%s cdr-type %s" % (prefix, " ".join(words)))
    return commands


def _package_command(resource, index, want, have, reset_all):
    words = render_attributes(PACKAGE_FIELDS, want, have, _keys(PACKAGE_FIELDS) if reset_all else ())
    if not words:
        return []
    return ["configure %s package %s %s" % (cli_family(resource), index, " ".join(words))]


def package_system_commands(state, resource, want, have, targeted=None):
    """Commands for the system settings and package list of one family (igmp / mcast_control).

    merged: set what config gives. replaced: system (when given) and each listed package
    are replaced. overridden: also omitted system and unlisted packages are reset.
    deleted: the listed packages / given system are reset, or all when config names none
    (``targeted``: whether the config names any; defaults to this family's config).
    Packages are fixed slots (1..1024): reset means "no name no template-name no template-version".
    """
    want, have = want or {}, have or {}
    want_sys, have_sys = want.get("system"), have.get("system") or {}
    have_pkgs = dict((p["index"], p) for p in have.get("packages") or [] if p.get("index") is not None)
    want_pkgs = [p for p in want.get("packages") or [] if p.get("index") is not None]
    commands = []

    if state == "deleted":
        targeted = names_blocks(want) if targeted is None else targeted
        if not targeted or want_sys:
            commands += _system_commands(resource, {}, have_sys, True)
        indexes = [p["index"] for p in want_pkgs] if targeted else sorted(have_pkgs)
        for index in indexes:
            commands += _package_command(resource, index, {}, have_pkgs.get(index) or {}, True)
        return commands

    replace = state in ("replaced", "overridden")
    if want_sys is not None or state == "overridden":
        commands += _system_commands(resource, want_sys or {}, have_sys, replace)
    listed = set()
    for pkg in want_pkgs:
        listed.add(pkg["index"])
        commands += _package_command(resource, pkg["index"], pkg, have_pkgs.get(pkg["index"]) or {}, replace)
    if state == "overridden":
        for index in sorted(set(have_pkgs) - listed):
            commands += _package_command(resource, index, {}, have_pkgs[index], True)
    return commands


class Multicast(IsamResourceModule):
    """The isam_multicast config class."""

    def __init__(self, module):
        super(Multicast, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="multicast",
            tmplt=MulticastTemplate(),
        )
        self.parsers = [
            "igmp.mld_snooping",
            "igmp.mld_querier",
            "igmp.igmp_snooping",
            "igmp.igmp_querier",
            "igmp.query_interval",
            "igmp.query_response_interval",
            "igmp.robustness_count",
            "mcast_control.admin_state",
            "mcast_control.max_groups",
            "mcast_control.max_sources",
        ]

    def generate_commands(self):
        raw_want, raw_have = self.want or {}, self.have or {}
        targeted = any(names_blocks(raw_want.get(r)) for r in ("igmp", "mcast_control"))
        for resource in ("igmp", "mcast_control"):
            self.commands.extend(package_system_commands(
                self.state, resource, raw_want.get(resource), raw_have.get(resource), targeted))
        if self.state == "deleted" and targeted:
            return

        want = self._normalize(dict((r, strip_blocks(v)) for r, v in raw_want.items() if r in ("igmp", "mcast_control")))
        have = self._normalize(dict((r, strip_blocks(v)) for r, v in raw_have.items() if r in ("igmp", "mcast_control")))

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted":
            want = {}

        self._compare_igmp(want.get("igmp", {}), have.get("igmp", {}))
        self._compare_mcast_control(want.get("mcast_control", {}), have.get("mcast_control", {}))

    def _compare_igmp(self, want, have):
        if self.state in ["overridden", "replaced", "deleted"]:
            for key, negate_val in [("mld_snooping", False), ("mld_querier", False),
                                     ("igmp_snooping", False), ("igmp_querier", False)]:
                if key not in want and have.get(key) is True:
                    self.addcmd({"igmp": {key: negate_val}}, "igmp." + key)

        for key in ("mld_snooping", "mld_querier", "igmp_snooping", "igmp_querier",
                     "query_interval", "query_response_interval", "robustness_count"):
            if key in want and want.get(key) != have.get(key):
                self.addcmd({"igmp": {key: want.get(key)}}, "igmp." + key)

    def _compare_mcast_control(self, want, have):
        if self.state in ["overridden", "replaced", "deleted"]:
            if "admin_state" not in want and have.get("admin_state") is True:
                self.addcmd({"mcast_control": {"admin_state": False}}, "mcast_control.admin_state")

        for key in ("admin_state", "max_groups", "max_sources"):
            if key in want and want.get(key) != have.get(key):
                self.addcmd({"mcast_control": {key: want.get(key)}}, "mcast_control." + key)

    def _normalize(self, data):
        if not data:
            return {}
        normalized = dict(data)
        if normalized.get("igmp"):
            normalized["igmp"] = dict(normalized["igmp"])
        if normalized.get("mcast_control"):
            normalized["mcast_control"] = dict(normalized["mcast_control"])
        return normalized
