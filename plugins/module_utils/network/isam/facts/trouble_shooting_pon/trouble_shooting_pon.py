# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
The isam trouble_shooting_pon fact class.
"""

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import (
    get_targeted_config,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.trouble_shooting_pon.trouble_shooting_pon import (
    Trouble_shooting_ponArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.trouble_shooting_pon import (
    Trouble_shooting_ponTemplate,
)


def to_config(parsed):
    """Module config shape of a template parse.

    A threshold entry with only default values exists (every PON has one): it stays
    as its identity, the defaults are not reported (docs/targeted-read-contract.md).
    """
    config = {}
    if parsed.get("interfaces"):
        config["interfaces"] = list(parsed["interfaces"].values())
    threshold = {}
    if "interval" in parsed:
        threshold["interval"] = parsed["interval"]
    entries = list(parsed.get("thresholds", {}).values())
    if entries:
        threshold["interfaces"] = entries
    if threshold:
        config["threshold"] = threshold
    return config


class Trouble_shooting_ponFacts(object):
    """The isam_trouble_shooting_pon facts class."""

    def __init__(self, module, subspec="config", options="options"):
        self._module = module
        self.argument_spec = Trouble_shooting_ponArgs.argument_spec

    def get_config(self, connection):
        """The whole resource, or only the interfaces named in config (targeted gathering)."""
        return get_targeted_config(self._module, connection, "trouble_shooting_pon", "info configure trouble-shooting pon flat", {
            "interfaces": "info configure trouble-shooting pon statistics interface %s flat",
            "threshold.interfaces": "info configure trouble-shooting pon statistics threshold interface %s flat",
        })

    def populate_facts(self, connection, ansible_facts, data=None):
        """Populate facts for the trouble_shooting_pon network resource."""
        facts = {}
        if not data:
            data = self.get_config(connection)
        if isinstance(data, tuple):
            data = data[0]
        parser = Trouble_shooting_ponTemplate(lines=str(data or "").splitlines(), module=self._module)
        objs = to_config(parser.parse())

        ansible_facts["ansible_network_resources"].pop("trouble_shooting_pon", None)
        params = {}
        if objs:
            params = utils.remove_empties(
                parser.validate_config(self.argument_spec, {"config": objs}, redact=True)
            ) or {}
        facts["trouble_shooting_pon"] = params.get("config") or {}
        ansible_facts["ansible_network_resources"].update(facts)
        return ansible_facts
