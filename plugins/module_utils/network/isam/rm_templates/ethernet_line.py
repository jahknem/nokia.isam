# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The Ethernet_line parser templates file. This contains
a list of parser definitions and associated functions that
facilitates both facts gathering and native command generation for
the given network resource.
"""

import re
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)

class Ethernet_lineTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Ethernet_lineTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "port_type",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\sport-type\s(?P<port_type>\S+)
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} port-type {{ port_type }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "port_type": "{{ port_type }}",
                }
            },
        },
        {
            "name": "admin_up",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\s((?P<negate_admin_up>no\sadmin-up)|(?P<admin_up>admin-up))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} {{ 'no' if admin_up is 'False' else '' }}admin-up",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "admin_up": "{{ False if negate_admin_up else True }}",
                }
            },
        },
        {
            "name": "tca_line_threshold_enable",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_enable>no\senable)|(?P<tca_line_threshold_enable>enable))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} tca-line-threshold {{ 'no' if tca_line_threshold_enable is 'False' else '' }}enable",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "enable": "{{ 'False' if negate_tca_line_threshold_enable or if not tca_line_threshold_enable else 'True' }}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_los",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_los>no\slos)|los\s(?P<tca_line_threshold_los>\d+))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} tca-line-threshold los {{ 'no los' if tca_line_threshold_los is 'False' else tca_line_threshold_los }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "los": "{{ if not negate_tca_line_threshold_los then tca_line_threshold_los }}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_fcs",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_fcs>no\sfcs)|fcs\s(?P<tca_line_threshold_fcs>\d+))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} tca-line-threshold fcs {{ 'no fcs' if tca_line_threshold_fcs is 'False' else tca_line_threshold_fcs }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "fcs": "{{ if not negate_tca_line_threshold_fcs then tca_line_threshold_fcs }}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_rx_octets",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_rx_octets>no\srx-octets)|rx-octets\s(?P<tca_line_threshold_rx_octets>\d+))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} tca-line-threshold rx-octets {{ 'no rx-octets' if tca_line_threshold_rx_octets is 'False' else tca_line_threshold_rx_octets }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "rx_octets": "{{ if not negate_tca_line_threshold_rx_octets then tca_line_threshold_rx_octets else 0}}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_tx_octets",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_tx_octets>no\stx-octets)|tx-octets\s(?P<tca_line_threshold_tx_octets>\d+))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} tca-line-threshold tx-octets {{ 'no tx-octets' if tca_line_threshold_tx_octets is 'False' else tca_line_threshold_tx_octets }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "tx_octets": "{{ if not negate_tca_line_threshold_tx_octets then tca_line_threshold_tx_octets else 0}}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_los_day",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_los_day>no\slos-day)|los-day\s(?P<tca_line_threshold_los_day>\d+))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} tca-line-threshold los-day {{ 'no los-day' if tca_line_threshold_los_day is 'False' else tca_line_threshold_los_day }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "los_day": "{{ if tca_line_threshold_los_day is defined and negate_tca_line_threshold_los_day is not defined then tca_line_threshold_los_day else 0}}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_fcs_day",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_fcs_day>no\sfcs-day)|fcs-day\s(?P<tca_line_threshold_fcs_day>\d+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "fcs_day": "{{ if tca_line_threshold_fcs_day is defined and negate_tca_line_threshold_fcs_day is not defined then tca_line_threshold_fcs_day else 0}}",
                    }
                }   
            },
        },
        {
            "name": "tca_line_threshold_rx_octets_day",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_rx_octets_day>no\srx-octets-day)|rx-octets-day\s(?P<tca_line_threshold_rx_octets_day>\d+)) 
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "rx_octets_day": "{{ if tca_line_threshold_rx_octets_day is defined and negate_tca_line_threshold_rx_octets_day is not defined then tca_line_threshold_rx_octets_day else 0}}",
                    }
                }
            },
        },
        {
            "name": "tca_line_threshold_tx_octets_day",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\stca-line-threshold\s((?P<negate_tca_line_threshold_tx_octets_day>no\stx-octets-day)|tx-octets-day\s(?P<tca_line_threshold_tx_octets_day>\d+))
                $""", re.VERBOSE),
            "setval": "",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "tca_line_threshold": {
                        "tx_octets_day": "{{ if tca_line_threshold_tx_octets_day is defined and negate_tca_line_threshold_tx_octets_day is not defined then tca_line_threshold_tx_octets_day else 0}}",
                    }
                }
            },
        },
        {
            "name": "mau_type",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\stype\s(?P<mau_type>\S+)
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} type {{ mau_type }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "mau_type": "{{ mau_type }}",
                        }
                    }
                }
            },
        },
        {
            "name": "mau_power",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\spower\s(?P<mau_power>\S+)
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} power {{ 'down' if mau_power is False else 'up' }}",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "power": "{{ 'down' if mau_power is false else 'up' }}",
                        }
                    }
                }
            },
        },
        {
            "name": "mau_speed_auto_sense",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\s((?P<no_mau_speed_auto_sense>no\sspeed-auto-sense)|(?P<mau_speed_auto_sense>speed-auto-sense))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} {{ 'no' if no_mau_speed_auto_sense is defined else '' }} speed_auto_sense",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "speed_auto_sense": "{{ False if no_mau_speed_auto_sense is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "mau_autonegotiate",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\s((?P<no_mau_autonegotiate>no\sautonegotiate)|(?P<mau_autonegotiate>autonegotiate))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} {{ 'no' if no_mau_autonegotiate is defined else '' }} autonegotiate",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "autonegotiate": "{{ False if no_mau_autonegotiate is defined else True }}",
                        }   
                    }
                }
            },
        },
        {
            "name": "mau_cap100base_tfd",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\s((?P<no_mau_cap100base_tfd>no\scap100base-tfd)|(?P<mau_cap100base_tfd>cap100base-tfd))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} {{ 'no' if no_mau_cap100base_tfd is defined else '' }} cap100base-tfd", 
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "cap100base_tfd": "{{ False if no_mau_cap100base_tfd is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "mau_cap1000base_xfd",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\s((?P<no_mau_cap1000base_xfd>no\scap1000base-xfd)|(?P<mau_cap1000base_xfd>cap1000base-xfd))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} {{ 'no' if no_mau_cap1000base_xfd is defined else '' }} cap1000base-xfd",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "cap1000base_xfd": "{{ False if no_mau_cap1000base_xfd is defined else True }}",
                        }
                    }
                }
            },
        },
        {
            "name": "mau_cap1000base_tfd",
            "getval": re.compile(
                r"""
                configure\sethernet\sline\s(?P<if_index>\S+)\smau\s(?P<index>\d+)\s((?P<no_mau_cap1000base_tfd>no\scap1000base-tfd)|(?P<mau_cap1000base_tfd>cap1000base-tfd))
                $""", re.VERBOSE),
            "setval": "configure ethernet line {{ if_index }} mau {{ index }} {{ 'no' if no_mau_cap1000base_tfd is defined else '' }} cap1000base-tfd",
            "result": {
                "{{ if_index }}": {
                    "if_index": "{{ if_index }}",
                    "mau": {
                        "{{ index }}": {
                            "index": "{{ index }}",
                            "cap1000base_tfd": "{{ False if no_mau_cap1000base_tfd is defined else True }}",
                        }
                    }
                }
            },
        },
    ]
    # fmt: on
