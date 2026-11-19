# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Attribute table of the isam_generic_pon resource (global PON settings).

The device prints each node as one packed line ('info configure generic-pon detail
flat', lab ISAM)::

    configure generic-pon dpinteg-threshold 0
    configure generic-pon utilization no pon-pmcollect no ont-pmcollect
    configure generic-pon utilization threshold no txmcutilhi ... no dbacongthresh
    configure generic-pon ont no slid-mode no sn-bundle-timer no sw-ver-mis-block no sn-autounlock
    configure generic-pon alarmflag no ponlos-alarm-ctrl

TABLE (CLI guide) drives the facts, the config class and the argument spec (see
attribute_table.py). dpinteg-threshold is a top-level value without a removal form
(removable=False); the utilization thresholds are free string values (the device
prints "disabled" or a number). Nothing is created or removed: deleted resets sections.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import (
    Attr,
    AttributeTable,
    Node,
    TableTemplate,
)

_THRESHOLDS = (
    "txmcutilhi", "txmcutilmd", "txmcutillo", "txtotutilhi", "txtotutilmd", "txtotutillo",
    "rxtotutilhi", "rxtotutilmd", "rxtotutillo", "dbacongperiodhi", "dbacongperiodmd", "dbacongperiodlo",
    "txucdropfrmhi", "txucdropfrmmd", "txucdropfrmlo", "txmcdropfrmhi", "txmcdropfrmmd", "txmcdropfrmlo",
    "txbcdropfrmhi", "txbcdropfrmmd", "txbcdropfrmlo", "rxtotdropfrmhi", "rxtotdropfrmmd", "rxtotdropfrmlo",
    "numtcint", "numtcintdba", "dbacongthresh",
)

TABLE = AttributeTable("configure generic-pon", (
    Node((), "", (
        Attr("dpinteg_threshold", "dpinteg-threshold", "int", removable=False),
    )),
    Node("utilization", "utilization", (
        Attr("pon_pmcollect", "pon-pmcollect", "str", "none", ["none", "pm-enable", "tca-enable"]),
        Attr("ont_pmcollect", "ont-pmcollect", "str", "disable", ["enable", "disable"]),
    )),
    Node(("utilization", "threshold"), "utilization threshold",
         tuple(Attr(name, name, "str", "disabled") for name in _THRESHOLDS)),
    Node("ont", "ont", (
        Attr("slid_mode", "slid-mode", "str", "ascii", ["ascii", "hexa-dec"]),
        Attr("sn_bundle_timer", "sn-bundle-timer", "int", 24),
        Attr("sw_ver_mis_block", "sw-ver-mis-block", "str", "enable", ["enable", "disable"]),
        Attr("sn_autounlock", "sn-autounlock", "str", "disable", ["enable", "disable"]),
    )),
    Node("alarmflag", "alarmflag", (
        Attr("ponlos_alarm_ctrl", "ponlos-alarm-ctrl", "str", "disable", ["enable", "disable"]),
    )),
))


class Generic_ponTemplate(TableTemplate):
    TABLE = TABLE
