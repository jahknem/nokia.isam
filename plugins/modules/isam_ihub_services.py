#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Read-only IHUB customer, VPLS and IES configuration."""

DOCUMENTATION = """
---
module: isam_ihub_services
short_description: Gather or parse IHUB service configuration without changing the device
description:
  - Reads the verified family-wide C(info configure service) source.
  - Parses observed customers, VPLS including V-VPLS VLAN identity, IES interfaces and SAPs.
  - Other service types or options remain explicit projection coverage gaps.
version_added: "1.0.0"
author: Jan Kühnemund (@jahknem)
extends_documentation_fragment: nokia.isam.ihub
options:
  config:
    description:
      - Optional selections under C(customers) and C(services).
      - Customers select by C(id); services select by C(service_type) and C(id).
      - Selection filters the family-wide source and requires I(allow_broad_read=true); it is not a scoped device read.
    type: dict
    suboptions:
      customers:
        description: Customer identity selections.
        type: list
        elements: dict
        suboptions:
          id:
            description: Customer identifier.
            type: str
            required: true
      services:
        description: Service identity selections.
        type: list
        elements: dict
        suboptions:
          id:
            description: Service identifier.
            type: str
            required: true
          service_type:
            description: Service namespace.
            type: str
            required: true
            choices: [vpls, ies]
"""
EXAMPLES = """
- name: Explicitly gather the whole IHUB service family
  nokia.isam.isam_ihub_services:
    state: gathered

- name: Filter one VPLS from an explicitly authorized family-wide read
  nokia.isam.isam_ihub_services:
    state: gathered
    config:
      services:
        - service_type: vpls
          id: '99'
    allow_broad_read: true
"""
RETURN = """
gathered:
  description: Typed customer and service lists with interfaces and SAPs.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: The same typed projection from supplied hierarchical output.
  returned: when I(state) is C(parsed)
  type: dict
coverage:
  description: Projection coverage and unparsed command locations; not a device completeness certificate.
  returned: always
  type: dict
source:
  description: Actual read command and scope, or offline source.
  returned: always
  type: dict
ansible_facts:
  description: The gathered resource under C(ansible_network_resources.ihub_services); offline C(parsed) output is never published as facts.
  returned: when I(state) is C(gathered)
  type: dict
"""
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ihub_services.ihub_services import IhubServicesArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.ihub_config import run_module


def main():
    run_module("ihub_services", IhubServicesArgs.argument_spec)


if __name__ == "__main__":
    main()
