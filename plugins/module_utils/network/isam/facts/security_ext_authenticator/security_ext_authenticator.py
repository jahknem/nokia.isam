from __future__ import absolute_import, division, print_function

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.security_ext_authenticator import (
    Isam_security_ext_authenticatorTemplate,
)


class Isam_security_ext_authenticatorFacts(object):
    """Parse supplied command output without issuing an operational command."""

    def __init__(self, module):
        self.module = module

    def populate_facts(self, ansible_facts, data):
        template = Isam_security_ext_authenticatorTemplate(
            lines=data.splitlines() if isinstance(data, str) else data or [],
            module=self.module,
        )
        ansible_facts["security_ext_authenticator"] = template.parse()
        return ansible_facts
