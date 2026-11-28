#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Read-only IHUB port configuration, distinct from access interface ports."""

DOCUMENTATION = """
---
module: isam_ihub_ports
short_description: Gather or parse IHUB port configuration without changing the device
description:
  - Reads the Port Configuration section of hierarchical C(info configure).
  - The verified source is device-wide and requires I(allow_broad_read=true).
  - Optical, internal and virtual IHUB ports remain separate from access-side interfaces and equipment inventory.
version_added: "1.0.0"
author: Jan Kühnemund (@jahknem)
extends_documentation_fragment: nokia.isam.ihub
options:
  config:
    description:
      - Optional list of port selections, identified by C(id) (the only accepted key).
      - This filters the device-wide source and requires I(allow_broad_read=true); it is not a scoped device read.
    type: list
    elements: dict
    suboptions:
      id:
        description: IHUB port identity, for example C(nt-a:xfp:3).
        type: str
        required: true
"""
EXAMPLES = """
- name: Explicitly gather the IHUB port family using its verified root source
  nokia.isam.isam_ihub_ports:
    state: gathered
    allow_broad_read: true
"""
RETURN = """
gathered:
  description: Typed port configuration including observed shutdown, description and Ethernet settings.
  returned: when I(state) is C(gathered)
  type: list
  elements: dict
parsed:
  description: The same typed projection from supplied hierarchical output.
  returned: when I(state) is C(parsed)
  type: list
  elements: dict
coverage:
  description: Projection coverage and unparsed command locations; not a device completeness certificate.
  returned: always
  type: dict
source:
  description: Actual read command and scope, or offline source.
  returned: always
  type: dict
ansible_facts:
  description: The gathered resource under C(ansible_network_resources.ihub_ports); offline C(parsed) output is never published as facts.
  returned: when I(state) is C(gathered)
  type: dict
"""
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ihub_ports.ihub_ports import IhubPortsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.ihub_config import run_module


def main():
    run_module("ihub_ports", IhubPortsArgs.argument_spec)


if __name__ == "__main__":
    main()
