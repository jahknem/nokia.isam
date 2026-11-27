# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure pppox-relay cross-connect global-session``."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    SettingsBlockTemplate,
    make_parsers,
)

NODE = "pppox-relay cross-connect global-session"
# (option, CLI keyword, kind, device default); syntax from the CLI help:
# configure pppox-relay cross-connect global-session [ no pado-timeout | pado-timeout <value> ] [ no pads-timeout | pads-timeout <value> ] [ no max-pad-attempts | max-pad-attempts <value> ] [ no trans-max-age | trans-max-age <value> ] [ no cc-max-age | cc-max-age <value> ]
ATTRS = (
    ("pado_timeout", "pado-timeout", "int", 3),
    ("pads_timeout", "pads-timeout", "int", 3),
    ("max_pad_attempts", "max-pad-attempts", "int", 10),
    ("trans_max_age", "trans-max-age", "int", 300),
    ("cc_max_age", "cc-max-age", "int", 300),
)


class Pppox_relay_globalTemplate(SettingsBlockTemplate):
    NODE = NODE
    ATTRS = ATTRS
    PARSERS = make_parsers("pppox_relay_global", NODE, ATTRS)
