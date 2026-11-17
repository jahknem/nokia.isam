# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Whole-configuration root tree facts (schema-less, lossless)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import parse_config_tree


class Config_treeFacts(object):
    """Read 'info configure [detail] flat' once and parse the whole config into a tree.

    Non-detail (default) gives the configured content; detail also prints unset defaults
    (much larger). Secret attribute values are redacted by name.
    """

    def __init__(self, module, subspec="config", options="options"):
        self._module = module

    def populate_facts(self, connection, data=None):
        if data is None:
            detail = bool(self._module.params.get("config_tree_detail"))
            command = "info configure detail flat" if detail else "info configure flat"
            data = connection.get(command)
        if isinstance(data, tuple):
            data = data[0]
        return {"config_tree": parse_config_tree(data)}
