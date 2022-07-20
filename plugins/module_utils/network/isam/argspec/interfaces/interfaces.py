# -*- coding: utf-8 -*-
# Copyright 2022 Red Hat
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

#############################################
#                WARNING                    #
#############################################
#
# This file is auto generated by the
# cli_rm_builder.
#
# Manually editing this file is not advised.
#
# To update the argspec make the desired changes
# in the module docstring and re-run
# cli_rm_builder.
#
#############################################

"""
The arg spec for the isam_interfaces module
"""


class InterfacesArgs(object):  # pylint: disable=R0903
    """The arg spec for the isam_interfaces module
    """

    argument_spec = {
        "config": {
            "type": "list",
            "elements": "dict",
            "options": {
                "id": {"type": "str"},
                "admin-up": {"type": "bool"},
                "link-state-trap": {
                    "type": "str",
                    "choices": ["enable", "disable", "no-value"],
                    "default": "no-value",
                },
                "link-up-down-trap": {"type": "bool"},
                "severity": {
                    "type": "str",
                    "choices": [
                        "indetermiante",
                        "warning",
                        "minor",
                        "major",
                        "critical",
                        "no-alarms",
                        "default",
                        "no-value",
                    ],
                    "default": "no-value",
                },
                "port-type": {
                    "type": "str",
                    "choices": ["uni", "nni", "hc-uni", "uplink"],
                    "default": "uni",
                },
            },
        },
        "state": {
            "type": "str",
            "choices": ["merged", "replaced", "overridden", "deleted", "gathered"],
            "default": "merged",
        },
    }  # pylint: disable=C0301
