# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class AlarmTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(AlarmTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "log_sev_level",
            "getval": re.compile(
                r"configure\salarm\slog-sev-level\s(?P<log_sev_level>(indeterminate|warning|minor|major|critical))\s"
                r"log-full-action\s(?P<log_full_action>(wrap|halt))\s"
                r"non-itf-rep-sev-level\s(?P<non_itf_rep_sev_level>(indeterminate|warning|minor|major|critical))$",
                re.VERBOSE,
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
            "getval": re.compile(
                r"configure\salarm\sentry\s(?P<index>\S+)\s*$",
                re.VERBOSE,
            ),
            "setval": "configure alarm entry {{ index }}",
            "result": {
                "entries": {
                    "{{ index }}": {}
                }
            },
            "shared": True,
            "compval": "entry",
        },
        {
            "name": "entry.severity",
            "getval": re.compile(
                r"configure\salarm\sentry\s(?P<index>\S+)\s((?P<negate>no\s)severity|severity\s(?P<severity>(indeterminate|warning|minor|major|critical)))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm entry {{ index }} {{ 'no' if negate else '' }}severity{{ ' ' + severity if not negate else '' }}",
            "result": {
                "entries": {
                    "{{ index }}": {
                        "index": "{{ index }}",
                        "severity": "{{ 'indeterminate' if negate else severity }}",
                    }
                }
            },
        },
        {
            "name": "entry.service_affecting",
            "getval": re.compile(
                r"configure\salarm\sentry\s(?P<index>\S+)\s((?P<negate>no\s)|(?P<service_affecting>service-affecting))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm entry {{ index }} {{ 'no' if negate else '' }}service-affecting",
            "result": {
                "entries": {
                    "{{ index }}": {
                        "index": "{{ index }}",
                        "service_affecting": "{{ False if negate else True }}",
                    }
                }
            },
        },
        {
            "name": "entry.reporting",
            "getval": re.compile(
                r"configure\salarm\sentry\s(?P<index>\S+)\s((?P<negate>no\s)|(?P<reporting>reporting))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm entry {{ index }} {{ 'no' if negate else '' }}reporting",
            "result": {
                "entries": {
                    "{{ index }}": {
                        "index": "{{ index }}",
                        "reporting": "{{ False if negate else True }}",
                    }
                }
            },
        },
        {
            "name": "entry.logging",
            "getval": re.compile(
                r"configure\salarm\sentry\s(?P<index>\S+)\s((?P<negate>no\s)|(?P<logging>logging))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm entry {{ index }} {{ 'no' if negate else '' }}logging",
            "result": {
                "entries": {
                    "{{ index }}": {
                        "index": "{{ index }}",
                        "logging": "{{ False if negate else True }}",
                    }
                }
            },
        },
        {
            "name": "filter",
            "getval": re.compile(
                r"configure\salarm\sfilter\s(?P<fltr_type>(temporal|spatial))\sfilterid\s(?P<filterid>\d+)$",
                re.VERBOSE,
            ),
            "setval": "configure alarm filter {{ fltr_type }} filterid {{ filterid }}",
            "result": {
                "filters": {
                    "{{ fltr_type }}/{{ filterid }}": {
                        "fltr_type": "{{ fltr_type }}",
                        "filterid": "{{ filterid }}",
                    }
                }
            },
            "shared": True,
            "compval": "filter",
        },
        {
            "name": "filter.alarmid",
            "getval": re.compile(
                r"configure\salarm\sfilter\s(?P<fltr_type>(temporal|spatial))\sfilterid\s(?P<filterid>\d+)\salarmid\s(?P<alarmid>\S+)$",
                re.VERBOSE,
            ),
            "setval": "configure alarm filter {{ fltr_type }} filterid {{ filterid }} alarmid {{ alarmid }}",
            "result": {
                "filters": {
                    "{{ fltr_type }}/{{ filterid }}": {
                        "fltr_type": "{{ fltr_type }}",
                        "filterid": "{{ filterid }}",
                        "alarmid": "{{ alarmid }}",
                    }
                }
            },
        },
        {
            "name": "filter.status",
            "getval": re.compile(
                r"configure\salarm\sfilter\s(?P<fltr_type>(temporal|spatial))\sfilterid\s(?P<filterid>\d+)\s((?P<negate>no\s)status|status\s(?P<status>\d+))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm filter {{ fltr_type }} filterid {{ filterid }} {{ 'no' if negate else '' }}status{{ ' ' + status if not negate else '' }}",
            "result": {
                "filters": {
                    "{{ fltr_type }}/{{ filterid }}": {
                        "fltr_type": "{{ fltr_type }}",
                        "filterid": "{{ filterid }}",
                        "status": "{{ 0 if negate else status }}",
                    }
                }
            },
        },
        {
            "name": "filter.threshold",
            "getval": re.compile(
                r"configure\salarm\sfilter\s(?P<fltr_type>(temporal|spatial))\sfilterid\s(?P<filterid>\d+)\s((?P<negate>no\s)threshold|threshold\s(?P<threshold>\d+))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm filter {{ fltr_type }} filterid {{ filterid }} {{ 'no' if negate else '' }}threshold{{ ' ' + threshold if not negate else '' }}",
            "result": {
                "filters": {
                    "{{ fltr_type }}/{{ filterid }}": {
                        "fltr_type": "{{ fltr_type }}",
                        "filterid": "{{ filterid }}",
                        "threshold": "{{ 0 if negate else threshold }}",
                    }
                }
            },
        },
        {
            "name": "filter.window",
            "getval": re.compile(
                r"configure\salarm\sfilter\s(?P<fltr_type>(temporal|spatial))\sfilterid\s(?P<filterid>\d+)\s((?P<negate>no\s)window|window\s(?P<window>\d+))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm filter {{ fltr_type }} filterid {{ filterid }} {{ 'no' if negate else '' }}window{{ ' ' + window if not negate else '' }}",
            "result": {
                "filters": {
                    "{{ fltr_type }}/{{ filterid }}": {
                        "fltr_type": "{{ fltr_type }}",
                        "filterid": "{{ filterid }}",
                        "window": "{{ 0 if negate else window }}",
                    }
                }
            },
        },
        {
            "name": "suppression",
            "getval": re.compile(
                r"configure\salarm\ssuppression\sfilterid\s(?P<filterid>\d+)\sinterface\s(?P<interface>\S+)\salarmid\s(?P<alarmid>\S+)$",
                re.VERBOSE,
            ),
            "setval": "configure alarm suppression filterid {{ filterid }} interface {{ interface }} alarmid {{ alarmid }}",
            "result": {
                "filters": {
                    "temporal/{{ filterid }}": {
                        "suppressions": [{
                            "filterid": "{{ filterid }}",
                            "interface": "{{ interface }}",
                            "alarmid": "{{ alarmid }}",
                        }]
                    }
                }
            },
        },
        {
            "name": "suppression.status",
            "getval": re.compile(
                r"configure\salarm\ssuppression\sfilterid\s(?P<filterid>\d+)\sinterface\s(?P<interface>\S+)\salarmid\s(?P<alarmid>\S+)\s((?P<negate>no\s)status|status\s(?P<status>\d+))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm suppression filterid {{ filterid }} interface {{ interface }} alarmid {{ alarmid }} {{ 'no' if negate else '' }}status{{ ' ' + status if not negate else '' }}",
            "result": {
                "filters": {
                    "temporal/{{ filterid }}": {
                        "suppressions": [{
                            "filterid": "{{ filterid }}",
                            "interface": "{{ interface }}",
                            "alarmid": "{{ alarmid }}",
                            "status": "{{ 0 if negate else status }}",
                        }]
                    }
                }
            },
        },
        {
            "name": "suppression.threshold",
            "getval": re.compile(
                r"configure\salarm\ssuppression\sfilterid\s(?P<filterid>\d+)\sinterface\s(?P<interface>\S+)\salarmid\s(?P<alarmid>\S+)\s((?P<negate>no\s)threshold|threshold\s(?P<threshold>\d+))$",
                re.VERBOSE,
            ),
            "setval": "configure alarm suppression filterid {{ filterid }} interface {{ interface }} alarmid {{ alarmid }} {{ 'no' if negate else '' }}threshold{{ ' ' + threshold if not negate else '' }}",
            "result": {
                "filters": {
                    "temporal/{{ filterid }}": {
                        "suppressions": [{
                            "filterid": "{{ filterid }}",
                            "interface": "{{ interface }}",
                            "alarmid": "{{ alarmid }}",
                            "threshold": "{{ 0 if negate else threshold }}",
                        }]
                    }
                }
            },
        },
        {
            "name": "delta_log",
            "getval": re.compile(
                r"configure\salarm\sdelta-log\s"
                r"indet-log-full-action\s(?P<indet_log_full_action>(wrap|halt))\s"
                r"warn-log-full-action\s(?P<warn_log_full_action>(wrap|halt))\s"
                r"minor-log-full-action\s(?P<minor_log_full_action>(wrap|halt))\s"
                r"major-log-full-action\s(?P<major_log_full_action>(wrap|halt))\s"
                r"crit-log-full-act\s(?P<crit_log_full_act>(wrap|halt))$",
                re.VERBOSE,
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
    ]
    # fmt: on
