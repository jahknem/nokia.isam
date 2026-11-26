# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import warn_retained_on_delete
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.resource_module import TableResourceModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    TABLE,
    Software_mngtTemplate,
)


class Software_mngt(TableResourceModule):
    """The isam_software_mngt config class (global settings; OSWP records are a list)."""

    TABLE = TABLE

    def __init__(self, module):
        super(Software_mngt, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="software_mngt",
            tmplt=Software_mngtTemplate(),
        )

    def generate_commands(self):
        super(Software_mngt, self).generate_commands()
        warn_retained_on_delete(self)
