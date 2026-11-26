#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.igmp.igmp import IgmpArgs
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.igmp.igmp import Igmp


DOCUMENTATION = """
---
module: isam_igmp
short_description: Manage Nokia ISAM IGMP configuration
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
description:
  - Owns only the C(configure igmp) command family.
options:
  config:
    description: IGMP configuration.
    type: dict
    suboptions:
      mcast_svc_context:
        description: 'Multicast service context name (C(mcast-svc-context)).'
        type: str
      mld_snooping:
        description: 'Enable or disable MLD snooping.'
        type: bool
      mld_querier:
        description: 'Enable or disable MLD querier.'
        type: bool
      igmp_snooping:
        description: 'Enable or disable IGMP snooping.'
        type: bool
      igmp_querier:
        description: 'Enable or disable IGMP querier.'
        type: bool
      query_interval:
        description: 'IGMP query interval in seconds.'
        type: int
      query_response_interval:
        description: 'IGMP query response interval in seconds.'
        type: int
      robustness_count:
        description: 'IGMP robustness count.'
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
  running_config:
    description:
      - 'Device-native configuration to parse.'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
      - Desired state of the configuration.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device,
        selected by C(packages[].index) (targeted gathering). Other fields are ignored and absent
        instances are not returned; an instance with nothing configured answers like an absent one
        and is not returned either. Without I(config) the whole resource is read.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = r"""
- name: Gather IGMP configuration from the device
  nokia.isam.isam_igmp:
    state: gathered

- name: Read only the named packages (targeted gathering)
  nokia.isam.isam_igmp:
    state: gathered
    config:
      packages:
        - index: 5
        - index: 42
"""

RETURN = """
# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)
read_outcomes:
  description:
    - Sanitized per-instance read outcomes for a targeted read (I(state) is C(gathered)
      and I(config) names instances).
    - Each outcome names the config section that addressed the instance (for example
      C(config)) and the selector -- the instance identity, a composite identity
      recorded joined by C(/). Instances in different sections that share an identity
      value are different instances and are reported separately.
    - Each outcome records the command axis (C(ok), C(rejected) or C(failed)) and the
      instance-existence axis (C(present), C(confirmed_absent) or C(unknown)).
    - Only C(confirmed_absent) -- the device's explicit "instance does not exist" signal
      about that instance -- is evidence the instance is gone. C(unknown) (a header-only
      reply, an invalid-token rejection, a missing dependency, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(complete), C(partial), C(failed) or C(unverified)) is reported at
      resource level under C(parse); C(unverified) means the parser did not record its
      coverage of the reply.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With I(running_config) (offline preview) they are rendered only, never sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""


def main():
    module = AnsibleModule(
        argument_spec=IgmpArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]], ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]], ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    module.exit_json(**Igmp(module).execute_module())


if __name__ == "__main__":
    main()

MODULE_DESCRIPTION = """
module: isam_igmp
short_description: Manage Nokia ISAM IGMP
description: Manage Nokia ISAM IGMP using the configure igmp command family.
"""
