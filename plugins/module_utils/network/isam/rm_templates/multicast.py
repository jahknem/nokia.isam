# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


_TOKEN = re.compile(r'"[^"]*"|\S+')

# CLI family -> resource key
FAMILIES = (("igmp", "igmp"), ("mcast-control", "mcast_control"))

# (CLI keyword, field, type) in device order; type "bool" is a [no] flag.
PACKAGE_FIELDS = (
    ("name", "name", "str"),
    ("template-name", "template_name", "str"),
    ("template-version", "template_version", "int"),
)

CDR_TYPE_FIELDS = (
    ("periodic", "periodic", "bool"),
    ("period", "period", "int"),
    ("attempt-max-pview", "attempt_max_pview", "bool"),
    ("attempt-blackout", "attempt_blackout", "bool"),
    ("attempt-no-perm", "attempt_no_perm", "bool"),
)


def _system_fields(mld):
    fields = [("src-ip-address", "src_ip_address", "str")]
    if mld:
        fields.append(("v6-src-ip-address", "v6_src_ip_address", "str"))
    fields += [
        ("verify-checksum", "verify_checksum", "bool"),
        ("query-interval", "query_interval", "int"),
        ("max-rsp-time", "max_rsp_time", "int"),
        ("robustness", "robustness", "int"),
        ("mem-query-int", "mem_query_int", "int"),
        ("last-memb-cnt", "last_memb_cnt", "int"),
        ("last-max-resp-tim", "last_max_resp_tim", "int"),
        ("host-report-intv", "host_report_intv", "int"),
        ("start", "start", "bool"),
        ("preview-valid", "preview_valid", "int"),
        ("cdr-validation", "cdr_validation", "str"),
        ("cdr-generation", "cdr_generation", "bool"),
        ("except-cdr-rate", "except_cdr_rate", "int"),
        ("cdr-export", "cdr_export", "str"),
        ("cdr-file-aging", "cdr_file_aging", "int"),
        ("cdr-polling", "cdr_polling", "int"),
        ("user-igmp-version", "user_igmp_version", "str"),
        ("netw-igmp-version", "netw_igmp_version", "str"),
    ]
    if mld:
        fields += [
            ("user-mld-version", "user_mld_version", "str"),
            ("netw-mld-version", "netw_mld_version", "str"),
        ]
    fields += [
        ("v3-max-num-rec", "v3_max_num_rec", "int"),
        ("forking", "forking", "bool"),
        ("lt-ont-signaling", "lt_ont_signaling", "bool"),
        ("vlan-selection", "vlan_selection", "bool"),
        ("disc-lwr-version", "disc_lwr_version", "bool"),
        ("uncfg-mcast-supp", "uncfg_mcast_supp", "str"),
    ]
    return tuple(fields)


SYSTEM_FIELDS = {"igmp": _system_fields(False), "mcast_control": _system_fields(True)}

_PACKAGE = re.compile(r"^configure\s(?P<family>igmp|mcast-control)\spackage\s(?P<index>\d+)(?:\s(?P<rest>.*))?$")
_CDR_TYPE = re.compile(r"^configure\s(?P<family>igmp|mcast-control)\ssystem\scdr-type(?:\s(?P<rest>.*))?$")
_SYSTEM = re.compile(r"^configure\s(?P<family>igmp|mcast-control)\ssystem(?:\s(?P<rest>(?!cdr-type(?:\s|$)).*))?$")


def _unquote(value):
    return value[1:-1] if len(value) >= 2 and value.startswith('"') and value.endswith('"') else value


def _quote(value):
    value = str(value)
    return '"%s"' % value if not value or re.search(r"\s", value) else value


def parse_attributes(rest, fields):
    """Attribute tokens of one line -> (entry, leftover tokens).

    ``no <value field>`` is the default (absent), ``[no] <flag>`` is False/True.
    """
    by_cli = dict((cli, (key, kind)) for cli, key, kind in fields)
    tokens = _TOKEN.findall(rest or "")
    entry, leftover, i = {}, [], 0
    while i < len(tokens):
        negate = tokens[i] == "no" and i + 1 < len(tokens) and tokens[i + 1] in by_cli
        cli = tokens[i + 1] if negate else tokens[i]
        if cli not in by_cli:
            leftover.append(tokens[i])
            i += 1
            continue
        key, kind = by_cli[cli]
        i += 2 if negate else 1
        if kind == "bool":
            entry[key] = not negate
        elif negate:
            entry.pop(key, None)
        elif i < len(tokens):
            value = _unquote(tokens[i])
            entry[key] = int(value) if kind == "int" and value.isdigit() else value
            i += 1
        else:
            leftover.append(cli)
    return entry, leftover


def parse_line(line):
    """One package/system line -> (resource key, section, index, entry, leftover), or None."""
    for regex, section in ((_PACKAGE, "packages"), (_CDR_TYPE, "cdr_type"), (_SYSTEM, "system")):
        match = regex.match(line)
        if not match:
            continue
        family = "igmp" if match.group("family") == "igmp" else "mcast_control"
        fields = PACKAGE_FIELDS if section == "packages" else CDR_TYPE_FIELDS if section == "cdr_type" else SYSTEM_FIELDS[family]
        entry, leftover = parse_attributes(match.group("rest"), fields)
        index = int(match.group("index")) if section == "packages" else None
        return family, section, index, entry, leftover
    return None


def render_attributes(fields, want, have, reset):
    """Attribute words setting want (where it differs from have) and resetting ``reset`` keys."""
    words = []
    for cli, key, kind in fields:
        if want.get(key) is not None:
            value = want[key]
            current = have.get(key)
            if kind == "bool":
                if bool(value) != bool(current):
                    words.append(cli if value else "no " + cli)
            elif current is None or str(value) != str(current):
                words.append("%s %s" % (cli, _quote(value)))
        elif key in reset:
            if kind == "bool":
                if have.get(key):
                    words.append("no " + cli)
            elif have.get(key) is not None:
                words.append("no " + cli)
    return words


