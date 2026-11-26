# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import RetainedOnDeleteWarnings
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import TableResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.generic_pon import (
    TABLE,
    Generic_ponTemplate,
)


class Generic_pon(RetainedOnDeleteWarnings, TableResourceModule):
    """The isam_generic_pon config class (global settings: nothing is created or removed)."""

    TABLE = TABLE

    def __init__(self, module):
        super(Generic_pon, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="generic_pon",
            tmplt=Generic_ponTemplate(),
        )
