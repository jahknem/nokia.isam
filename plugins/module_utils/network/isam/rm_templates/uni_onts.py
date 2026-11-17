# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Parser/renderer for ``configure uni ont tc-layer <uni>`` (TC-layer PM collection per UNI).

Device form (``info configure uni [detail] flat``)::

    configure uni ont tc-layer 1/1/2/1/1/1/1 no pm-collect

Uses the UNI PM engine of rm_templates/l2uni_onts.py.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.l2uni_onts import (
    UniPmField,
    UniPmNode,
    UniPmTemplate,
)

UNI_NODES = (
    UniPmNode(
        "config", "configure uni ont tc-layer",
        [UniPmField("pm_collect", "pm-collect", "str", "disable")],
    ),
)


class Uni_ontsTemplate(UniPmTemplate):
    NODES = UNI_NODES
