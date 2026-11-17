# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


# CLI keyword grammar of ``configure xdsl board`` / ``vp-board``, shared by the
# facts parser and the renderer. Every attribute below is printed by
# ``info configure xdsl ... detail`` as ``no <keyword>`` when at its default,
# which is also its removal form.
#
# (field, keyword, kind) with kind "value" (``<keyword> <value>``) or "flag"
# (``<keyword>`` / ``no <keyword>``).
BOARD_ATTRS = (
    ("admin_state", "admin-state", "value"),
    ("card_type", "card-type", "value"),
    ("dpbo_profile", "dpbo-profile", "value"),
    ("vce_profile", "vce-profile", "value"),
    ("vplt_autodiscover", "vplt-autodiscover", "value"),
    ("vce_capacity_mode", "vce-capacity-mode", "value"),
    ("leg_upbo_profile", "leg-upbo-profile", "value"),
    ("vect_class", "vect-class", "value"),
)
# Sub-nodes of a board: (field, keyword, attributes).
BOARD_SUBNODES = (
    ("vect_fallback", "vect-fallback", (
        ("fb_vplt_com_fail", "fb-vplt-com-fail", "flag"),
        ("fb_cpe_cap_mism", "fb-cpe-cap-mism", "flag"),
        ("fb_conf_not_feas", "fb-conf-not-feas", "flag"),
        ("spectrum_profile", "spectrum-profile", "value"),
        ("service_profile", "service-profile", "value"),
        ("dpbo_profile", "dpbo-profile", "value"),
        ("rtx_profile", "rtx-profile", "value"),
        ("sos_profile", "sos-profile", "value"),
    )),
    ("auto_port_reset", "auto-port-reset", (
        ("max_retry_attempt", "max-retry-attempt", "value"),
        ("reset_interval", "reset-interval", "value"),
        ("reset_threshold", "reset-threshold", "value"),
    )),
)
BOARD_INT_FIELDS = {
    "auto_port_reset": ("max_retry_attempt", "reset_interval", "reset_threshold"),
}
VP_BOARD_ATTRS = (
    ("admin_state", "admin-state", "value"),
)
VP_LINK_ATTRS = (
    ("lt_expect", "lt-expect", "value"),
)


def _board_parsers():
    parsers = []
    for field, keyword, _kind in BOARD_ATTRS:
        parsers.append({
            "name": "board.%s" % field,
            "setval": "configure xdsl board {{ board_id }} %s {{ %s }}" % (keyword, field),
            "remval": "configure xdsl board {{ board_id }} no %s" % keyword,
        })
    for node, node_keyword, attrs in BOARD_SUBNODES:
        for field, keyword, kind in attrs:
            prefix = "configure xdsl board {{ board_id }} %s " % node_keyword
            if kind == "flag":
                setval = prefix + "{{ '%s' if %s.%s else 'no %s' }}" % (keyword, node, field, keyword)
            else:
                setval = prefix + "%s {{ %s.%s }}" % (keyword, node, field)
            parsers.append({
                "name": "board.%s.%s" % (node, field),
                "setval": setval,
                "remval": prefix + "no %s" % keyword,
            })
    parsers.append({
        "name": "board",
        "setval": "configure xdsl board {{ board_id }}",
        "remval": "configure xdsl no board {{ board_id }}",
    })
    return parsers


def _vp_board_parsers():
    parsers = []
    for field, keyword, _kind in VP_BOARD_ATTRS:
        parsers.append({
            "name": "vp_board.%s" % field,
            "setval": "configure xdsl vp-board {{ vp_board_id }} %s {{ %s }}" % (keyword, field),
            "remval": "configure xdsl vp-board {{ vp_board_id }} no %s" % keyword,
        })
    for field, keyword, _kind in VP_LINK_ATTRS:
        parsers.append({
            "name": "vp_board.vp_links.%s" % field,
            "setval": "configure xdsl vp-board {{ vp_board_id }} vp-link {{ link_id }} %s {{ %s }}" % (keyword, field),
            "remval": "configure xdsl vp-board {{ vp_board_id }} vp-link {{ link_id }} no %s" % keyword,
        })
    parsers.append({
        "name": "vp_board",
        "setval": "configure xdsl vp-board {{ vp_board_id }}",
        "remval": "configure xdsl no vp-board {{ vp_board_id }}",
    })
    return parsers


class Xdsl_boardsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_boardsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = _board_parsers() + _vp_board_parsers()
