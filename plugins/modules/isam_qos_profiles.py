#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_qos_profiles
version_added: 1.0.0
short_description: Manage QoS profiles on Nokia ISAM devices
description:
- Manage initial support for C(configure qos profiles) on Nokia ISAM devices.
- The module supports live-observed profile identities and all parameters of the profile types
  C(queue), C(scheduler-node), C(cac), C(marker d1p), C(policer), C(session), C(aggrqueuesconfig),
  C(shaper), C(bandwidth), C(ingress-qos) and C(rate-limit).
- Parameter options keep the CLI spelling (for example C(q0-priority)); facts use that spelling.
  The snake_case spelling (for example C(q0_priority)) is accepted as an alias.
- Mandatory profile parameters (the ones on the profile line, for example C(committed-info-rate))
  can be changed but not removed; with I(state=replaced) or I(state=overridden) they are kept and a warning is issued.
  Deleting a profile renders only C(configure qos profiles no <type> <name>).
- Optional parameters are reset with C(configure qos profiles <type> <name> no <parameter>) (CLI help syntax, not yet verified on a device).
- Complex nested profile data can be supplied as raw strings in C(attributes).
author: Jan Kühnemund (@jahknem)
notes:
- Tested against read-only output from Nokia ISAM 6.2.04ng.
options:
  config:
    type: list
    elements: dict
    description: QoS profile entries.
    suboptions:
      profile_type:
        description: QoS profile family.
        type: str
        required: true
        choices: [queue, scheduler-node, cac, marker-d1p, policer, session, aggrqueuesconfig, shaper, bandwidth, ingress-qos, rate-limit]
      name:
        description: QoS profile name or identifier.
        type: str
        required: true
      queue-type:
        description:
        - Positional CLI value of profile type queue. Buffer acceptance control algorithm (C(bac-complex-type)), e.g. C(red:24:48:80) or C(tail-drop:64).
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: str
        aliases: [queue_type]
      unit:
        description:
        - CLI C(unit), profile type queue. Threshold unit type.
        type: str
        choices: [packet, byte]
      priority:
        description:
        - CLI C(priority), profile type scheduler-node. Relative priority (1-8).
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
      weight:
        description:
        - CLI C(weight), profile type scheduler-node. Relative weight (0-127).
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
      shaper-profile:
        description:
        - CLI C(shaper-profile), profile type scheduler-node. Associated shaper profile, C(none) or C(name:<profile>).
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: str
        aliases: [shaper_profile]
      ext-shaper:
        description:
        - CLI C(ext-shaper), profile type scheduler-node. Shaper profile for 10G PON bandwidth, C(none) or C(name:<profile>).
        type: str
        aliases: [ext_shaper]
      autoshape:
        description:
        - CLI C(autoshape), profile type shaper. Automatic shaping (C(autoshape-on) or C(no-autoshape-on)).
        type: str
      mcast-inc-shape:
        description:
        - CLI C(mcast-inc-shape), profile type scheduler-node. Whether downstream shaping includes multicast (C(mcast-shap-on) or C(no-mcast-shap)).
        type: str
        aliases: [mcast_inc_shape]
      res-voice-bandwidth:
        description:
        - CLI C(res-voice-bandwidth), profile type cac. Reserved voice bandwidth in kbps.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [res_voice_bandwidth]
      max-mcast-bandwidth:
        description:
        - CLI C(max-mcast-bandwidth), profile type cac. Maximum multicast and unicast video bandwidth in kbps.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [max_mcast_bandwidth]
      res-data-bandwidth:
        description:
        - CLI C(res-data-bandwidth), profile type cac. Reserved data bandwidth in kbps.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [res_data_bandwidth]
      cac-type:
        description:
        - CLI C(cac-type), profile type cac. CAC profile type (C(dsl-cac), C(pon-cac), C(generic-pon-cac)).
        type: str
        aliases: [cac_type]
      default-dot1p:
        description:
        - CLI C(default-dot1p), profile type marker-d1p. Default dot1p bit value (0-7).
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [default_dot1p]
      use-dei:
        description:
        - CLI C(use-dei), profile type ingress-qos. Use the DEI bit (C(use-dei) / C(no use-dei)).
        type: bool
        aliases: [use_dei]
      policer-type:
        description:
        - CLI C(policer-type), profile type policer. Policer type.
        type: str
        aliases: [policer_type]
      excess-burst-size:
        description:
        - CLI C(excess-burst-size), profile type policer. Excess burst size (trTCM).
        type: int
        aliases: [excess_burst_size]
      coupling-flag:
        description:
        - CLI C(coupling-flag), profile type policer. Coupling flag (trTCM), C(enable) or C(disable).
        type: str
        aliases: [coupling_flag]
      color-mode:
        description:
        - CLI C(color-mode), profile type policer. Color mode (trTCM), C(color-blind) or C(color-aware).
        type: str
        aliases: [color_mode]
      green-action:
        description:
        - CLI C(green-action), profile type policer. Action for green packets.
        type: str
        aliases: [green_action]
      yellow-action:
        description:
        - CLI C(yellow-action), profile type policer. Action for yellow packets.
        type: str
        aliases: [yellow_action]
      red-action:
        description:
        - CLI C(red-action), profile type policer. Action for red packets.
        type: str
        aliases: [red_action]
      policed-size-ctrl:
        description:
        - CLI C(policed-size-ctrl), profile type policer. Control for the policed frame size.
        type: str
        aliases: [policed_size_ctrl]
      peak-info-rate:
        description:
        - CLI C(peak-info-rate), profile type policer. Peak information rate in kbps.
        type: int
        aliases: [peak_info_rate]
      peak-burst-size:
        description:
        - CLI C(peak-burst-size), profile type policer. Peak burst size in bytes.
        type: int
        aliases: [peak_burst_size]
      cos-threshold:
        description:
        - CLI C(cos-threshold), profile type policer. CoS threshold profile, C(none) or C(name:<profile>).
        type: str
        aliases: [cos_threshold]
      ing-outer-marker:
        description:
        - CLI C(ing-outer-marker), profile type session. Ingress outer marker profile, C(none) or C(name:<profile>).
        type: str
        aliases: [ing_outer_marker]
      ds-schedule-tag:
        description:
        - CLI C(ds-schedule-tag), profile type session. Downstream scheduler tag.
        type: str
        aliases: [ds_schedule_tag]
      up-policer-per-tc:
        description:
        - CLI C(up-policer-per-tc), profile type session. Upstream policer-per-tc profile, C(none) or C(name:<profile>).
        type: str
        aliases: [up_policer_per_tc]
      up-dscptotc-prof:
        description:
        - CLI C(up-dscptotc-prof), profile type session. Upstream DSCP-to-TC profile.
        type: str
        aliases: [up_dscptotc_prof]
      dn-dscptotc-prof:
        description:
        - CLI C(dn-dscptotc-prof), profile type session. Downstream DSCP-to-TC profile.
        type: str
        aliases: [dn_dscptotc_prof]
      up-pbittotc-prof:
        description:
        - CLI C(up-pbittotc-prof), profile type session. Upstream pbit-to-TC profile.
        type: str
        aliases: [up_pbittotc_prof]
      dn-pbittotc-prof:
        description:
        - CLI C(dn-pbittotc-prof), profile type session. Downstream pbit-to-TC profile.
        type: str
        aliases: [dn_pbittotc_prof]
      up-default-tc:
        description:
        - CLI C(up-default-tc), profile type session. Upstream default traffic class.
        type: int
        aliases: [up_default_tc]
      dn-default-tc:
        description:
        - CLI C(dn-default-tc), profile type session. Downstream default traffic class.
        type: int
        aliases: [dn_default_tc]
      assu-burst-size:
        description:
        - CLI C(assu-burst-size), profile type bandwidth. Assured burst size (EPON) in kB.
        type: int
        aliases: [assu_burst_size]
      exce-burst-size:
        description:
        - CLI C(exce-burst-size), profile type bandwidth. Excessive burst size (EPON) in kB.
        type: int
        aliases: [exce_burst_size]
      dbru:
        description:
        - CLI C(dbru), profile type bandwidth. DBRu use (C(enable), C(disable), C(enable-if-supported)).
        type: str
      committed-info-rate:
        description:
        - CLI C(committed-info-rate), profile type policer, shaper, bandwidth. Committed information rate in kbps.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [committed_info_rate]
      committed-burst-size:
        description:
        - CLI C(committed-burst-size), profile type policer, shaper. Committed burst size in bytes.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [committed_burst_size]
      excess-info-rate:
        description:
        - CLI C(excess-info-rate), profile type policer, shaper. Excess information rate in kbps.
        type: int
        aliases: [excess_info_rate]
      shaper-type:
        description:
        - CLI C(type), profile type shaper. Shaper type; CLI keyword C(type).
        type: str
        aliases: [shaper_type]
      assured-info-rate:
        description:
        - CLI C(assured-info-rate), profile type bandwidth. Assured information rate in kbps.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [assured_info_rate]
      excessive-info-rate:
        description:
        - CLI C(excessive-info-rate), profile type bandwidth. Excessive information rate in kbps.
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: int
        aliases: [excessive_info_rate]
      delay-tolerance:
        description:
        - CLI C(delay-tolerance), profile type bandwidth. Delay tolerance (1-240).
        type: int
        aliases: [delay_tolerance]
      logical-flow-type:
        description:
        - CLI C(logical-flow-type), profile type session. Logical flow type (deprecated on the device; C(generic) is used).
        - Mandatory on the device; it can be changed but not removed (it goes away with the profile).
        type: str
        aliases: [logical_flow_type]
      up-policer:
        description:
        - CLI C(up-policer), profile type session. Upstream policer profile, C(none) or C(name:<profile>).
        type: str
        aliases: [up_policer]
      down-policer:
        description:
        - CLI C(down-policer), profile type session. Downstream policer profile, C(none) or C(name:<profile>).
        type: str
        aliases: [down_policer]
      up-marker:
        description:
        - CLI C(up-marker), profile type session. Upstream marker profile, C(none) or C(name:<profile>).
        type: str
        aliases: [up_marker]
      total-rate:
        description:
        - CLI C(total-rate), profile type rate-limit. Total rate limit in pps.
        type: int
        aliases: [total_rate]
      total-burst:
        description:
        - CLI C(total-burst), profile type rate-limit. Total burst in pps.
        type: int
        aliases: [total_burst]
      dot1-p0-tc:
        description:
        - CLI C(dot1-p0-tc), profile type ingress-qos. Traffic class for pbit 0.
        type: int
        aliases: [dot1_p0_tc]
      dot1-p1-tc:
        description:
        - CLI C(dot1-p1-tc), profile type ingress-qos. Traffic class for pbit 1.
        type: int
        aliases: [dot1_p1_tc]
      dot1-p2-tc:
        description:
        - CLI C(dot1-p2-tc), profile type ingress-qos. Traffic class for pbit 2.
        type: int
        aliases: [dot1_p2_tc]
      dot1-p3-tc:
        description:
        - CLI C(dot1-p3-tc), profile type ingress-qos. Traffic class for pbit 3.
        type: int
        aliases: [dot1_p3_tc]
      dot1-p4-tc:
        description:
        - CLI C(dot1-p4-tc), profile type ingress-qos. Traffic class for pbit 4.
        type: int
        aliases: [dot1_p4_tc]
      dot1-p5-tc:
        description:
        - CLI C(dot1-p5-tc), profile type ingress-qos. Traffic class for pbit 5.
        type: int
        aliases: [dot1_p5_tc]
      dot1-p6-tc:
        description:
        - CLI C(dot1-p6-tc), profile type ingress-qos. Traffic class for pbit 6.
        type: int
        aliases: [dot1_p6_tc]
      dot1-p7-tc:
        description:
        - CLI C(dot1-p7-tc), profile type ingress-qos. Traffic class for pbit 7.
        type: int
        aliases: [dot1_p7_tc]
      q0-priority:
        description:
        - CLI C(q0-priority), profile type aggrqueuesconfig. Priority of queue 0.
        type: int
        aliases: [q0_priority]
      q0-weight:
        description:
        - CLI C(q0-weight), profile type aggrqueuesconfig. Relative weight of queue 0.
        type: int
        aliases: [q0_weight]
      q0-queue-prof:
        description:
        - CLI C(q0-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 0, C(none) or C(name:<profile>).
        type: str
        aliases: [q0_queue_prof]
      q0-shaper-prof:
        description:
        - CLI C(q0-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 0.
        type: str
        aliases: [q0_shaper_prof]
      q0-bandwidth-prof:
        description:
        - CLI C(q0-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 0.
        type: str
        aliases: [q0_bandwidth_prof]
      q0-bw-sharing:
        description:
        - CLI C(q0-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 0.
        type: str
        aliases: [q0_bw_sharing]
      q1-priority:
        description:
        - CLI C(q1-priority), profile type aggrqueuesconfig. Priority of queue 1.
        type: int
        aliases: [q1_priority]
      q1-weight:
        description:
        - CLI C(q1-weight), profile type aggrqueuesconfig. Relative weight of queue 1.
        type: int
        aliases: [q1_weight]
      q1-queue-prof:
        description:
        - CLI C(q1-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 1, C(none) or C(name:<profile>).
        type: str
        aliases: [q1_queue_prof]
      q1-shaper-prof:
        description:
        - CLI C(q1-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 1.
        type: str
        aliases: [q1_shaper_prof]
      q1-bandwidth-prof:
        description:
        - CLI C(q1-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 1.
        type: str
        aliases: [q1_bandwidth_prof]
      q1-bw-sharing:
        description:
        - CLI C(q1-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 1.
        type: str
        aliases: [q1_bw_sharing]
      q2-priority:
        description:
        - CLI C(q2-priority), profile type aggrqueuesconfig. Priority of queue 2.
        type: int
        aliases: [q2_priority]
      q2-weight:
        description:
        - CLI C(q2-weight), profile type aggrqueuesconfig. Relative weight of queue 2.
        type: int
        aliases: [q2_weight]
      q2-queue-prof:
        description:
        - CLI C(q2-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 2, C(none) or C(name:<profile>).
        type: str
        aliases: [q2_queue_prof]
      q2-shaper-prof:
        description:
        - CLI C(q2-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 2.
        type: str
        aliases: [q2_shaper_prof]
      q2-bandwidth-prof:
        description:
        - CLI C(q2-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 2.
        type: str
        aliases: [q2_bandwidth_prof]
      q2-bw-sharing:
        description:
        - CLI C(q2-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 2.
        type: str
        aliases: [q2_bw_sharing]
      q3-priority:
        description:
        - CLI C(q3-priority), profile type aggrqueuesconfig. Priority of queue 3.
        type: int
        aliases: [q3_priority]
      q3-weight:
        description:
        - CLI C(q3-weight), profile type aggrqueuesconfig. Relative weight of queue 3.
        type: int
        aliases: [q3_weight]
      q3-queue-prof:
        description:
        - CLI C(q3-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 3, C(none) or C(name:<profile>).
        type: str
        aliases: [q3_queue_prof]
      q3-shaper-prof:
        description:
        - CLI C(q3-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 3.
        type: str
        aliases: [q3_shaper_prof]
      q3-bandwidth-prof:
        description:
        - CLI C(q3-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 3.
        type: str
        aliases: [q3_bandwidth_prof]
      q3-bw-sharing:
        description:
        - CLI C(q3-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 3.
        type: str
        aliases: [q3_bw_sharing]
      q4-priority:
        description:
        - CLI C(q4-priority), profile type aggrqueuesconfig. Priority of queue 4.
        type: int
        aliases: [q4_priority]
      q4-weight:
        description:
        - CLI C(q4-weight), profile type aggrqueuesconfig. Relative weight of queue 4.
        type: int
        aliases: [q4_weight]
      q4-queue-prof:
        description:
        - CLI C(q4-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 4, C(none) or C(name:<profile>).
        type: str
        aliases: [q4_queue_prof]
      q4-shaper-prof:
        description:
        - CLI C(q4-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 4.
        type: str
        aliases: [q4_shaper_prof]
      q4-bandwidth-prof:
        description:
        - CLI C(q4-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 4.
        type: str
        aliases: [q4_bandwidth_prof]
      q4-bw-sharing:
        description:
        - CLI C(q4-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 4.
        type: str
        aliases: [q4_bw_sharing]
      q5-priority:
        description:
        - CLI C(q5-priority), profile type aggrqueuesconfig. Priority of queue 5.
        type: int
        aliases: [q5_priority]
      q5-weight:
        description:
        - CLI C(q5-weight), profile type aggrqueuesconfig. Relative weight of queue 5.
        type: int
        aliases: [q5_weight]
      q5-queue-prof:
        description:
        - CLI C(q5-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 5, C(none) or C(name:<profile>).
        type: str
        aliases: [q5_queue_prof]
      q5-shaper-prof:
        description:
        - CLI C(q5-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 5.
        type: str
        aliases: [q5_shaper_prof]
      q5-bandwidth-prof:
        description:
        - CLI C(q5-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 5.
        type: str
        aliases: [q5_bandwidth_prof]
      q5-bw-sharing:
        description:
        - CLI C(q5-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 5.
        type: str
        aliases: [q5_bw_sharing]
      q6-priority:
        description:
        - CLI C(q6-priority), profile type aggrqueuesconfig. Priority of queue 6.
        type: int
        aliases: [q6_priority]
      q6-weight:
        description:
        - CLI C(q6-weight), profile type aggrqueuesconfig. Relative weight of queue 6.
        type: int
        aliases: [q6_weight]
      q6-queue-prof:
        description:
        - CLI C(q6-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 6, C(none) or C(name:<profile>).
        type: str
        aliases: [q6_queue_prof]
      q6-shaper-prof:
        description:
        - CLI C(q6-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 6.
        type: str
        aliases: [q6_shaper_prof]
      q6-bandwidth-prof:
        description:
        - CLI C(q6-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 6.
        type: str
        aliases: [q6_bandwidth_prof]
      q6-bw-sharing:
        description:
        - CLI C(q6-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 6.
        type: str
        aliases: [q6_bw_sharing]
      q7-priority:
        description:
        - CLI C(q7-priority), profile type aggrqueuesconfig. Priority of queue 7.
        type: int
        aliases: [q7_priority]
      q7-weight:
        description:
        - CLI C(q7-weight), profile type aggrqueuesconfig. Relative weight of queue 7.
        type: int
        aliases: [q7_weight]
      q7-queue-prof:
        description:
        - CLI C(q7-queue-prof), profile type aggrqueuesconfig. Queue profile of queue 7, C(none) or C(name:<profile>).
        type: str
        aliases: [q7_queue_prof]
      q7-shaper-prof:
        description:
        - CLI C(q7-shaper-prof), profile type aggrqueuesconfig. Shaper profile of queue 7.
        type: str
        aliases: [q7_shaper_prof]
      q7-bandwidth-prof:
        description:
        - CLI C(q7-bandwidth-prof), profile type aggrqueuesconfig. Bandwidth profile of queue 7.
        type: str
        aliases: [q7_bandwidth_prof]
      q7-bw-sharing:
        description:
        - CLI C(q7-bw-sharing), profile type aggrqueuesconfig. Bandwidth sharing of queue 7.
        type: str
        aliases: [q7_bw_sharing]
      arp-rate:
        description:
        - CLI C(arp-rate), profile type rate-limit. ARP rate limit in pps.
        type: int
        aliases: [arp_rate]
      arp-burst:
        description:
        - CLI C(arp-burst), profile type rate-limit. ARP burst limit in pps.
        type: int
        aliases: [arp_burst]
      dhcp-rate:
        description:
        - CLI C(dhcp-rate), profile type rate-limit. DHCP rate limit in pps.
        type: int
        aliases: [dhcp_rate]
      dhcp-burst:
        description:
        - CLI C(dhcp-burst), profile type rate-limit. DHCP burst limit in pps.
        type: int
        aliases: [dhcp_burst]
      igmp-rate:
        description:
        - CLI C(igmp-rate), profile type rate-limit. IGMP rate limit in pps.
        type: int
        aliases: [igmp_rate]
      igmp-burst:
        description:
        - CLI C(igmp-burst), profile type rate-limit. IGMP burst limit in pps.
        type: int
        aliases: [igmp_burst]
      pppoe-rate:
        description:
        - CLI C(pppoe-rate), profile type rate-limit. PPPOE rate limit in pps.
        type: int
        aliases: [pppoe_rate]
      pppoe-burst:
        description:
        - CLI C(pppoe-burst), profile type rate-limit. PPPOE burst limit in pps.
        type: int
        aliases: [pppoe_burst]
      nd-rate:
        description:
        - CLI C(nd-rate), profile type rate-limit. ND rate limit in pps.
        type: int
        aliases: [nd_rate]
      nd-burst:
        description:
        - CLI C(nd-burst), profile type rate-limit. ND burst limit in pps.
        type: int
        aliases: [nd_burst]
      icmpv6-rate:
        description:
        - CLI C(icmpv6-rate), profile type rate-limit. ICMPV6 rate limit in pps.
        type: int
        aliases: [icmpv6_rate]
      icmpv6-burst:
        description:
        - CLI C(icmpv6-burst), profile type rate-limit. ICMPV6 burst limit in pps.
        type: int
        aliases: [icmpv6_burst]
      mld-rate:
        description:
        - CLI C(mld-rate), profile type rate-limit. MLD rate limit in pps.
        type: int
        aliases: [mld_rate]
      mld-burst:
        description:
        - CLI C(mld-burst), profile type rate-limit. MLD burst limit in pps.
        type: int
        aliases: [mld_burst]
      dhcpv6-rate:
        description:
        - CLI C(dhcpv6-rate), profile type rate-limit. DHCPV6 rate limit in pps.
        type: int
        aliases: [dhcpv6_rate]
      dhcpv6-burst:
        description:
        - CLI C(dhcpv6-burst), profile type rate-limit. DHCPV6 burst limit in pps.
        type: int
        aliases: [dhcpv6_burst]
      cfm-rate:
        description:
        - CLI C(cfm-rate), profile type rate-limit. CFM rate limit in pps.
        type: int
        aliases: [cfm_rate]
      cfm-burst:
        description:
        - CLI C(cfm-burst), profile type rate-limit. CFM burst limit in pps.
        type: int
        aliases: [cfm_burst]
      dot1-p0-color:
        description:
        - CLI C(dot1-p0-color), profile type ingress-qos. Ingress color for pbit 0.
        type: str
        aliases: [dot1_p0_color]
      dot1-p0-pol-tc:
        description:
        - CLI C(dot1-p0-pol-tc), profile type ingress-qos. Policer traffic class for pbit 0.
        type: int
        aliases: [dot1_p0_pol_tc]
      dot1-p1-color:
        description:
        - CLI C(dot1-p1-color), profile type ingress-qos. Ingress color for pbit 1.
        type: str
        aliases: [dot1_p1_color]
      dot1-p1-pol-tc:
        description:
        - CLI C(dot1-p1-pol-tc), profile type ingress-qos. Policer traffic class for pbit 1.
        type: int
        aliases: [dot1_p1_pol_tc]
      dot1-p2-color:
        description:
        - CLI C(dot1-p2-color), profile type ingress-qos. Ingress color for pbit 2.
        type: str
        aliases: [dot1_p2_color]
      dot1-p2-pol-tc:
        description:
        - CLI C(dot1-p2-pol-tc), profile type ingress-qos. Policer traffic class for pbit 2.
        type: int
        aliases: [dot1_p2_pol_tc]
      dot1-p3-color:
        description:
        - CLI C(dot1-p3-color), profile type ingress-qos. Ingress color for pbit 3.
        type: str
        aliases: [dot1_p3_color]
      dot1-p3-pol-tc:
        description:
        - CLI C(dot1-p3-pol-tc), profile type ingress-qos. Policer traffic class for pbit 3.
        type: int
        aliases: [dot1_p3_pol_tc]
      dot1-p4-color:
        description:
        - CLI C(dot1-p4-color), profile type ingress-qos. Ingress color for pbit 4.
        type: str
        aliases: [dot1_p4_color]
      dot1-p4-pol-tc:
        description:
        - CLI C(dot1-p4-pol-tc), profile type ingress-qos. Policer traffic class for pbit 4.
        type: int
        aliases: [dot1_p4_pol_tc]
      dot1-p5-color:
        description:
        - CLI C(dot1-p5-color), profile type ingress-qos. Ingress color for pbit 5.
        type: str
        aliases: [dot1_p5_color]
      dot1-p5-pol-tc:
        description:
        - CLI C(dot1-p5-pol-tc), profile type ingress-qos. Policer traffic class for pbit 5.
        type: int
        aliases: [dot1_p5_pol_tc]
      dot1-p6-color:
        description:
        - CLI C(dot1-p6-color), profile type ingress-qos. Ingress color for pbit 6.
        type: str
        aliases: [dot1_p6_color]
      dot1-p6-pol-tc:
        description:
        - CLI C(dot1-p6-pol-tc), profile type ingress-qos. Policer traffic class for pbit 6.
        type: int
        aliases: [dot1_p6_pol_tc]
      dot1-p7-color:
        description:
        - CLI C(dot1-p7-color), profile type ingress-qos. Ingress color for pbit 7.
        type: str
        aliases: [dot1_p7_color]
      dot1-p7-pol-tc:
        description:
        - CLI C(dot1-p7-pol-tc), profile type ingress-qos. Policer traffic class for pbit 7.
        type: int
        aliases: [dot1_p7_pol_tc]
      attributes:
        type: list
        elements: str
        description: Raw profile subcommands for complex or not-yet-modeled nested values.
  running_config:
    type: str
    description: Output from C(info configure qos profiles), used with state C(parsed).
  state:
    description:
    - Desired resource state.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(profile_type) and C(name) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
    - All changes to one profile are sent as one command (the mandatory parameters followed by the changes), as the device validates parameters that depend on each other together.
    - The device does not allow changing the type of an existing shaper profile; the module fails before sending such a change (delete and create the profile instead).
    type: str
    default: merged
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
"""

EXAMPLES = """
- name: Gather QoS profiles
  nokia.isam.isam_qos_profiles:
    state: gathered

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_qos_profiles:
    state: gathered
    config:
      - profile_type: queue
        name: Q_BE
      - profile_type: marker-d1p
        name: FD_Marker_BE

- name: Render a queue profile
  nokia.isam.isam_qos_profiles:
    state: rendered
    config:
      - profile_type: queue
        name: FD_BEQ
        queue-type: red:24:48:80
"""

RETURN = """
extends_documentation_fragment: nokia.isam.read_outcomes
before:
  description: Configuration prior to module execution.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
after:
  description: Configuration after module execution.
  returned: when changed
  type: list
commands:
  description: Commands sent to the device or produced in check mode.
  returned: when state is merged, replaced, overridden, or deleted
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered structured QoS profile data.
  returned: when state is gathered
  type: list
parsed:
  description: Parsed structured QoS profile data.
  returned: when state is parsed
  type: list
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_profiles.qos_profiles import (
    Qos_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.qos_profiles.qos_profiles import (
    Qos_profiles,
)


def main():
    module = AnsibleModule(
        argument_spec=Qos_profilesArgs.argument_spec,
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
    result = Qos_profiles(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
