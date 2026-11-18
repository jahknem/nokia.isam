# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""isam_alarm config.

Removal forms in the ISAM CLI (help configure alarm ...):

* log-sev-level / delta-log: no removal form; left as they are on deleted
  and when omitted with overridden.
* entry (index): the alarm table always holds every alarm type; there is no
  ``no entry``. Only ``no severity`` resets to the (alarm type specific)
  default. ``no service-affecting|reporting|logging`` set the flag to false,
  which is not a reset to the default, so omitted flags are left untouched.
* filter (fltr-type, filterid): fixed table, no ``no filter``. ``no status``,
  ``no threshold`` and ``no window`` reset to the defaults; ``alarmid`` has no
  removal form (``all`` is what the device shows for unconfigured filters).
* suppression (filterid): no ``no suppression``. ``no status`` and
  ``no threshold`` reset; ``interface`` and ``alarmid`` have no removal form.
* custom-profile: ``configure alarm no custom-profile <name>``; attributes
  ``no mnemonicN`` etc.
* hgutr069-cust: ``configure alarm no hgutr069-cust <alarm-id>``.

Attributes without a removal form are never invented: the module warns and
leaves them on the device.
"""

from copy import deepcopy

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import IsamResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.alarm import (
    AlarmTemplate,
)


LOG_FIELDS = (
    ("log_sev_level", "log-sev-level"),
    ("log_full_action", "log-full-action"),
    ("non_itf_rep_sev_level", "non-itf-rep-sev-level"),
)
DELTA_LOG_FIELDS = (
    ("indet_log_full_action", "indet-log-full-action"),
    ("warn_log_full_action", "warn-log-full-action"),
    ("minor_log_full_action", "minor-log-full-action"),
    ("major_log_full_action", "major-log-full-action"),
    ("crit_log_full_act", "crit-log-full-act"),
)
ENTRY_FLAGS = (
    ("service_affecting", "service-affecting"),
    ("reporting", "reporting"),
    ("logging", "logging"),
)
FILTER_RESETTABLE = (("status", "status"), ("threshold", "threshold"), ("window", "window"))
SUPPRESSION_RESETTABLE = (("status", "status"), ("threshold", "threshold"))
FILTER_ALARMID_DEFAULT = "all"
PROFILE_FIELDS = tuple(
    (attr % i, attr % i)
    for i in range(1, 6)
    for attr in ("mnemonic%d", "description%d", "visible%d", "audible%d", "polarity%d", "severity%d")
)


def _quote(value):
    value = str(value)
    return '"%s"' % value if (not value or any(c.isspace() for c in value)) else value


def _cli_value(field, value):
    if isinstance(value, bool):
        return "enable" if value else "disable"
    if field.startswith("description"):
        return _quote(value)
    return str(value)


def _by_key(items, key):
    return dict((key(item), item) for item in (items or []))


class Alarm(IsamResourceModule):
    def __init__(self, module):
        super(Alarm, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="alarm",
            tmplt=AlarmTemplate(),
        )
        self.parsers = []

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    # ------------------------------------------------------------------ driver

    def generate_commands(self):
        want = deepcopy(self.want) or {}
        have = (deepcopy(self.have) or {}) if self.state != "rendered" else {}
        self._validate_suppressions(want)

        if self.state == "deleted":
            self._deleted(want, have)
            return

        self._compare_log("log", "configure alarm", LOG_FIELDS, want.get("log"), have.get("log"), whole=True)
        self._compare_list(want, have, "entries", lambda e: e["index"], self._entry)
        self._compare_list(want, have, "filters", lambda f: (f["fltr_type"], f["filterid"]), self._filter)
        self._compare_log("delta_log", "configure alarm delta-log", DELTA_LOG_FIELDS, want.get("delta_log"), have.get("delta_log"))
        self._compare_list(want, have, "custom_profiles", lambda p: p["name"], self._profile)
        self._compare_list(want, have, "hgutr069_custs", lambda c: c["alarm_id"], self._hgutr069)

    def _deleted(self, want, have):
        for section in ("log", "delta_log"):
            if want.get(section) and have.get(section):
                self._module.warn("alarm %s has no removal form in ISAM CLI; left unchanged" % section)
        for section, key, handler in (
            ("entries", lambda e: e["index"], self._entry),
            ("filters", lambda f: (f["fltr_type"], f["filterid"]), self._filter),
            ("custom_profiles", lambda p: p["name"], self._profile),
            ("hgutr069_custs", lambda c: c["alarm_id"], self._hgutr069),
        ):
            haved = _by_key(have.get(section), key)
            if want:
                if section not in want:
                    continue
                names = set(key(item) for item in want[section])
                haved = dict((k, v) for k, v in haved.items() if k in names)
            for item in haved.values():
                handler({}, item, remove=True)

    def _compare_list(self, want, have, section, key, handler):
        wantd = _by_key(want.get(section), key)
        haved = _by_key(have.get(section), key)
        for name, item in wantd.items():
            handler(item, haved.get(name, {}))
        if self.state == "overridden":
            for name, item in haved.items():
                if name not in wantd:
                    handler({}, item, remove=True)

    def _validate_suppressions(self, want):
        for fltr in want.get("filters") or []:
            for supp in fltr.get("suppressions") or []:
                if fltr["fltr_type"] != "temporal" or supp["filterid"] != fltr["filterid"]:
                    self._module.fail_json(
                        msg="alarm suppression filterid %s must be listed under the temporal filter with the same filterid"
                        % supp["filterid"]
                    )

    # ------------------------------------------------------------------ helpers

    def _changes(self, fields, want, have, reset):
        """CLI parts setting want's differing values, and 'no X' for reset fields omitted from want."""
        parts = []
        for field, cli in fields:
            value = want.get(field)
            if value is not None:
                if value != have.get(field):
                    parts.append("%s %s" % (cli, _cli_value(field, value)))
            elif field in reset and have.get(field) is not None and self.state in ("replaced", "overridden"):
                parts.append("no %s" % cli)
        return parts

    def _warn_unremovable(self, what, fields, have, defaults=None):
        defaults = defaults or {}
        kept = [f for f in fields if have.get(f) is not None and have.get(f) != defaults.get(f)]
        if kept:
            self._module.warn(
                "%s: %s has no removal form in ISAM CLI; left unchanged" % (what, ", ".join(kept))
            )

    # ------------------------------------------------------------------ sections

    def _compare_log(self, section, prefix, fields, want, have, whole=False):
        want = want or {}
        have = have or {}
        if not want or all(want.get(f) is None or want.get(f) == have.get(f) for f, _cli in fields):
            return
        if whole:
            # 'configure alarm log-sev-level .. log-full-action .. non-itf-rep-sev-level ..' is
            # one command; send every known value, want overriding have.
            merged = dict((f, want.get(f) if want.get(f) is not None else have.get(f)) for f, _cli in fields)
            parts = ["%s %s" % (cli, merged[f]) for f, cli in fields if merged[f] is not None]
        else:
            parts = self._changes(fields, want, have, ())
        self.commands.append("%s %s" % (prefix, " ".join(parts)))

    def _entry(self, want, have, remove=False):
        index = want.get("index") or have.get("index")
        if remove:
            parts = ["no severity"] if have.get("severity") else []
        else:
            parts = []
            if want.get("severity") is not None:
                if want["severity"] != have.get("severity"):
                    parts.append("severity %s" % want["severity"])
            elif have.get("severity") and self.state in ("replaced", "overridden"):
                parts.append("no severity")
            for field, cli in ENTRY_FLAGS:
                value = want.get(field)
                if value is not None and value != have.get(field):
                    parts.append(cli if value else "no %s" % cli)
        if parts:
            self.commands.append("configure alarm entry %s %s" % (index, " ".join(parts)))

    def _filter(self, want, have, remove=False):
        source = want or have
        fltr_type, filterid = source["fltr_type"], source["filterid"]
        prefix = "configure alarm filter %s filterid %s" % (fltr_type, filterid)
        if remove:
            parts = ["no %s" % cli for field, cli in FILTER_RESETTABLE if have.get(field) is not None]
            self._warn_unremovable(prefix, ["alarmid"], have, {"alarmid": FILTER_ALARMID_DEFAULT})
        else:
            parts = self._changes(
                (("alarmid", "alarmid"),) + FILTER_RESETTABLE, want, have, [f for f, _cli in FILTER_RESETTABLE]
            )
            if self.state in ("replaced", "overridden") and want.get("alarmid") is None:
                self._warn_unremovable(prefix, ["alarmid"], have, {"alarmid": FILTER_ALARMID_DEFAULT})
        if parts:
            self.commands.append("%s %s" % (prefix, " ".join(parts)))

        wanted = _by_key(want.get("suppressions"), lambda s: s["filterid"])
        haved = _by_key(have.get("suppressions"), lambda s: s["filterid"])
        for key, supp in wanted.items():
            self._suppression(supp, haved.get(key, {}))
        if remove or self.state in ("replaced", "overridden"):
            for key, supp in haved.items():
                if key not in wanted:
                    self._suppression({}, supp, remove=True)

    def _suppression(self, want, have, remove=False):
        filterid = (want or have)["filterid"]
        prefix = "configure alarm suppression filterid %s" % filterid
        if remove:
            parts = ["no %s" % cli for field, cli in SUPPRESSION_RESETTABLE if have.get(field) is not None]
            self._warn_unremovable(prefix, ["interface", "alarmid"], have)
        else:
            fields = (("interface", "interface"), ("alarmid", "alarmid")) + SUPPRESSION_RESETTABLE
            parts = self._changes(fields, want, have, [f for f, _cli in SUPPRESSION_RESETTABLE])
            if self.state in ("replaced", "overridden"):
                self._warn_unremovable(prefix, [f for f in ("interface", "alarmid") if want.get(f) is None], have)
        if parts:
            self.commands.append("%s %s" % (prefix, " ".join(parts)))

    def _profile(self, want, have, remove=False):
        name = want.get("name") or have.get("name")
        if remove:
            self.commands.append("configure alarm no custom-profile %s" % name)
            return
        parts = self._changes(PROFILE_FIELDS, want, have, [f for f, _cli in PROFILE_FIELDS])
        if parts or not have:
            self.commands.append(" ".join(["configure alarm custom-profile %s" % name] + parts))

    def _hgutr069(self, want, have, remove=False):
        alarm_id = want.get("alarm_id") or have.get("alarm_id")
        if remove:
            self.commands.append("configure alarm no hgutr069-cust %s" % alarm_id)
            return
        description = want.get("description")
        if description is None:
            if not have:
                self._module.fail_json(msg="alarm hgutr069-cust %s: description is mandatory in ISAM CLI" % alarm_id)
            return
        if description != have.get("description"):
            self.commands.append("configure alarm hgutr069-cust %s description %s" % (alarm_id, _quote(description)))
