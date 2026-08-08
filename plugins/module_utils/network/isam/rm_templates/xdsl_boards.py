# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Xdsl_boardsTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Xdsl_boardsTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    PARSERS = [
        {
            "name": "board.admin_state",
            "setval": "configure xdsl board {{ board_id }} admin-state {{ admin_state }}",
            "remval": "configure xdsl board {{ board_id }} no admin-state",
        },
        {
            "name": "board.card_type",
            "setval": "configure xdsl board {{ board_id }} card-type {{ card_type }}",
            "remval": "configure xdsl board {{ board_id }} no card-type",
        },
        {
            "name": "board.dpbo_profile",
            "setval": "configure xdsl board {{ board_id }} dpbo-profile {{ dpbo_profile }}",
            "remval": "configure xdsl board {{ board_id }} no dpbo-profile",
        },
        {
            "name": "board.vce_profile",
            "setval": "configure xdsl board {{ board_id }} vce-profile {{ vce_profile }}",
            "remval": "configure xdsl board {{ board_id }} no vce-profile",
        },
        {
            "name": "board",
            "setval": "configure xdsl board {{ board_id }}",
            "remval": "configure xdsl no board {{ board_id }}",
        },
        {
            "name": "vp_board.admin_state",
            "setval": "configure xdsl vp-board {{ vp_board_id }} admin-state {{ admin_state }}",
            "remval": "configure xdsl vp-board {{ vp_board_id }} no admin-state",
        },
        {
            "name": "vp_board",
            "setval": "configure xdsl vp-board {{ vp_board_id }}",
            "remval": "configure xdsl no vp-board {{ vp_board_id }}",
        },
    ]
