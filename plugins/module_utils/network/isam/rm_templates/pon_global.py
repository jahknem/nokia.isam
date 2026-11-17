# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure pon``."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    SettingsBlockTemplate,
    make_parsers,
)

NODE = "pon"
# (option, CLI keyword, kind, device default); syntax from the CLI help:
# configure pon [ no pwrbrst-mode | pwrbrst-mode <value> ] [ no range-mode | range-mode <value> ]
ATTRS = (
    ("pwrbrst_mode", "pwrbrst-mode", "str", "disable"),
    ("range_mode", "range-mode", "str", "normal"),
)


class Pon_globalTemplate(SettingsBlockTemplate):
    NODE = NODE
    ATTRS = ATTRS
    PARSERS = make_parsers("pon_global", NODE, ATTRS)
