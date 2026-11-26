# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import RetainedOnDeleteWarnings
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import TableResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    TABLE,
    Isam_voice_sipTemplate,
)


class Isam_voice_sip(RetainedOnDeleteWarnings, TableResourceModule):
    """The isam_voice_sip config class (global settings: instances are created/removable,
    flat sections are reset)."""

    TABLE = TABLE

    def __init__(self, module):
        super(Isam_voice_sip, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="voice_sip",
            tmplt=Isam_voice_sipTemplate(),
        )
