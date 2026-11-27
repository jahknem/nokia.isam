#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Several isolated reads on one MSAN, each with its own outcome."""

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_read
short_description: Read several configuration families and operational subsets of one ISAM, each with its own outcome
description:
  - Runs a list of reads on one MSAN and returns one result per read, in request order.
  - A read is a whole configuration family, a whole operational subset, or only some
    instances of one instance list of a configuration family (targeted gathering, the
    same read the family module does with C(state=gathered) and C(config)).
  - Every read is isolated. A read that fails, or a family the MSAN does not support,
    becomes a result with C(status=error) and the next read runs; the module itself
    only fails when it cannot run at all.
  - A targeted read says which named instances were found (C(returned_ids)), which
    the device confirmed absent (C(confirmed_absent_ids)) and which stay unverified
    (C(unverified_ids)). Only a confirmed absence establishes that an instance does
    not exist.
  - Known credential fields are removed from the data (fields the family marks
    C(no_log) and common credential names). Warnings are reduced to stable categories;
    the device's own text is never returned.
  - This module never writes configuration.
version_added: "1.1.0"
author: Jan Kühnemund (@jahknem)
options:
  reads:
    description: The reads to run, in order.
    type: list
    elements: dict
    required: true
    suboptions:
      kind:
        description:
          - C(configuration) reads a configuration family (the names of
            O(nokia.isam.isam_facts#module:gather_network_resources) plus
            C(pppoe_client_interface), C(pppoe_client_ppp_profile) and C(pppoel2_statistics)).
          - C(operational) reads an operational subset (the names of
            O(nokia.isam.isam_facts#module:gather_subset)).
        type: str
        choices: [configuration, operational]
        default: configuration
      resource:
        description: The family or subset to read.
        type: str
        required: true
      section:
        description:
          - The instance list the O(reads[].ids) belong to, as the family names it in
            its targeted gathering (C(config) when the family's config is itself the list,
            for example C(interfaces) or C(slots) for C(equipment_onts)).
          - Required with O(reads[].ids); leave out to read the whole family.
        type: str
      ids:
        description:
          - The instances to read. A string per instance for a single identity field, a
            mapping of every identity field for a composite identity.
          - Without ids the whole family is read.
        type: list
        elements: raw
      meta:
        description: Caller data returned unchanged with the read's result.
        type: dict
"""

EXAMPLES = """
- name: Read the ONT status, all PON interfaces and two ONTs
  nokia.isam.isam_read:
    reads:
      - kind: operational
        resource: ont_status
      - resource: pon_interfaces
      - resource: equipment_onts
        section: interfaces
        ids: [1/1/8/5/1, 1/1/8/5/2]
  register: device

- name: Name every ONT the device confirmed absent
  ansible.builtin.debug:
    msg: "{{ device.reads[2].confirmed_absent_ids }}"
"""

RETURN = """
status:
  description: C(ok) when every read is C(ok), C(error) when every read failed, else C(partial).
  returned: always
  type: str
reads:
  description: One result per read, in request order; the request's fields are echoed.
  returned: always
  type: list
  elements: dict
  contains:
    status:
      description: C(ok), C(partial) (read with warnings) or C(error).
      type: str
    data:
      description: The family's facts (redacted); for a targeted read only the named instances.
      type: raw
    returned_ids:
      description: Named instances present in C(data).
      type: list
    confirmed_absent_ids:
      description: Named instances the device reported as not existing.
      type: list
    unverified_ids:
      description: Named instances neither found nor confirmed absent.
      type: list
    dependency_gaps:
      description: >-
        Unverified instances whose read named a missing object they depend on
        (C(lower-interface), C(interface-index)): a list of C(id) and
        C(dependency_gap). Present only when there is one.
      type: list
    warnings:
      description: >-
        Warning categories: C(unsupported_resource), C(unmatched_configuration),
        C(empty_response), C(collection_warning).
      type: list
    parse:
      description: >-
        Parse outcome of a targeted read, when the family reports one: a string, or a
        mapping per section when the read covers several (see read_outcomes).
      type: raw
    error:
      description: For C(status=error), C(invalid_request), C(unsupported_resource) or C(read_failed).
      type: str
    error_detail:
      description: For C(error=invalid_request), what is wrong with the request.
      type: str
    collected_at:
      description: UTC time the read finished.
      type: str
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import (
    get_resource_connection,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.read import read_all


def main():
    module = AnsibleModule(
        argument_spec=dict(
            reads=dict(type="list", elements="dict", required=True, options=dict(
                kind=dict(type="str", choices=["configuration", "operational"], default="configuration"),
                resource=dict(type="str", required=True),
                section=dict(type="str"),
                ids=dict(type="list", elements="raw"),
                meta=dict(type="dict"),
            )),
        ),
        supports_check_mode=True,
    )
    # One connection for every read; each read sees it through its own params.
    module._connection = get_resource_connection(module)
    results, status = read_all(module, module.params["reads"])
    module.exit_json(changed=False, status=status, reads=results)


if __name__ == "__main__":
    main()
