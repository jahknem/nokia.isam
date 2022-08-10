# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Bridges parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class BridgesTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(BridgesTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "ageing_time",
            "getval": re.compile(
                r"""
                \s+ageing_time\s(?P<ageing_time>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "ageing_time": "{{ ageing_time }}",
            },
        },
        {
            "name": "port",
            "getval": re.compile(
                r"""
                port\s(?P<id>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}"
                }
            },
            "shared": True,

        },
        {
            "name": "default_priority",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?\sdefault-priority\s+(?P<default_priority>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "default_priority": "{{ 0 if negate is defined and default_priority is not defined else default_priority|int }}",
                    }
                },
            }
        },
        {
            "name": "mac_learn_off",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?\s(?P<mac_learn_off>mac-learn-off)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "mac_learn_off": "{{ False  if negate is defined True }}",
                    }
                }
            },
        },
        {
            "name": "max_unicast_mac",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \smax-unicast-mac\s(?P<max_unicast_mac>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "max_unicast_mac": "{{ none if negate is defined else max_unicast_mac|int }}",
                    }
                }
            },
        },
        {
            "name": "qos_profile",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \sos-profile\s(?P<qos_profile>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "qos_profile": "{{ none if negate is defined else qos_profile|string }}",
                    }
                }
            },
        },
        {
            "name": "prio_regen_prof",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \sprio-regen-prof\s(?P<prio_regen_prof>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "prio_regen_prof": "{{ none if negate is defined else prio_regen_prof|string }}",
                    }
                }
            },
        },
        {
            "name": "prio_regen_name",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \sprio-regen-name\s(?P<prio_regen_name>(none|trusted-port|best-effort|cl-all-prio-3|cl-all-prio-4|background|be-cl-voice|be-cl-ld-voice|be-voice|l2-vpn-3|l2-vpn-4|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "prio_regen_name": "{{ none if negate is defined else prio_regen_name|string }}",
                    }
                }
            },
        },
        {
            "name": "max_comitted_mac",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+max-committed-mac\s(?P<max_comitted_mac>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "max_comitted_mac": "{{ none if negate is defined else max_comitted_mac|int }}",
                    }
                }
            },
        },
        {
            "name": "mirror_mode",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+mirror-mode\s(?P<mirror_mode>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "mirror_mode": "{{ none if negate is defined else mirror_mode|string }}",
                    }
                }
            },
        },
        {
            "name": "mirror_vlan",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+mirror-vlan\s(?P<mirror_vlan>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "mirror_vlan": "{{ none if negate is defined else mirror_vlan|int }}",
                    }
                }
            },
        },
        {
            "name": "pvid_tagging_flag",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+pvid-tagging-flag\s(?P<pvid_tagging_flag>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "pvid_tagging_flag": "{{ none if negate is defined else pvid_tagging_flag|string }}",
                    }
                }
            },
        },
        {
            "name": "ds_pbit_mode",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+ds-pbit-mode\s(?P<ds_pbit_mode>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "ds_pbit_mode": "{{ none if negate is defined else ds_pbit_mode|string }}",
                    }
                }
            },
        },
        {
            "name": "vlan_id",
            "getval": re.compile(
                r"""
                \s+vlan-id\s(?P<vlan_id>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan": [{
                            "id": "{{ vlan_id|int }}",
                        }]
                    }
                }
            },
            "shared": True,
        },
        {
            "name": "tag",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+tag\s(?P<tag>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            "tag": "{{ none if tag is defined else tag|string }}",
                        }
                    }
                }
            },
        },
        {
            "name": "l2fwder_vlan",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+l2fwder-vlan\s(?P<l2fwder_vlan>\d+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            "l2fwder_vlan": "{{ none if tag is defined else l2fwder_vlan|string }}",
                        }
                    }
                }
            },
        },
        {
            "name": "vlan_scope",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+vlan-scope\s(?P<vlan_scope>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            "vlan_scope": "{{ none if negate is defined else vlan_scope|string }}",
                        }
                    }
                }
            },
        },
        {
            "name": "qos",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+qos\s(?P<qos>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            "qos": "{{ none if negate is defined else qos|string }}",
                        }
                    }
                }
            },
        },
        {
            "name": "qos_profile",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+qos-profile\s(?P<qos_profile>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "qos_profile": "{{ none if negate is defined else qos_profile|string }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_best_effort",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-best-effort\s(?P<prior_best_effort>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_best_effort": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_background",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-background\s(?P<prior_background>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_background": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_spare",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-spare\s(?P<prior_spare>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_spare": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_exc_effort",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-exc-effort\s(?P<prior_exc_effort>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_exc_effort": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_ctrl_load",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-ctrl-load\s(?P<prior_ctrl_load>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_ctrl_load": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_less_100ms",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-less-100ms\s(?P<prior_less_100ms>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_less_100ms": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_less_10ms",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-less-10ms\s(?P<prior_less_10ms>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_less_10ms": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "prior_nw_ctrl",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+prior-nw-ctrl\s(?P<prior_nw_ctrl>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "prior_nw_ctrl": "{{ none if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "in_qos_prof_name",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+in-qos-prof-name\s(?P<in_qos_prof_name>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "in_qos_prof_name": "{{ none if negate is defined else in_qos_prof_name|string }}",
                        }
                    }
                }
            },
        },
        {
            "name": "max_up_qos_policy",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+max-up-qos-policy\s(?P<max_up_qos_policy>(\d|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "max_up_qos_policy": "{{ 0 if negate is defined else max_up_qos_policy|int }}",
                        }
                    }
                }
            },
        },
        {
            "name": "max_ip_antispoof",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+max-ip-antispoof\s(?P<max_ip_antispoof>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "max_ip_antispoof": "{{ 65535 if negate is defined else max_ip_antispoof|int }}",
                        }
                    }
                }
            },
        },
        {
            "name": "max_unicast_mac",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+max-unicast-mac\s(?P<max_unicast_mac>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "max_unicast_mac": "{{ 65535 if negate is defined else max_unicast_mac|int }}",
                        }
                    }
                }
            },
        },
        {
            "name": "max_ipv6_antispf",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+max-ipv6-antispf\s(?P<max_ipv6_antispf>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "max_ipv6_antispf": "{{ 65535 if negate is defined else max_ipv6_antispf|int }}",
                        }
                    }
                }
            },
        },
        {
            "name": "mac_learn_ctrl",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+mac-learn-ctrl\s(?P<mac_learn_ctrl>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "mac_learn_ctrl": "{{ 3 if negate is defined else mac_learn_ctrl|int }}",
                        }
                    }
                }
            },
        },
        {
            "name": "min_cvlan_id",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+min-cvlan-id\s(?P<min_cvlan_id>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "min_cvlan_id": "{{ 1 if negate is defined else min_cvlan_id|int }}",
                        }
                    }
                }
            },
        },
        {
            "name": "max_cvlan_id",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+max-cvlan-id\s(?P<max_cvlan_id>(\d+|\#))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "max_cvlan_id": "{{ 4095 if negate is defined else max_cvlan_id }}",
                        }
                    }
                }
            },
        },
        {
            "name": "ds_dedicated_q",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+ds-dedicated-q\s(?P<ds_dedicated_q>\S+)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "ds_dedicated_q": "{{ False if negate is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "tpid",
            "getval": re.compile(
                r"""
                \s+(?P<negate> no)?
                \s+tpid\s(?P<tpid>[a-zA-Z0-9_]*)
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "port": {
                    "{{ id }}": {
                        "vlan_id": {
                            
                            "tpid": "{{ 0 if negate is defined else tpid|string }}",
                        }
                    }
                }
            },
        },
    ]
    # fmt: on