def cli_family(resource):
    return "igmp" if resource == "igmp" else "mcast-control"


class MulticastTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(MulticastTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    def parse(self):
        """Regex parsers for the context selectors, a token parser for package/system lines.

        Packages with only default values (``no name no template-name no template-version``
        in ``detail`` output) are not returned: the 1024 package slots always exist.
        """
        result = super(MulticastTemplate, self).parse()
        packages = {}
        for raw in self._lines:
            parsed = parse_line(raw.strip())
            if parsed is None:
                continue
            family, section, index, entry, leftover = parsed
            if section == "packages":
                packages.setdefault(family, {}).setdefault(index, {}).update(entry)
            elif not entry:
                continue
            elif section == "cdr_type":
                result.setdefault(family, {}).setdefault("system", {}).setdefault("cdr_type", {}).update(entry)
            else:
                result.setdefault(family, {}).setdefault("system", {}).update(entry)
        for family, by_index in packages.items():
            entries = [dict(entry, index=index) for index, entry in sorted(by_index.items()) if entry]
            if entries:
                result.setdefault(family, {})["packages"] = entries
        return result

    # fmt: off
    PARSERS = [
        {
            # Claims package/system lines for the unmatched-line tracker; parse() reads them.
            "name": "package_system",
            "getval": re.compile(r"^configure\s(?:igmp|mcast-control)\s(?:package\s\d+|system)(?:\s.*)?$"),
            "setval": "",
            "result": {},
        },
        {
            "name": "igmp.mcast_svc_context",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<mcast_svc_context>\S+)$"
            ),
            "setval": "configure igmp mcast-svc-context {{ igmp.mcast_svc_context }}",
            "result": {
                "igmp": {
                    "mcast_svc_context": "{{ mcast_svc_context }}",
                },
            },
        },
        {
            "name": "igmp.mld_snooping",
            "compval": "mld_snooping",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<mld_snooping>mld-snooping)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.mld_snooping == false else '' }}mld-snooping",
            "result": {
                "igmp": {
                    "mld_snooping": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.mld_querier",
            "compval": "mld_querier",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<mld_querier>mld-querier)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.mld_querier == false else '' }}mld-querier",
            "result": {
                "igmp": {
                    "mld_querier": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.igmp_snooping",
            "compval": "igmp_snooping",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<igmp_snooping>igmp-snooping)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.igmp_snooping == false else '' }}igmp-snooping",
            "result": {
                "igmp": {
                    "igmp_snooping": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.igmp_querier",
            "compval": "igmp_querier",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\s(?P<negate>no\s)?(?P<igmp_querier>igmp-querier)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context {{ 'no ' if igmp.igmp_querier == false else '' }}igmp-querier",
            "result": {
                "igmp": {
                    "igmp_querier": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "igmp.query_interval",
            "compval": "query_interval",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\squery-interval\s(?P<query_interval>\d+)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context query-interval {{ igmp.query_interval }}",
            "result": {
                "igmp": {
                    "query_interval": "{{ query_interval|int }}",
                },
            },
        },
        {
            "name": "igmp.query_response_interval",
            "compval": "query_response_interval",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\squery-response-interval\s(?P<query_response_interval>\d+)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context query-response-interval {{ igmp.query_response_interval }}",
            "result": {
                "igmp": {
                    "query_response_interval": "{{ query_response_interval|int }}",
                },
            },
        },
        {
            "name": "igmp.robustness_count",
            "compval": "robustness_count",
            "getval": re.compile(
                r"^configure\sigmp\smcast-svc-context\srobustness-count\s(?P<robustness_count>\d+)(?:\s+.*)?$"
            ),
            "setval": "configure igmp mcast-svc-context robustness-count {{ igmp.robustness_count }}",
            "result": {
                "igmp": {
                    "robustness_count": "{{ robustness_count|int }}",
                },
            },
        },
        {
            "name": "mcast_control.mcast_svc_context",
            "getval": re.compile(
                r"^configure\smcast-control\smcast-svc-context\s(?P<mcast_svc_context>\S+)$"
            ),
            "setval": "configure mcast-control mcast-svc-context {{ mcast_control.mcast_svc_context }}",
            "result": {
                "mcast_control": {
                    "mcast_svc_context": "{{ mcast_svc_context }}",
                },
            },
        },
        {
            "name": "mcast_control.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\smcast-control\s(?P<negate>no\s)?(?P<admin_state>admin-state)(?:\s+.*)?$"
            ),
            "setval": "configure mcast-control {{ 'no ' if mcast_control.admin_state == false else '' }}admin-state",
            "result": {
                "mcast_control": {
                    "admin_state": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "mcast_control.max_groups",
            "compval": "max_groups",
            "getval": re.compile(
                r"^configure\smcast-control\smax-groups\s(?P<max_groups>\d+)(?:\s+.*)?$"
            ),
            "setval": "configure mcast-control max-groups {{ mcast_control.max_groups }}",
            "result": {
                "mcast_control": {
                    "max_groups": "{{ max_groups|int }}",
                },
            },
        },
        {
            "name": "mcast_control.max_sources",
            "compval": "max_sources",
            "getval": re.compile(
                r"^configure\smcast-control\smax-sources\s(?P<max_sources>\d+)(?:\s+.*)?$"
            ),
            "setval": "configure mcast-control max-sources {{ mcast_control.max_sources }}",
            "result": {
                "mcast_control": {
                    "max_sources": "{{ max_sources|int }}",
                },
            },
        },
    ]
    # fmt: on
