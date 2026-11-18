#
# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam_ethernet_line config file.
It is in this file where the current configuration (as dict)
is compared to the provided configuration (as dict) and the command set
necessary to bring the current configuration to its desired end-state is
created.
"""

from ansible.module_utils.six import iteritems
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.ethernet_line import (
    LINE_PARSERS,
    MAU_PARSERS,
    TCA_PARSERS,
    Ethernet_lineTemplate,
)

# Device defaults (CLI guide, lab ISAM 'flat detail'): a value at its default equals an
# unset one. port-type and the MAU type/power have no "no" form; they are only set.
LINE_DEFAULTS = {"admin_up": False}
TCA_DEFAULTS = {"enable": False, "los": 0, "fcs": 0, "rx_octets": 0, "tx_octets": 0,
                "los_day": 0, "fcs_day": 0, "rx_octets_day": 0, "tx_octets_day": 0}
MAU_DEFAULTS = {"speed_auto_sense": False, "autonegotiate": False, "cap100base_tfd": False,
                "cap1000base_xfd": False, "cap1000base_tfd": False}
SET_ONLY = ("port_type", "mau_type", "power")


def _without_defaults(entry, defaults):
    return dict((key, value) for key, value in iteritems(entry or {})
                if value is not None and not (key in defaults and value == defaults[key]))


class Ethernet_line(IsamResourceModule):
    """
    The isam_ethernet_line config class
    """

    COMPACT_COMMAND_SCOPES = (
        r"^(?P<scope>configure ethernet line \S+) (?P<suffix>(?!tca-line-threshold(?:\s|$)|mau(?:\s|$)).+)$",
        r"^(?P<scope>configure ethernet line \S+ tca-line-threshold) (?P<suffix>.+)$",
        r"^(?P<scope>configure ethernet line \S+ mau \S+) (?P<suffix>.+)$",
    )

    def __init__(self, module):
        super(Ethernet_line, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="ethernet_line",
            tmplt=Ethernet_lineTemplate(),
        )
        self.line_parsers = [parser["name"] for parser in LINE_PARSERS + TCA_PARSERS]
        self.mau_parsers = [parser["name"] for parser in MAU_PARSERS]

    def execute_module(self):
        """ Execute the module
        :rtype: A dictionary
        :returns: The result from module execution
        """
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def generate_commands(self):
        """ Generate configuration commands to send based on
            want, have and desired state.
        """
        wantd = dict((entry["if_index"], entry) for entry in self.want or [])
        haved = dict((entry["if_index"], entry) for entry in self.have or [])

        if self.state == "deleted":
            for if_index, have in iteritems(haved):
                if not wantd or if_index in wantd:
                    self._compare(self._deleted_target(wantd.get(if_index) or {}, have), have)
            return
        if self.state == "overridden":
            for if_index, have in iteritems(haved):
                if if_index not in wantd:
                    self._compare({"if_index": if_index}, have)
        for if_index, want in iteritems(wantd):
            have = haved.get(if_index, {})
            self._compare(self._merge(have, want) if self.state == "merged" else want, have)

    @staticmethod
    def _merge(have, want):
        """merged: want onto have; MAU entries merged by index."""
        merged = dict(have, **dict((k, v) for k, v in iteritems(want) if v is not None and k not in ("mau", "tca_line_threshold")))
        merged["tca_line_threshold"] = dict(have.get("tca_line_threshold") or {},
                                            **_without_defaults(want.get("tca_line_threshold"), {}))
        maus = dict((entry["index"], dict(entry)) for entry in have.get("mau") or [])
        for entry in want.get("mau") or []:
            maus[entry["index"]] = dict(maus.get(entry["index"], {}), **_without_defaults(entry, {}))
        merged["mau"] = list(maus.values())
        return merged

    @staticmethod
    def _deleted_target(want, have):
        """deleted: an identity alone resets the line; named settings reset only those."""
        named = [key for key, value in iteritems(want) if key != "if_index" and value not in (None, {}, [])]
        if not named:
            return {"if_index": have["if_index"]}
        target = dict((key, value) for key, value in iteritems(have) if key not in named)
        if "tca_line_threshold" in named:
            named_tca = [key for key, value in iteritems(want["tca_line_threshold"]) if value is not None]
            target["tca_line_threshold"] = dict((key, value) for key, value in iteritems(have.get("tca_line_threshold") or {})
                                                if named_tca and key not in named_tca)
        if "mau" in named:
            # per MAU: an index alone resets that MAU, named fields reset only themselves
            requested = dict((entry["index"], entry) for entry in want["mau"])
            target["mau"] = []
            for entry in have.get("mau") or []:
                ask = requested.get(entry["index"])
                if ask is None:
                    target["mau"].append(entry)
                    continue
                fields = [key for key, value in iteritems(ask) if key != "index" and value is not None]
                if fields:
                    target["mau"].append(dict((key, value) for key, value in iteritems(entry) if key not in fields))
        return target

    def _compare(self, want, have):
        """The line with its TCA thresholds, then each MAU. Defaults equal unset values;
        set-only attributes the request does not name are kept."""
        if_index = want.get("if_index") or have["if_index"]
        rendering = self.state == "rendered"
        self.compare(parsers=self.line_parsers, want=self._line(want, have, rendering), have=self._line(have, {}, rendering))
        want_mau = dict((entry["index"], entry) for entry in want.get("mau") or [])
        have_mau = dict((entry["index"], entry) for entry in have.get("mau") or [])
        for index in list(want_mau) + [index for index in have_mau if index not in want_mau]:
            base = {"if_index": if_index, "index": index}
            wanted = dict(base, **want_mau.get(index, {}))
            current = dict(base, **have_mau.get(index, {}))
            for key in SET_ONLY:
                if wanted.get(key) is None and current.get(key) is not None:
                    wanted[key] = current[key]
            if not rendering:
                wanted, current = (dict(base, **_without_defaults(entry, MAU_DEFAULTS)) for entry in (wanted, current))
            self.compare(parsers=self.mau_parsers, want=wanted, have=current)

    @staticmethod
    def _line(entry, keep_from, rendering):
        line = dict((key, value) for key, value in iteritems(entry) if key != "mau")
        line["if_index"] = entry.get("if_index") or keep_from.get("if_index")
        if line.get("port_type") is None and keep_from.get("port_type") is not None:
            line["port_type"] = keep_from["port_type"]
        if rendering:
            return line
        tca = _without_defaults(line.pop("tca_line_threshold", None), TCA_DEFAULTS)
        line = dict(_without_defaults(line, LINE_DEFAULTS), if_index=line["if_index"])
        if tca:
            line["tca_line_threshold"] = tca
        return line
