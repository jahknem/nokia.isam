# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""The isam_uni_onts config class (configure uni ont tc-layer).

State logic is shared with isam_l2uni_onts (UniPmConfigMixin): fields are set or
reset to their CLI default with ``no <attr>``; the node exists with its UNI.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.l2uni_onts.l2uni_onts import (
    UniPmConfigMixin,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.uni_onts import (
    Uni_ontsTemplate,
)


class Uni_onts(UniPmConfigMixin, ResourceModule):
    """The isam_uni_onts config class."""

    TEMPLATE = Uni_ontsTemplate

    def __init__(self, module):
        super(Uni_onts, self).__init__(
            empty_fact_val=[],
            facts_module=Facts(module),
            module=module,
            resource="uni_onts",
            tmplt=Uni_ontsTemplate(),
        )

    def _sections(self, data):
        return {"config": data or []}
