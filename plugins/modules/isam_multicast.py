#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_multicast
short_description: Manage Nokia ISAM multicast configuration.
description:
  - Manages C(configure igmp) (service context, C(system), C(package)) and C(configure mcast-control) configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided multicast configuration.
    type: dict
    suboptions:
      igmp:
        description: IGMP multicast service context settings.
        type: dict
        suboptions:
          mcast_svc_context:
            description: Multicast service context name.
            type: str
          mld_snooping:
            description: Enable or disable MLD snooping.
            type: bool
          mld_querier:
            description: Enable or disable MLD querier.
            type: bool
          igmp_snooping:
            description: Enable or disable IGMP snooping.
            type: bool
          igmp_querier:
            description: Enable or disable IGMP querier.
            type: bool
          query_interval:
            description: IGMP query interval in seconds.
            type: int
          query_response_interval:
            description: IGMP query response interval in seconds.
            type: int
          robustness_count:
            description: IGMP robustness count.
            type: int
          system:
            description: 'Node-wide settings (C(configure igmp system)). Values absent from the device (C(no <keyword>) in C(detail) output) are the defaults.'
            type: dict
            suboptions:
              src_ip_address:
                description: 'IPv4 source address sent in every multicast IP datagram (C(src-ip-address), default C(0.0.0.0)).'
                type: str
              verify_checksum:
                description: 'Verify the checksum of received multicast frames (C([no] verify-checksum)).'
                type: bool
              query_interval:
                description: 'Interval in seconds at which general membership queries are sent (C(query-interval), C(2..3175), default C(125)).'
                type: int
              max_rsp_time:
                description: 'Maximum query response time advertised in queries, in 1/10 s (C(max-rsp-time), C(1..31744), default C(100)).'
                type: int
              robustness:
                description: 'Tuning for the expected packet loss on a subnet (C(robustness), C(1..10), default C(2)).'
                type: int
              mem_query_int:
                description: 'Interval between group-specific queries, in 1/10 s (C(mem-query-int), C(2..31744), default C(10)).'
                type: int
              last_memb_cnt:
                description: 'Number of group-specific queries sent (C(last-memb-cnt), C(1..10), default C(2)).'
                type: int
              last_max_resp_tim:
                description: 'Last member maximum response time, in 1/10 s (C(last-max-resp-tim), C(1..31744), default C(2)).'
                type: int
              host_report_intv:
                description: 'Unsolicited host report interval, in 1/10 s (C(host-report-intv), C(1..255), default C(10)).'
                type: int
              start:
                description: 'Start the multicast application module (C([no] start)).'
                type: bool
              preview_valid:
                description: 'Time in seconds confirming a preview session is valid (C(preview-valid), C(1..120), default C(8)).'
                type: int
              cdr_validation:
                description: 'Minimum session time in seconds for generating a CDR, C(0..120) or C(none) (C(cdr-validation), default C(2)).'
                type: str
              cdr_generation:
                description: 'Start CDR generation in the system (C([no] cdr-generation)).'
                type: bool
              except_cdr_rate:
                description: 'Limit for the generation of CDR records, in minutes (C(except-cdr-rate), C(1..30), default C(3)).'
                type: int
              cdr_export:
                description: 'How CDRs are generated and forwarded (C(cdr-export), default C(local-file-storage)).'
                type: str
                choices: ['local-file-storage', 'remote-logging']
              cdr_file_aging:
                description: 'CDR file aging time in hours (C(cdr-file-aging), C(4..24), default C(8)).'
                type: int
              cdr_polling:
                description: 'CDR polling period in seconds, multiple of 60 (C(cdr-polling), C(60..900), default C(180)).'
                type: int
              user_igmp_version:
                description: 'IGMP version of general membership queries to the user side (C(user-igmp-version), default C(3)).'
                type: str
                choices: ['2', '3']
              netw_igmp_version:
                description: 'IGMP version received/forwarded on the network side (C(netw-igmp-version), default C(3)).'
                type: str
                choices: ['2', '3']
              v3_max_num_rec:
                description: 'Maximum number of group records in one IGMPv3/MLDv2 report, as 2 to the power N (C(v3-max-num-rec), C(0..10), default C(3)).'
                type: int
              forking:
                description: 'Enable IGMP forking at system level (C([no] forking)).'
                type: bool
              lt_ont_signaling:
                description: 'Enable LT to ONT signaling at system level (C([no] lt-ont-signaling)).'
                type: bool
              vlan_selection:
                description: 'Enable VLAN selection (C([no] vlan-selection)).'
                type: bool
              disc_lwr_version:
                description: 'Discard lower version packets (C([no] disc-lwr-version)).'
                type: bool
              uncfg_mcast_supp:
                description: 'Unconfigured SSM/ASM support for GPON/DSL LT cards (C(uncfg-mcast-supp), default C(legacy)).'
                type: str
                choices: ['legacy', 'asmandssm']
              cdr_type:
                description: 'Call detail record types (C(configure igmp system cdr-type)).'
                type: dict
                suboptions:
                  periodic:
                    description: 'Generate interim CDR records for fullview/preview (C([no] periodic)).'
                    type: bool
                  period:
                    description: 'Intermediate CDR generation period in minutes, multiple of 5 (C(period), C(15..60), default C(15)).'
                    type: int
                  attempt_max_pview:
                    description: 'Generate a CDR when the maximum number of previews is exceeded (C([no] attempt-max-pview)).'
                    type: bool
                  attempt_blackout:
                    description: 'Generate a CDR when a blackout period is active (C([no] attempt-blackout)).'
                    type: bool
                  attempt_no_perm:
                    description: 'Generate a CDR on a join without access rights (C([no] attempt-no-perm)).'
                    type: bool
          packages:
            description: 'Package bitmaps (C(configure igmp package <index>)). The 1024 package slots always exist; slots with only default values are not gathered, and resetting a package sends C(no name no template-name no template-version). Targetable with I(state=gathered) by I(index) (reads C(info configure igmp package <index> flat)).'
            type: list
            elements: dict
            suboptions:
              index:
                description: 'Package index (C(1..1024)).'
                type: int
                required: true
              name:
                description: 'Package name (C(name), printable string, up to 32 characters).'
                type: str
              template_name:
                description: 'Name of the service template containing this package (C(template-name), up to 32 characters).'
                type: str
              template_version:
                description: 'Version of the service template containing this package (C(template-version), C(0..65535)).'
                type: int
      mcast_control:
        description: Multicast control settings.
        type: dict
        suboptions:
          mcast_svc_context:
            description: Multicast service context name.
            type: str
          admin_state:
            description: Enable or disable multicast control.
            type: bool
          max_groups:
            description: Maximum number of multicast groups.
            type: int
          max_sources:
            description: Maximum number of sources per group.
            type: int
          system:
            description: 'Node-wide settings (C(configure mcast-control system)). Values absent from the device (C(no <keyword>) in C(detail) output) are the defaults.'
            type: dict
            suboptions:
              src_ip_address:
                description: 'IPv4 source address sent in every multicast IP datagram (C(src-ip-address), default C(0.0.0.0)).'
                type: str
              v6_src_ip_address:
                description: 'IPv6 link-local source address sent in every multicast IP datagram (C(v6-src-ip-address)).'
                type: str
              verify_checksum:
                description: 'Verify the checksum of received multicast frames (C([no] verify-checksum)).'
                type: bool
              query_interval:
                description: 'Interval in seconds at which general membership queries are sent (C(query-interval), C(2..3175), default C(125)).'
                type: int
              max_rsp_time:
                description: 'Maximum query response time advertised in queries, in 1/10 s (C(max-rsp-time), C(1..31744), default C(100)).'
                type: int
              robustness:
                description: 'Tuning for the expected packet loss on a subnet (C(robustness), C(1..10), default C(2)).'
                type: int
              mem_query_int:
                description: 'Interval between group-specific queries, in 1/10 s (C(mem-query-int), C(2..31744), default C(10)).'
                type: int
              last_memb_cnt:
                description: 'Number of group-specific queries sent (C(last-memb-cnt), C(1..10), default C(2)).'
                type: int
              last_max_resp_tim:
                description: 'Last member maximum response time, in 1/10 s (C(last-max-resp-tim), C(1..31744), default C(2)).'
                type: int
              host_report_intv:
                description: 'Unsolicited host report interval, in 1/10 s (C(host-report-intv), C(1..255), default C(10)).'
                type: int
              start:
                description: 'Start the multicast application module (C([no] start)).'
                type: bool
              preview_valid:
                description: 'Time in seconds confirming a preview session is valid (C(preview-valid), C(1..120), default C(8)).'
                type: int
              cdr_validation:
                description: 'Minimum session time in seconds for generating a CDR, C(0..120) or C(none) (C(cdr-validation), default C(2)).'
                type: str
              cdr_generation:
                description: 'Start CDR generation in the system (C([no] cdr-generation)).'
                type: bool
              except_cdr_rate:
                description: 'Limit for the generation of CDR records, in minutes (C(except-cdr-rate), C(1..30), default C(3)).'
                type: int
              cdr_export:
                description: 'How CDRs are generated and forwarded (C(cdr-export), default C(local-file-storage)).'
                type: str
                choices: ['local-file-storage', 'remote-logging']
              cdr_file_aging:
                description: 'CDR file aging time in hours (C(cdr-file-aging), C(4..24), default C(8)).'
                type: int
              cdr_polling:
                description: 'CDR polling period in seconds, multiple of 60 (C(cdr-polling), C(60..900), default C(180)).'
                type: int
              user_igmp_version:
                description: 'IGMP version of general membership queries to the user side (C(user-igmp-version), default C(3)).'
                type: str
                choices: ['2', '3']
              netw_igmp_version:
                description: 'IGMP version received/forwarded on the network side (C(netw-igmp-version), default C(3)).'
                type: str
                choices: ['2', '3']
              user_mld_version:
                description: 'MLD version of general membership queries to the user side (C(user-mld-version), default C(2)).'
                type: str
                choices: ['1', '2']
              netw_mld_version:
                description: 'MLD version received/forwarded on the network side (C(netw-mld-version), default C(2)).'
                type: str
                choices: ['1', '2']
              v3_max_num_rec:
                description: 'Maximum number of group records in one IGMPv3/MLDv2 report, as 2 to the power N (C(v3-max-num-rec), C(0..10), default C(3)).'
                type: int
              forking:
                description: 'Enable IGMP forking at system level (C([no] forking)).'
                type: bool
              lt_ont_signaling:
                description: 'Enable LT to ONT signaling at system level (C([no] lt-ont-signaling)).'
                type: bool
              vlan_selection:
                description: 'Enable VLAN selection (C([no] vlan-selection)).'
                type: bool
              disc_lwr_version:
                description: 'Discard lower version packets (C([no] disc-lwr-version)).'
                type: bool
              uncfg_mcast_supp:
                description: 'Unconfigured SSM/ASM support for GPON/DSL LT cards (C(uncfg-mcast-supp), default C(legacy)).'
                type: str
                choices: ['legacy', 'asmandssm']
              cdr_type:
                description: 'Call detail record types (C(configure mcast-control system cdr-type)).'
                type: dict
                suboptions:
                  periodic:
                    description: 'Generate interim CDR records for fullview/preview (C([no] periodic)).'
                    type: bool
                  period:
                    description: 'Intermediate CDR generation period in minutes, multiple of 5 (C(period), C(15..60), default C(15)).'
                    type: int
                  attempt_max_pview:
                    description: 'Generate a CDR when the maximum number of previews is exceeded (C([no] attempt-max-pview)).'
                    type: bool
                  attempt_blackout:
                    description: 'Generate a CDR when a blackout period is active (C([no] attempt-blackout)).'
                    type: bool
                  attempt_no_perm:
                    description: 'Generate a CDR on a join without access rights (C([no] attempt-no-perm)).'
                    type: bool
          packages:
            description: 'Package bitmaps (C(configure mcast-control package <index>)). The 1024 package slots always exist; slots with only default values are not gathered, and resetting a package sends C(no name no template-name no template-version). Targetable with I(state=gathered) by I(index) (reads C(info configure mcast-control package <index> flat)).'
            type: list
            elements: dict
            suboptions:
              index:
                description: 'Package index (C(1..1024)).'
                type: int
                required: true
              name:
                description: 'Package name (C(name), printable string, up to 32 characters).'
                type: str
              template_name:
                description: 'Name of the service template containing this package (C(template-name), up to 32 characters).'
                type: str
              template_version:
                description: 'Version of the service template containing this package (C(template-version), C(0..65535)).'
                type: int
  running_config:
    description: Device native configuration to parse.
    type: str
  state:
    description: The state of the configuration after module completion.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- name: Gather multicast configuration
  nokia.isam.isam_multicast:
    state: gathered

- name: Configure IGMP multicast service context
  nokia.isam.isam_multicast:
    config:
      igmp:
        mcast_svc_context: default
        mld_snooping: true
        igmp_snooping: true
        query_interval: 125
      mcast_control:
        mcast_svc_context: default
        admin_state: true
        max_groups: 256
    state: merged
"""

RETURN = """
before:
  description: The configuration as structured data before module invocation.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: dict
after:
  description: The resulting configuration as structured data after module invocation.
  returned: when changed
  type: dict
commands:
  description: The set of commands pushed to the remote device.
  returned: when I(state) is C(merged), C(replaced), C(overridden), or C(deleted)
  type: list
rendered:
  description: The provided configuration rendered as device-native commands.
  returned: when I(state) is C(rendered)
  type: list
gathered:
  description: Facts gathered from the remote device as structured data.
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description: Device-native config parsed into structured data.
  returned: when I(state) is C(parsed)
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.multicast.multicast import (
    MulticastArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.multicast.multicast import (
    Multicast,
)


def main():
    module = AnsibleModule(
        argument_spec=MulticastArgs.argument_spec,
        mutually_exclusive=[["config", "running_config"]],
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )

    result = Multicast(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
