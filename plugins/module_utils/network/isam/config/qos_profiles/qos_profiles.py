# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.utils.utils import dict_merge
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import Facts
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)


class Qos_profiles(IsamResourceModule):
    """The isam_qos_profiles config class."""

    # Fields the device refuses to change on an existing profile -> their default
    # (lab ISAM: "QOS MGT error 2 : changing type is not allowed").
    IMMUTABLE = {"shaper": {"shaper-type": "singletokenbucket"}}

    def __init__(self, module):
        super(Qos_profiles, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="qos_profiles",
            tmplt=Qos_profilesTemplate(),
        )
        self.parsers = list(Qos_profilesTemplate._FIELDS)

    @staticmethod
    def _key(entry):
        return "{0}:{1}".format(entry["profile_type"], entry["name"])

    def generate_commands(self):
        wantd = {self._key(entry): entry for entry in self.want}
        haved = {self._key(entry): entry for entry in self.have}

        if self.state == "merged":
            wantd = dict_merge(haved, wantd)

        if self.state == "deleted":
            haved = {k: v for k, v in iteritems(haved) if k in wantd or not wantd}
            wantd = {}

        if self.state in ["overridden", "deleted"]:
            for key, have in iteritems(deepcopy(haved)):
                if key not in wantd:
                    self._compare(want={}, have=have)

        for key, want in iteritems(wantd):
            self._compare(want=want, have=haved.pop(key, {}))
        self.commands = list(dict.fromkeys(self.commands))

    def _compare(self, want, have):
        if not want:
            # "configure qos profiles no <type> <name>" removes the profile with all
            # its parameters; per-parameter removals after it would be invalid.
            self.compare(parsers=["profile_type"], want=want, have=have)
            return
        self._check_immutable(want, have)
        before = len(self.commands)
        self.compare(parsers=self.parsers, want=want, have=have)
        self._pack(before, want, have)

    def _check_immutable(self, want, have):
        """Fail before sending a change the device refuses for an existing profile."""
        if not have:
            return
        for field, default in self.IMMUTABLE.get(want.get("profile_type"), {}).items():
            wanted = want.get(field)
            if wanted is not None and wanted != (have.get(field) or default):
                self._module.fail_json(msg=(
                    "qos profile %s %s: %s cannot be changed on an existing profile; "
                    "delete the profile and create it again" % (want["profile_type"], want["name"], field)))

    def _pack(self, before, want, have):
        """One command per profile: '<path> <mandatory params> <changes>'.

        The device validates a profile command as a whole, and some parameters depend
        on each other (a shaper's excess-info-rate is only valid with a two-rate type).
        Sent as separate commands -- excess-info-rate before type -- the device rejected
        the first one. The packed line is also the form the device prints.
        """
        path = "configure qos profiles " + Qos_profilesTemplate._profile_path(want)
        new = self.commands[before:]
        mine = [c for c in new if c == path or c.startswith(path + " ")]
        if not mine:
            return
        data = dict(have)
        data.update(want)
        # The profile line carries the mandatory parameters with the desired value
        # (want over have); a per-field command for one of them must not repeat the
        # keyword. Each per-field command is '<kw> [<value>]' or 'no <kw>'.
        inline = set(field for field in Qos_profilesTemplate._INLINE_ORDER.get(data.get("profile_type"), ())
                     if data.get(field) is not None)
        parts = []
        line = Qos_profilesTemplate._render_profile_line(data)[len(path):].strip()
        if line:
            parts.append(line)
        for command in mine:
            part = command[len(path):].strip()
            tokens = part.split()
            keyword = tokens[1] if tokens[:1] == ["no"] and len(tokens) > 1 else (tokens or [None])[0]
            if part and keyword not in inline and part not in parts:
                parts.append(part)
        others = [c for c in new if c not in mine]
        self.commands[before:] = others + [" ".join([path] + parts)]
