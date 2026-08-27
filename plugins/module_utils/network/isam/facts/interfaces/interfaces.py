# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
 The isam interfaces fact class
 It is in this file the configuration is collected from the device
 for a given resource, parsed, and the facts tree is populated
 based on the configuration.
"""

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import (
    utils,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.interfaces import (
    InterfacesTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.interfaces.interfaces import (
    InterfacesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    normalize_resource_keys,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_scoped_config,
    unwrap_response,
)


class InterfacesFacts(object):
    """ The isam interfaces facts class
    """

    # Attributes the device may compact onto a single "port <id> ..." line,
    # e.g. "port uni:1/1/5/1/19/1/1 admin-up user Y654321". admin-up and
    # link-updown-trap are bare flags; user/severity/port-type take a value.
    _PACKED_WORDS = {"admin-up", "link-updown-trap", "user", "severity", "port-type"}
    # Matches a double-quoted span (kept intact, quotes included) or a
    # single non-whitespace run, so quoted values (including an explicit
    # empty value like `user ""`) survive re-splitting unchanged.
    _TOKEN_RE = re.compile(r'"[^"]*"|\S+')

    def __init__(self, module, subspec='config', options='options'):
        self._module = module
        self.argument_spec = InterfacesArgs.argument_spec

    @classmethod
    def _split_packed_line(cls, line):
        """Split a compacted "port <id> attr1 [val1] attr2 [val2] ..." line
        into one "port <id> attr [val]" line per attribute so the existing
        per-attribute regex parsers in rm_templates/interfaces.py can match
        each one. Live devices always compact simultaneously-set interface
        attributes onto one line; without this the generic regex parsers
        (which each expect exactly one attribute per line) silently match
        nothing and facts gathering returns empty/incomplete data.
        """
        tokens = cls._TOKEN_RE.findall(line)
        if len(tokens) < 3 or tokens[0] != "port":
            return [line]
        starts = [
            index for index, token in enumerate(tokens[2:], 2)
            if (token in cls._PACKED_WORDS and (index == 2 or tokens[index - 1] != "no"))
            or (token == "no" and index + 1 < len(tokens) and tokens[index + 1] in cls._PACKED_WORDS)
        ]
        if not starts:
            return [line]
        prefix = " ".join(tokens[:2])
        return [
            prefix + " " + " ".join(tokens[start:end])
            for start, end in zip(starts, starts[1:] + [len(tokens)])
        ]

    @staticmethod
    def _canonicalize_entry(item):
        entry = normalize_resource_keys(item, aliases=(("id", "name"),))

        entry.pop("id", None)
        entry.pop("admin-up", None)
        entry.pop("link-updown-trap", None)
        entry.pop("port-type", None)
        return entry

    def get_config(self, connection):
        config = self._module.params.get("config") or []
        commands = [
            "info configure interface port %s detail flat" % item["name"]
            for item in config
        ]
        return get_scoped_config(
            self._module,
            connection,
            config,
            "info configure interface port flat",
            commands,
        )

    def populate_facts(self, connection, ansible_facts, data=None):
        """ Populate the facts for Interfaces network resource

        :param connection: the device connection
        :param ansible_facts: Facts dictionary
        :param data: previously collected conf

        :rtype: dictionary
        :returns: facts
        """
        facts = {}
        objs = []

        if not data:
            data = self.get_config(connection)
        data = unwrap_response(data)

        # parse native config using the Interfaces template
        # the template 'getval' regexes expect lines starting with 'port ...'
        # but the device output contains 'configure interface port ...'
        # so strip the leading prefix and ignore non-config lines
        raw_lines = []
        for line in str(data or "").splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('configure interface port '):
                stripped = line.replace('configure interface ', '', 1)
                raw_lines.extend(self._split_packed_line(stripped))

        interfaces_parser = InterfacesTemplate(lines=raw_lines, module=self._module)
        parsed = interfaces_parser.parse()
        valued = parsed.values()
        objs = list(valued)

        objs = [self._canonicalize_entry(item) for item in objs]

        ansible_facts['ansible_network_resources'].pop('interfaces', None)

        params = utils.remove_empties(
            interfaces_parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
        ) or {}
        validated = params.get('config') or []
        facts['interfaces'] = [self._canonicalize_entry(item) for item in validated]
        ansible_facts['ansible_network_resources'].update(facts)

        return ansible_facts
