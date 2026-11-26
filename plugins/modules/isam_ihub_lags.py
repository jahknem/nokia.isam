#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Read-only IHUB LAG configuration, distinct from access link-agg groups."""

DOCUMENTATION = """
---
module: isam_ihub_lags
short_description: Gather or parse IHUB LAG configuration without changing the device
description:
  - Reads the LAG Configuration section of hierarchical C(info configure).
  - The verified source is device-wide and requires I(allow_broad_read=true).
  - IHUB LAG identities are not the LT addresses of access-side link-agg groups.
version_added: "1.1.0"
author: Jan Kühnemund (@jahknem)
extends_documentation_fragment: nokia.isam.ihub
options:
  config:
    description:
      - Optional list of LAG selections, identified by C(id) (the only accepted key).
      - This filters the device-wide source and requires I(allow_broad_read=true); it is not a scoped device read.
    type: list
    elements: dict
    suboptions:
      id:
        description: IHUB LAG identifier, for example C(1).
        type: str
        required: true
"""
EXAMPLES = """
- name: Explicitly gather the IHUB LAG family using its verified root source
  nokia.isam.isam_ihub_lags:
    state: gathered
    allow_broad_read: true
"""
RETURN = """
gathered:
  description: Typed LAG configuration including member ports, LACP and shutdown settings.
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
  description: The gathered resource under C(ansible_network_resources.ihub_lags); offline C(parsed) output is never published as facts.
  returned: when I(state) is C(gathered)
  type: dict
"""
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.ihub_lags.ihub_lags import IhubLagsArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.ihub_config import run_module


def main():
    run_module("ihub_lags", IhubLagsArgs.argument_spec)


if __name__ == "__main__":
    main()
