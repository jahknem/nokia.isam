# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


def _custom_profile_getval():
    """'configure alarm custom-profile <name> [mnemonicN ..] [descriptionN ..] ...' in CLI syntax order."""
    fields = []
    for i in range(1, 6):
        fields.append(r"(?:\smnemonic%d\s(?P<mnemonic%d>\S+))?" % (i, i))
        fields.append(r'(?:\sdescription%d\s(?:"(?P<qdescription%d>[^"]*)"|(?P<description%d>\S+)))?' % (i, i, i))
        fields.append(r"(?:\svisible%d\s(?P<visible%d>enable|disable))?" % (i, i))
        fields.append(r"(?:\saudible%d\s(?P<audible%d>enable|disable))?" % (i, i))
        fields.append(r"(?:\spolarity%d\s(?P<polarity%d>\S+))?" % (i, i))
        fields.append(r"(?:\sseverity%d\s(?P<severity%d>\S+))?" % (i, i))
    return re.compile(r"configure\salarm\scustom-profile\s(?P<name>\S+)" + "".join(fields) + r"\s*$")


def _custom_profile_result():
    profile = {"name": "{{ name }}"}
    for i in range(1, 6):
        profile["mnemonic%d" % i] = "{{ mnemonic%d }}" % i
        profile["description%d" % i] = "{{ description%d if description%d is defined else qdescription%d | default(None) }}" % (i, i, i)
        profile["visible%d" % i] = "{{ (visible%d == 'enable') if visible%d is defined else None }}" % (i, i)
        profile["audible%d" % i] = "{{ (audible%d == 'enable') if audible%d is defined else None }}" % (i, i)
        profile["polarity%d" % i] = "{{ polarity%d }}" % i
        profile["severity%d" % i] = "{{ severity%d }}" % i
    return {"custom_profiles": {"{{ name }}": profile}}


class AlarmTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(AlarmTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "log_sev_level",
            "getval": re.compile(
                r"configure\salarm(?=\slog-sev-level|\slog-full-action|\snon-itf-rep-sev-level)"
                r"(?:\slog-sev-level\s(?P<log_sev_level>\S+))?"
                r"(?:\slog-full-action\s(?P<log_full_action>\S+))?"
                r"(?:\snon-itf-rep-sev-level\s(?P<non_itf_rep_sev_level>\S+))?\s*$",
            ),
            "setval": "configure alarm log-sev-level {{ log_sev_level }} log-full-action {{ log_full_action }} non-itf-rep-sev-level {{ non_itf_rep_sev_level }}",
            "result": {
                "log": {
                    "log_sev_level": "{{ log_sev_level }}",
                    "log_full_action": "{{ log_full_action }}",
                    "non_itf_rep_sev_level": "{{ non_itf_rep_sev_level }}",
                }
            },
        },
        {
            "name": "entry",
            # One line per entry with all attributes ('info configure alarm flat'),
            # e.g. 'configure alarm entry door severity critical service-affecting
            # reporting logging'; every attribute is optional, in CLI order, so a
            # line carrying a single attribute parses as well.
            "getval": re.compile(
                r"configure\salarm\sentry\s(?P<index>\S+)"
                r"(?:\s(?:(?P<no_severity>no\sseverity)|severity\s(?P<severity>\S+)))?"
                r"(?:\s(?P<service_affecting>(?:no\s)?service-affecting))?"
                r"(?:\s(?P<reporting>(?:no\s)?reporting))?"
                r"(?:\s(?P<logging>(?:no\s)?logging))?"
                r"\s*$"
            ),
            "setval": "configure alarm entry {{ index }}",
            "result": {
                "entries": {
                    "{{ index }}": {
                        "index": "{{ index }}",
                        # 'no severity' is the device default (alarm type specific): not set.
                        "severity": "{{ severity }}",
                        "service_affecting": "{{ (service_affecting == 'service-affecting') if service_affecting is defined else None }}",
                        "reporting": "{{ (reporting == 'reporting') if reporting is defined else None }}",
                        "logging": "{{ (logging == 'logging') if logging is defined else None }}",
                    }
                }
            },
        },
        {
            "name": "filter",
            "getval": re.compile(
                r"configure\salarm\sfilter\s(?P<fltr_type>temporal|spatial)\sfilterid\s(?P<filterid>\d+)"
                r"(?:\salarmid\s(?P<alarmid>\S+))?"
                r"(?:\s(?:(?P<no_status>no\sstatus)|status\s(?P<status>\S+)))?"
                r"(?:\s(?:(?P<no_threshold>no\sthreshold)|threshold\s(?P<threshold>\d+)))?"
                r"(?:\s(?:(?P<no_window>no\swindow)|window\s(?P<window>\d+)))?"
                r"\s*$"
            ),
            "setval": "configure alarm filter {{ fltr_type }} filterid {{ filterid }}",
            "result": {
                "filters": {
                    "{{ fltr_type }}/{{ filterid }}": {
                        "fltr_type": "{{ fltr_type }}",
                        "filterid": "{{ filterid }}",
                        "alarmid": "{{ alarmid }}",
                        # 'no <attr>' resets to the CLI help default.
                        "status": "{{ 'not-used' if no_status is defined else status }}",
                        "threshold": "{{ '2' if no_threshold is defined else threshold }}",
                        "window": "{{ '60' if no_window is defined else window }}",
                    }
                }
            },
        },
        {
            "name": "suppression",
            # filterid is the suppression filter's only identifier. It is filed under
            # the temporal filter with the same id, which carries its identity itself,
            # so a suppression without a temporal filter line still yields a valid filter.
            "getval": re.compile(
                r"configure\salarm\ssuppression\sfilterid\s(?P<filterid>\d+)"
                r"(?:\sinterface\s(?P<interface>\S+))?"
                r"(?:\salarmid\s(?P<alarmid>\S+))?"
                r"(?:\s(?:(?P<no_status>no\sstatus)|status\s(?P<status>\S+)))?"
                r"(?:\s(?:(?P<no_threshold>no\sthreshold)|threshold\s(?P<threshold>\d+)))?"
                r"\s*$"
            ),
            "setval": "configure alarm suppression filterid {{ filterid }}",
            "result": {
                "filters": {
                    "temporal/{{ filterid }}": {
                        "fltr_type": "temporal",
                        "filterid": "{{ filterid }}",
                        # keyed by filterid (one suppression per id); the facts turn it into a list
                        "suppressions": {
                            "{{ filterid }}": {
                                "filterid": "{{ filterid }}",
                                "interface": "{{ interface }}",
                                "alarmid": "{{ alarmid }}",
                                "status": "{{ 'not-used' if no_status is defined else status }}",
                                "threshold": "{{ '1' if no_threshold is defined else threshold }}",
                            }
                        },
                    }
                }
            },
        },
        {
            "name": "delta_log",
            "getval": re.compile(
                r"configure\salarm\sdelta-log"
                r"(?:\sindet-log-full-action\s(?P<indet_log_full_action>\S+))?"
                r"(?:\swarn-log-full-action\s(?P<warn_log_full_action>\S+))?"
                r"(?:\sminor-log-full-action\s(?P<minor_log_full_action>\S+))?"
                r"(?:\smajor-log-full-action\s(?P<major_log_full_action>\S+))?"
                r"(?:\scrit-log-full-act\s(?P<crit_log_full_act>\S+))?\s*$",
            ),
            "setval": "configure alarm delta-log indet-log-full-action {{ indet_log_full_action }} warn-log-full-action {{ warn_log_full_action }} minor-log-full-action {{ minor_log_full_action }} major-log-full-action {{ major_log_full_action }} crit-log-full-act {{ crit_log_full_act }}",
            "result": {
                "delta_log": {
                    "indet_log_full_action": "{{ indet_log_full_action }}",
                    "warn_log_full_action": "{{ warn_log_full_action }}",
                    "minor_log_full_action": "{{ minor_log_full_action }}",
                    "major_log_full_action": "{{ major_log_full_action }}",
                    "crit_log_full_act": "{{ crit_log_full_act }}",
                }
            },
        },
        {
            "name": "custom_profile",
            "getval": _custom_profile_getval(),
            "setval": "configure alarm custom-profile {{ name }}",
            "result": _custom_profile_result(),
        },
        {
            "name": "hgutr069_cust",
            "getval": re.compile(
                r'configure\salarm\shgutr069-cust\s(?P<alarm_id>\S+)(?:\sdescription\s(?:"(?P<qdescription>[^"]*)"|(?P<description>\S+)))?\s*$',
            ),
            "setval": "configure alarm hgutr069-cust {{ alarm_id }} description {{ description }}",
            "result": {
                "hgutr069_custs": {
                    "{{ alarm_id }}": {
                        "alarm_id": "{{ alarm_id }}",
                        "description": "{{ description if description is defined else qdescription | default(None) }}",
                    }
                }
            },
        },
    ]
    # fmt: on
