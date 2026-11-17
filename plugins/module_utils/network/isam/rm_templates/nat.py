# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure nat``."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.settings_block import (
    SettingsBlockTemplate,
    make_parsers,
)

NODE = "nat"
# (option, CLI keyword, kind, device default); syntax from the CLI help:
# configure nat [ no aging-time | aging-time <value> ]
ATTRS = (
    ("aging_time", "aging-time", "int", 120),
)


class NatTemplate(SettingsBlockTemplate):
    NODE = NODE
    ATTRS = ATTRS
    PARSERS = make_parsers("nat", NODE, ATTRS)
