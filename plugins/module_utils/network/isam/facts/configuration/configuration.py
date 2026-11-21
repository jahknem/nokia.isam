# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Access-side flat root tree facts (lossless for captured lines, not all IHUB)."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import parse_config_tree


class Config_treeFacts(object):
    """Read 'info configure [detail] flat' and parse its captured lines into a tree.

    Non-detail (default) gives the configured content; detail also prints unset defaults
    (much larger). IHUB port/LAG/service sections are omitted by this source on
    evidenced firmware; the source metadata makes this boundary explicit.
    """

    def __init__(self, module, subspec="config", options="options"):
        self._module = module

    def populate_facts(self, connection, data=None):
        command = None
        if data is None:
            detail = bool(self._module.params.get("config_tree_detail"))
            command = "info configure detail flat" if detail else "info configure flat"
            data = connection.get(command)
        if isinstance(data, tuple):
            data = data[0]
        return {"config_tree": parse_config_tree(data), "config_tree_source": {
            "command": command, "read_scope": "device" if command else "provided",
            "configuration_complete": False,
            "known_flat_source_omissions": ["ihub_ports", "ihub_lags", "ihub_services"],
        }}
