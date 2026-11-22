#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: isam_xdsl_profiles
short_description: Manages Nokia ISAM XDSL profile resources.
description:
  - Manages C(configure xdsl) service-profile, spectrum-profile, dpbo-profile,
    vect-profile, and vce-profile configuration.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    type: dict
    description: Grouped XDSL profile configuration.
    suboptions:
      service_profiles:
        type: list
        elements: dict
        description: Service profile configuration entries (C(configure xdsl service-profile)). The set/removal forms follow the device's flat C(info configure detail flat) output (C(<keyword> <value>), C(no <keyword>)); they are not verified against a device.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          ra_mode_down:
            type: str
            description: Value of C(ra-mode-down); C(no ra-mode-down) (the default) is not reported.
          ra_mode_up:
            type: str
            description: Value of C(ra-mode-up); C(no ra-mode-up) (the default) is not reported.
          min_bitrate_down:
            type: int
            description: Value of C(min-bitrate-down); C(no min-bitrate-down) (the default) is not reported.
          min_bitrate_up:
            type: int
            description: Value of C(min-bitrate-up); C(no min-bitrate-up) (the default) is not reported.
          sos_minbitrate_dn:
            type: int
            description: Value of C(sos-minbitrate-dn); C(no sos-minbitrate-dn) (the default) is not reported.
          sos_minbitrate_up:
            type: int
            description: Value of C(sos-minbitrate-up); C(no sos-minbitrate-up) (the default) is not reported.
          plan_bitrate_down:
            type: int
            description: Value of C(plan-bitrate-down); C(no plan-bitrate-down) (the default) is not reported.
          plan_bitrate_up:
            type: int
            description: Value of C(plan-bitrate-up); C(no plan-bitrate-up) (the default) is not reported.
          max_bitrate_down:
            type: int
            description: Maximum downstream bitrate.
          max_bitrate_up:
            type: int
            description: Maximum upstream bitrate.
          max_delay_down:
            type: int
            description: Maximum downstream delay.
          max_delay_up:
            type: int
            description: Maximum upstream delay.
          max_delay_var_dn:
            type: int
            description: Value of C(max-delay-var-dn); C(no max-delay-var-dn) (the default) is not reported.
          max_delay_var_up:
            type: int
            description: Value of C(max-delay-var-up); C(no max-delay-var-up) (the default) is not reported.
          memory_down:
            type: int
            description: Value of C(memory-down); C(no memory-down) (the default) is not reported.
          imp_noise_prot_dn:
            type: int
            description: Value of C(imp-noise-prot-dn); C(no imp-noise-prot-dn) (the default) is not reported.
          imp_noise_prot_up:
            type: int
            description: Value of C(imp-noise-prot-up); C(no imp-noise-prot-up) (the default) is not reported.
          inp8_dn:
            type: int
            description: Value of C(inp8-dn); C(no inp8-dn) (the default) is not reported.
          inp8_up:
            type: int
            description: Value of C(inp8-up); C(no inp8-up) (the default) is not reported.
          inp_wo_erasure_dn:
            type: int
            description: Value of C(inp-wo-erasure-dn); C(no inp-wo-erasure-dn) (the default) is not reported.
          inp_wo_erasure_up:
            type: int
            description: Value of C(inp-wo-erasure-up); C(no inp-wo-erasure-up) (the default) is not reported.
          min_l2_br_down:
            type: int
            description: Value of C(min-l2-br-down); C(no min-l2-br-down) (the default) is not reported.
          active:
            type: bool
            description: Whether the profile is active (C(active), C(no active) when false).
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile, relative to it (for example C(vdsl2 foo 1)). Commands the options model are folded into them when comparing; facts only return keywords the options do not model.
      spectrum_profiles:
        type: list
        elements: dict
        description: Spectrum profile configuration entries (C(configure xdsl spectrum-profile)). The set/removal forms follow the device's flat C(info configure detail flat) output (C(<keyword> <value>), C(no <keyword>)); they are not verified against a device.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          dis_ansi_t1413:
            type: bool
            description: Disable ANSI T1.413 mode.
          dis_etsi_dts:
            type: bool
            description: Disable ETSI DTS mode.
          dis_g992_1_a:
            type: bool
            description: Disable G.992.1 Annex A mode.
          dis_g992_1_b:
            type: bool
            description: Disable G.992.1 Annex B mode.
          dis_g992_2_a:
            type: bool
            description: Disable G.992.2 Annex A mode.
          dis_g992_3_a:
            type: bool
            description: Disable G.992.3 Annex A mode.
          dis_g992_3_b:
            type: bool
            description: Disable G.992.3 Annex B mode.
          g992_3_aj:
            type: bool
            description: Sets C(g992-3-aj) (C(no g992-3-aj) when false; default off).
          g992_3_l1:
            type: bool
            description: Sets C(g992-3-l1) (C(no g992-3-l1) when false; default off).
          g992_3_l2:
            type: bool
            description: Sets C(g992-3-l2) (C(no g992-3-l2) when false; default off).
          g992_3_am:
            type: bool
            description: Sets C(g992-3-am) (C(no g992-3-am) when false; default off).
          g992_5_a:
            type: bool
            description: Sets C(g992-5-a) (C(no g992-5-a) when false; default off).
          g992_5_b:
            type: bool
            description: Enable G.992.5 Annex B mode.
          ansi_t1_424:
            type: bool
            description: Sets C(ansi-t1.424) (C(no ansi-t1.424) when false; default off).
          dis_etsi_ts:
            type: bool
            description: Disable ETSI TS mode.
          itu_g993_1:
            type: bool
            description: Sets C(itu-g993-1) (C(no itu-g993-1) when false; default off).
          ieee_802_3ah:
            type: bool
            description: Sets C(ieee-802.3ah) (C(no ieee-802.3ah) when false; default off).
          g992_5_aj:
            type: bool
            description: Enable G.992.5 Annex AJ mode.
          g992_5_am:
            type: bool
            description: Sets C(g992-5-am) (C(no g992-5-am) when false; default off).
          g993_2_8a:
            type: bool
            description: Sets C(g993-2-8a) (C(no g993-2-8a) when false; default off).
          g993_2_8b:
            type: bool
            description: Sets C(g993-2-8b) (C(no g993-2-8b) when false; default off).
          g993_2_8c:
            type: bool
            description: Sets C(g993-2-8c) (C(no g993-2-8c) when false; default off).
          g993_2_8d:
            type: bool
            description: Sets C(g993-2-8d) (C(no g993-2-8d) when false; default off).
          g993_2_12a:
            type: bool
            description: Sets C(g993-2-12a) (C(no g993-2-12a) when false; default off).
          g993_2_12b:
            type: bool
            description: Sets C(g993-2-12b) (C(no g993-2-12b) when false; default off).
          g993_2_17a:
            type: bool
            description: Enable G.993.2 profile 17a mode.
          g993_2_30a:
            type: bool
            description: Sets C(g993-2-30a) (C(no g993-2-30a) when false; default off).
          g993_2_35b:
            type: bool
            description: Sets C(g993-2-35b) (C(no g993-2-35b) when false; default off).
          min_noise_down:
            type: int
            description: Value of C(min-noise-down); C(no min-noise-down) (the default) is not reported.
          min_noise_up:
            type: int
            description: Value of C(min-noise-up); C(no min-noise-up) (the default) is not reported.
          trgt_noise_down:
            type: int
            description: Value of C(trgt-noise-down); C(no trgt-noise-down) (the default) is not reported.
          trgt_noise_up:
            type: int
            description: Value of C(trgt-noise-up); C(no trgt-noise-up) (the default) is not reported.
          max_noise_down:
            type: int
            description: Value of C(max-noise-down); C(no max-noise-down) (the default) is not reported.
          max_noise_up:
            type: int
            description: Value of C(max-noise-up); C(no max-noise-up) (the default) is not reported.
          carrier_mask_down:
            type: str
            description: Value of C(carrier-mask-down); C(no carrier-mask-down) (the default) is not reported.
          carrier_mask_up:
            type: str
            description: Value of C(carrier-mask-up); C(no carrier-mask-up) (the default) is not reported.
          rf_band_list:
            type: str
            description: RF band list value.
          power_mgnt_mode:
            type: str
            description: Value of C(power_mgnt_mode); C(no power_mgnt_mode) (the default) is not reported.
          l0_time:
            type: int
            description: Value of C(l0-time); C(no l0-time) (the default) is not reported.
          l2_time:
            type: int
            description: Value of C(l2-time); C(no l2-time) (the default) is not reported.
          l2_agpow_red_tx:
            type: int
            description: Value of C(l2-agpow-red-tx); C(no l2-agpow-red-tx) (the default) is not reported.
          modification:
            type: str
            description: Value of C(modification); C(no modification) (the default) is not reported.
          rau_noise_down:
            type: int
            description: Value of C(rau-noise-down); C(no rau-noise-down) (the default) is not reported.
          rau_noise_up:
            type: int
            description: Value of C(rau-noise-up); C(no rau-noise-up) (the default) is not reported.
          rau_time_down:
            type: int
            description: Value of C(rau-time-down); C(no rau-time-down) (the default) is not reported.
          rau_time_up:
            type: int
            description: Value of C(rau-time-up); C(no rau-time-up) (the default) is not reported.
          rad_noise_down:
            type: int
            description: Value of C(rad-noise-down); C(no rad-noise-down) (the default) is not reported.
          rad_noise_up:
            type: int
            description: Value of C(rad-noise-up); C(no rad-noise-up) (the default) is not reported.
          rad_time_down:
            type: int
            description: Value of C(rad-time-down); C(no rad-time-down) (the default) is not reported.
          rad_time_up:
            type: int
            description: Value of C(rad-time-up); C(no rad-time-up) (the default) is not reported.
          l2_agpw_to_red_tx:
            type: int
            description: Value of C(l2-agpw-to-red-tx); C(no l2-agpw-to-red-tx) (the default) is not reported.
          active:
            type: bool
            description: Whether the profile is active (C(active), C(no active) when false).
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile, relative to it (for example C(vdsl2 foo 1)). Commands the options model are folded into them when comparing; facts only return keywords the options do not model.
          adsl_adsl2:
            type: dict
            description: The C(adsl-adsl2) sub-node.
            suboptions:
              propr_feat_value:
                type: str
                description: Value of C(adsl-adsl2 propr-feat-value); C(no propr-feat-value) (the default) is not reported.
              max_agpowlev_down:
                type: int
                description: Value of C(adsl-adsl2 max-agpowlev-down); C(no max-agpowlev-down) (the default) is not reported.
              max_agpowlev_up:
                type: int
                description: Value of C(adsl-adsl2 max-agpowlev-up); C(no max-agpowlev-up) (the default) is not reported.
              max_psd_down:
                type: int
                description: Value of C(adsl-adsl2 max-psd-down); C(no max-psd-down) (the default) is not reported.
              max_psd_up:
                type: int
                description: Value of C(adsl-adsl2 max-psd-up); C(no max-psd-up) (the default) is not reported.
              pbo_mode_up:
                type: str
                description: Value of C(adsl-adsl2 pbo-mode-up); C(no pbo-mode-up) (the default) is not reported.
              max_recv_power_up:
                type: int
                description: Value of C(adsl-adsl2 max-recv-power-up); C(no max-recv-power-up) (the default) is not reported.
              psd_mask_up:
                type: str
                description: Value of C(adsl-adsl2 psd-mask-up); C(no psd-mask-up) (the default) is not reported.
          re_adsl:
            type: dict
            description: The C(re-adsl) sub-node.
            suboptions:
              propr_feat_value:
                type: str
                description: Value of C(re-adsl propr-feat-value); C(no propr-feat-value) (the default) is not reported.
              max_agpowlev_down:
                type: int
                description: Value of C(re-adsl max-agpowlev-down); C(no max-agpowlev-down) (the default) is not reported.
              max_agpowlev_up:
                type: int
                description: Value of C(re-adsl max-agpowlev-up); C(no max-agpowlev-up) (the default) is not reported.
              max_psd_down:
                type: int
                description: Value of C(re-adsl max-psd-down); C(no max-psd-down) (the default) is not reported.
              max_psd_up:
                type: int
                description: Value of C(re-adsl max-psd-up); C(no max-psd-up) (the default) is not reported.
              pbo_mode_up:
                type: str
                description: Value of C(re-adsl pbo-mode-up); C(no pbo-mode-up) (the default) is not reported.
              max_recv_power_up:
                type: int
                description: Value of C(re-adsl max-recv-power-up); C(no max-recv-power-up) (the default) is not reported.
          adsl2_plus:
            type: dict
            description: The C(adsl2-plus) sub-node.
            suboptions:
              propr_feat_value:
                type: str
                description: Value of C(adsl2-plus propr-feat-value); C(no propr-feat-value) (the default) is not reported.
              max_agpowlev_down:
                type: int
                description: Value of C(adsl2-plus max-agpowlev-down); C(no max-agpowlev-down) (the default) is not reported.
              max_agpowlev_up:
                type: int
                description: Value of C(adsl2-plus max-agpowlev-up); C(no max-agpowlev-up) (the default) is not reported.
              max_psd_down:
                type: int
                description: Value of C(adsl2-plus max-psd-down); C(no max-psd-down) (the default) is not reported.
              max_psd_up:
                type: int
                description: Value of C(adsl2-plus max-psd-up); C(no max-psd-up) (the default) is not reported.
              psd_shape_down:
                type: str
                description: Value of C(adsl2-plus psd-shape-down); C(no psd-shape-down) (the default) is not reported.
              pbo_mode_up:
                type: str
                description: Value of C(adsl2-plus pbo-mode-up); C(no pbo-mode-up) (the default) is not reported.
              max_recv_power_up:
                type: int
                description: Value of C(adsl2-plus max-recv-power-up); C(no max-recv-power-up) (the default) is not reported.
              psd_mask_up:
                type: str
                description: Value of C(adsl2-plus psd-mask-up); C(no psd-mask-up) (the default) is not reported.
              cust_psd_pt_down:
                type: list
                elements: dict
                description: The indexed C(adsl2-plus cust-psd-pt-down <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
          vdsl:
            type: dict
            description: The C(vdsl) sub-node.
            suboptions:
              propr_feat_value:
                type: str
                description: Value of C(vdsl propr-feat-value); C(no propr-feat-value) (the default) is not reported.
              vdsl_band_plan:
                type: str
                description: Value of C(vdsl vdsl-band-plan); C(no vdsl-band-plan) (the default) is not reported.
              optional_band:
                type: str
                description: Value of C(vdsl optional-band); C(no optional-band) (the default) is not reported.
              optional_endfreq:
                type: int
                description: Value of C(vdsl optional-endfreq); C(no optional-endfreq) (the default) is not reported.
              adsl_band:
                type: str
                description: Value of C(vdsl adsl-band); C(no adsl-band) (the default) is not reported.
              max_agpowlev_down:
                type: int
                description: Value of C(vdsl max-agpowlev-down); C(no max-agpowlev-down) (the default) is not reported.
              max_agpowlev_up:
                type: int
                description: Value of C(vdsl max-agpowlev-up); C(no max-agpowlev-up) (the default) is not reported.
              psd_shape_down:
                type: str
                description: Value of C(vdsl psd-shape-down); C(no psd-shape-down) (the default) is not reported.
              psd_shape_up:
                type: str
                description: Value of C(vdsl psd-shape-up); C(no psd-shape-up) (the default) is not reported.
              pbo_mode:
                type: str
                description: Value of C(vdsl pbo-mode); C(no pbo-mode) (the default) is not reported.
              rx_psd_shape_up:
                type: str
                description: Value of C(vdsl rx-psd-shape-up); C(no rx-psd-shape-up) (the default) is not reported.
              ghstones_pwr_mode:
                type: str
                description: Value of C(vdsl ghstones-pwr-mode); C(no ghstones-pwr-mode) (the default) is not reported.
              max_band:
                type: str
                description: Value of C(vdsl max-band); C(no max-band) (the default) is not reported.
              max_freq:
                type: int
                description: Value of C(vdsl max-freq); C(no max-freq) (the default) is not reported.
              m_psd_level_down:
                type: int
                description: Value of C(vdsl m-psd-level-down); C(no m-psd-level-down) (the default) is not reported.
              m_psd_level_up:
                type: int
                description: Value of C(vdsl m-psd-level-up); C(no m-psd-level-up) (the default) is not reported.
              psd_pbo_par_a_up:
                type: str
                description: Value of C(vdsl psd-pbo-par-a-up); C(no psd-pbo-par-a-up) (the default) is not reported.
              psd_pbo_par_b_up:
                type: str
                description: Value of C(vdsl psd-pbo-par-b-up); C(no psd-pbo-par-b-up) (the default) is not reported.
              cust_psd_sc_down:
                type: str
                description: Value of C(vdsl cust-psd-sc-down); C(no cust-psd-sc-down) (the default) is not reported.
              cust_psd_ty_down:
                type: str
                description: Value of C(vdsl cust-psd-ty-down); C(no cust-psd-ty-down) (the default) is not reported.
              cust_rx_psd_sc_up:
                type: str
                description: Value of C(vdsl cust-rx-psd-sc-up); C(no cust-rx-psd-sc-up) (the default) is not reported.
              cust_rx_psd_ty_up:
                type: str
                description: Value of C(vdsl cust-rx-psd-ty-up); C(no cust-rx-psd-ty-up) (the default) is not reported.
              opt_startfreq:
                type: int
                description: Value of C(vdsl opt-startfreq); C(no opt-startfreq) (the default) is not reported.
              ghstone_set_pwr_ctrl:
                type: dict
                description: The C(vdsl ghstone-set-pwr-ctrl) sub-node.
                suboptions:
                  a43:
                    type: str
                    description: Value of C(vdsl ghstone-set-pwr-ctrl a43); C(no a43) (the default) is not reported.
                  b43:
                    type: str
                    description: Value of C(vdsl ghstone-set-pwr-ctrl b43); C(no b43) (the default) is not reported.
                  a43c:
                    type: str
                    description: Value of C(vdsl ghstone-set-pwr-ctrl a43c); C(no a43c) (the default) is not reported.
                  v43:
                    type: str
                    description: Value of C(vdsl ghstone-set-pwr-ctrl v43); C(no v43) (the default) is not reported.
              cust_psd_pt_down:
                type: list
                elements: dict
                description: The indexed C(vdsl cust-psd-pt-down <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              cust_rx_psd_pt_up:
                type: list
                elements: dict
                description: The indexed C(vdsl cust-rx-psd-pt-up <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              pbo:
                type: list
                elements: dict
                description: The indexed C(vdsl pbo <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  param_a:
                    type: int
                    description: Value of C(vdsl pbo <index> param-a); C(no param-a) (the default) is not reported.
                  param_b:
                    type: int
                    description: Value of C(vdsl pbo <index> param-b); C(no param-b) (the default) is not reported.
          vdsl2:
            type: dict
            description: The C(vdsl2) sub-node.
            suboptions:
              propr_feat_value:
                type: str
                description: Value of C(vdsl2 propr-feat-value); C(no propr-feat-value) (the default) is not reported.
              max_agpowlev_down:
                type: int
                description: Value of C(vdsl2 max-agpowlev-down); C(no max-agpowlev-down) (the default) is not reported.
              max_agpowlev_up:
                type: int
                description: Value of C(vdsl2 max-agpowlev-up); C(no max-agpowlev-up) (the default) is not reported.
              psd_shape_down:
                type: str
                description: Value of C(vdsl2 psd-shape-down); C(no psd-shape-down) (the default) is not reported.
              cs_psd_shape_dn:
                type: str
                description: Value of C(vdsl2 cs-psd-shape-dn); C(no cs-psd-shape-dn) (the default) is not reported.
              cs_psd_shape_up:
                type: str
                description: Value of C(vdsl2 cs-psd-shape-up); C(no cs-psd-shape-up) (the default) is not reported.
              psd_shape_up:
                type: str
                description: Value of C(vdsl2 psd-shape-up); C(no psd-shape-up) (the default) is not reported.
              rx_psd_shape_up:
                type: str
                description: Value of C(vdsl2 rx-psd-shape-up); C(no rx-psd-shape-up) (the default) is not reported.
              psd_pbo_e_len_up:
                type: str
                description: Value of C(vdsl2 psd-pbo-e-len-up); C(no psd-pbo-e-len-up) (the default) is not reported.
              m_psd_level_down:
                type: int
                description: Value of C(vdsl2 m-psd-level-down); C(no m-psd-level-down) (the default) is not reported.
              m_psd_level_up:
                type: int
                description: Value of C(vdsl2 m-psd-level-up); C(no m-psd-level-up) (the default) is not reported.
              psd_pbo_par_a_up:
                type: str
                description: Value of C(vdsl2 psd-pbo-par-a-up); C(no psd-pbo-par-a-up) (the default) is not reported.
              psd_pbo_par_b_up:
                type: str
                description: Value of C(vdsl2 psd-pbo-par-b-up); C(no psd-pbo-par-b-up) (the default) is not reported.
              v_noise_snr_down:
                type: str
                description: Value of C(vdsl2 v-noise-snr-down); C(no v-noise-snr-down) (the default) is not reported.
              v_noise_snr_up:
                type: str
                description: Value of C(vdsl2 v-noise-snr-up); C(no v-noise-snr-up) (the default) is not reported.
              v_noise_psd_down:
                type: str
                description: Value of C(vdsl2 v-noise-psd-down); C(no v-noise-psd-down) (the default) is not reported.
              v_noise_psd_up:
                type: str
                description: Value of C(vdsl2 v-noise-psd-up); C(no v-noise-psd-up) (the default) is not reported.
              cust_psd_sc_down:
                type: str
                description: Value of C(vdsl2 cust-psd-sc-down); C(no cust-psd-sc-down) (the default) is not reported.
              cust_psd_ty_down:
                type: str
                description: Value of C(vdsl2 cust-psd-ty-down); C(no cust-psd-ty-down) (the default) is not reported.
              cust_psd_sc_up:
                type: str
                description: Value of C(vdsl2 cust-psd-sc-up); C(no cust-psd-sc-up) (the default) is not reported.
              cust_psd_ty_up:
                type: str
                description: Value of C(vdsl2 cust-psd-ty-up); C(no cust-psd-ty-up) (the default) is not reported.
              cust_rx_psd_sc_up:
                type: str
                description: Value of C(vdsl2 cust-rx-psd-sc-up); C(no cust-rx-psd-sc-up) (the default) is not reported.
              cust_rx_psd_ty_up:
                type: str
                description: Value of C(vdsl2 cust-rx-psd-ty-up); C(no cust-rx-psd-ty-up) (the default) is not reported.
              upbo_aele_mode:
                type: str
                description: Value of C(vdsl2 upbo-aele-mode); C(no upbo-aele-mode) (the default) is not reported.
              upboaele_min_thrs:
                type: int
                description: Value of C(vdsl2 upboaele-min-thrs); C(no upboaele-min-thrs) (the default) is not reported.
              short_loop_lr:
                type: str
                description: Value of C(vdsl2 short-loop-lr); C(no short-loop-lr) (the default) is not reported.
              medium_loop_lr:
                type: str
                description: Value of C(vdsl2 medium-loop-lr); C(no medium-loop-lr) (the default) is not reported.
              long_loop_lr:
                type: str
                description: Value of C(vdsl2 long-loop-lr); C(no long-loop-lr) (the default) is not reported.
              cust_psd_pt_down:
                type: list
                elements: dict
                description: The indexed C(vdsl2 cust-psd-pt-down <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              cust_psd_pt_up:
                type: list
                elements: dict
                description: The indexed C(vdsl2 cust-psd-pt-up <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              cust_rx_psd_pt_up:
                type: list
                elements: dict
                description: The indexed C(vdsl2 cust-rx-psd-pt-up <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              v_noise_psd_pt_down:
                type: list
                elements: dict
                description: The indexed C(vdsl2 v-noise-psd-pt-down <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              v_noise_psd_pt_up:
                type: list
                elements: dict
                description: The indexed C(vdsl2 v-noise-psd-pt-up <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  frequency:
                    type: int
                    description: Breakpoint frequency (C(frequency)).
                  psd:
                    type: int
                    description: Breakpoint PSD level (C(psd)).
              pbo:
                type: list
                elements: dict
                description: The indexed C(vdsl2 pbo <index>) sub-nodes; entries with every attribute at its default are not reported.
                suboptions:
                  index:
                    type: int
                    required: true
                    description: Entry index (the identity of the indexed sub-node).
                  equal_fext:
                    type: int
                    description: Value of C(vdsl2 pbo <index> equal-fext); C(no equal-fext) (the default) is not reported.
                  param_a:
                    type: int
                    description: Value of C(vdsl2 pbo <index> param-a); C(no param-a) (the default) is not reported.
                  param_b:
                    type: int
                    description: Value of C(vdsl2 pbo <index> param-b); C(no param-b) (the default) is not reported.
          artificial_noise_down:
            type: list
            elements: dict
            description: The indexed C(artificial-noise-down <index>) sub-nodes; entries with every attribute at its default are not reported.
            suboptions:
              index:
                type: int
                required: true
                description: Entry index (the identity of the indexed sub-node).
              frequency:
                type: int
                description: Breakpoint frequency (C(frequency)).
              psd:
                type: int
                description: Breakpoint PSD level (C(psd)).
      dpbo_profiles:
        type: list
        elements: dict
        description: DPBO profile configuration entries (C(configure xdsl dpbo-profile)). The set/removal forms follow the device's flat C(info configure detail flat) output (C(<keyword> <value>), C(no <keyword>)); they are not verified against a device.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          es_elect_length:
            type: int
            description: E-side electrical length.
          es_cable_model_a:
            type: int
            description: E-side cable model A value.
          es_cable_model_b:
            type: int
            description: E-side cable model B value.
          es_cable_model_c:
            type: int
            description: E-side cable model C value.
          min_usable_signal:
            type: int
            description: Minimum usable signal value.
          min_frequency:
            type: int
            description: Minimum frequency.
          max_frequency:
            type: int
            description: Maximum frequency.
          rs_elect_length:
            type: int
            description: R-side electrical length.
          muf_control:
            type: str
            description: Value of C(muf-control); C(no muf-control) (the default) is not reported.
          offset:
            type: int
            description: Value of C(offset); C(no offset) (the default) is not reported.
          modification:
            type: str
            description: Value of C(modification); C(no modification) (the default) is not reported.
          active:
            type: bool
            description: Whether the profile is active (C(active), C(no active) when false).
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile, relative to it (for example C(vdsl2 foo 1)). Commands the options model are folded into them when comparing; facts only return keywords the options do not model.
          micpsd_pt_down:
            type: list
            elements: dict
            description: The indexed C(micpsd-pt-down <index>) sub-nodes; entries with every attribute at its default are not reported.
            suboptions:
              index:
                type: int
                required: true
                description: Entry index (the identity of the indexed sub-node).
              frequency:
                type: int
                description: Breakpoint frequency (C(frequency)).
              psd:
                type: int
                description: Breakpoint PSD level (C(psd)).
          epsd_pt_down:
            type: list
            elements: dict
            description: The indexed C(epsd-pt-down <index>) sub-nodes; entries with every attribute at its default are not reported.
            suboptions:
              index:
                type: int
                required: true
                description: Entry index (the identity of the indexed sub-node).
              frequency:
                type: int
                description: Breakpoint frequency (C(frequency)).
              psd:
                type: int
                description: Breakpoint PSD level (C(psd)).
      vect_profiles:
        type: list
        elements: dict
        description: Vectoring profile configuration entries (C(configure xdsl vect-profile)). The set/removal forms follow the device's flat C(info configure detail flat) output (C(<keyword> <value>), C(no <keyword>)); they are not verified against a device.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          fext_cancel_up:
            type: bool
            description: Sets C(fext-cancel-up) (C(no fext-cancel-up) when false; default off).
          fext_cancel_dn:
            type: bool
            description: Sets C(fext-cancel-dn) (C(no fext-cancel-dn) when false; default off).
          leg_can_dn_m1:
            type: bool
            description: Sets C(leg-can-dn-m1) (C(no leg-can-dn-m1) when false; default off).
          leg_can_dn_m2:
            type: bool
            description: Sets C(leg-can-dn-m2) (C(no leg-can-dn-m2) when false; default off).
          dis_gvect_cpe:
            type: bool
            description: Sets C(dis-gvect-cpe) (C(no dis-gvect-cpe) when false; default off).
          gvecfriend_cpe:
            type: bool
            description: Sets C(gvecfriend-cpe) (C(no gvecfriend-cpe) when false; default off).
          gvecfriend_dn_cpe:
            type: bool
            description: Sets C(gvecfriend-dn-cpe) (C(no gvecfriend-dn-cpe) when false; default off).
          legacy_cpe:
            type: bool
            description: Sets C(legacy-cpe) (C(no legacy-cpe) when false; default off).
          band_control_up:
            type: str
            description: Upstream band control value.
          band_control_dn:
            type: str
            description: Downstream band control value.
          vect_leav_thresh:
            type: int
            description: Value of C(vect-leav-thresh); C(no vect-leav-thresh) (the default) is not reported.
          vect_feat_bitmap:
            type: str
            description: Value of C(vect-feat-bitmap); C(no vect-feat-bitmap) (the default) is not reported.
          legacy_upbo:
            type: bool
            description: Sets C(legacy-upbo) (C(no legacy-upbo) when false; default off).
          modification:
            type: str
            description: Value of C(modification); C(no modification) (the default) is not reported.
          active:
            type: bool
            description: Whether the profile is active (C(active), C(no active) when false).
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile, relative to it (for example C(vdsl2 foo 1)). Commands the options model are folded into them when comparing; facts only return keywords the options do not model.
      vce_profiles:
        type: list
        elements: dict
        description: VCE profile configuration entries (C(configure xdsl vce-profile)). The set/removal forms follow the device's flat C(info configure detail flat) output (C(<keyword> <value>), C(no <keyword>)); they are not verified against a device.
        suboptions:
          id:
            type: int
            required: true
            description: Profile identifier.
          name:
            type: str
            description: Profile name.
          version:
            type: int
            description: Profile version.
          vce_gain_mode:
            type: str
            description: Value of C(vce-gain-mode); C(no vce-gain-mode) (the default) is not reported.
          vce_join_timeout:
            type: str
            description: VCE join timeout value.
          vce_min_par_join:
            type: str
            description: Value of C(vce-min-par-join); C(no vce-min-par-join) (the default) is not reported.
          vce_hist_pcoder:
            type: str
            description: Value of C(vce-hist-pcoder); C(no vce-hist-pcoder) (the default) is not reported.
          vce_band_plan:
            type: str
            description: Value of C(vce-band-plan); C(no vce-band-plan) (the default) is not reported.
          vce_max_vect_freq:
            type: str
            description: Value of C(vce-max-vect-freq); C(no vce-max-vect-freq) (the default) is not reported.
          modification:
            type: str
            description: Value of C(modification); C(no modification) (the default) is not reported.
          active:
            type: bool
            description: Whether the profile is active (C(active), C(no active) when false).
          commands:
            type: list
            elements: str
            description: Additional device-native commands for the profile, relative to it (for example C(vdsl2 foo 1)). Commands the options model are folded into them when comparing; facts only return keywords the options do not model.
  running_config:
    type: str
    description: Device-native C(info configure xdsl ...) output for parsed state.
  state:
    type: str
    description:
      - Desired resource state.
      - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by C(dpbo_profiles[].id) and C(service_profiles[].id) and C(spectrum_profiles[].id) and C(vce_profiles[].id) and C(vect_profiles[].id) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with nothing configured answers like an absent one and is not returned either. Without I(config) the whole resource is read.
      - With C(deleted) and I(config), only the profiles named in I(config) are deleted or reset; profile types not named are left alone. Without I(config) everything is deleted.
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """
- nokia.isam.isam_xdsl_profiles:
    config:
      service_profiles:
        - id: 11
          name: HSI-30-Private
          version: 1
          max_bitrate_down: 33000
          max_bitrate_up: 5500
          active: true
    state: merged

- name: Read only the named instances (targeted gathering)
  nokia.isam.isam_xdsl_profiles:
    config:
      service_profiles:
        - id: 11
      spectrum_profiles:
        - id: 2
    state: gathered
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
commands:
  description: Commands sent to the device.
  returned: when changed
  type: list
rendered:
  description: Rendered device-native commands.
  returned: when state is rendered
  type: list
gathered:
  description: Gathered XDSL profile facts.
  returned: when state is gathered
  type: dict
parsed:
  description: Parsed XDSL profile facts.
  returned: when state is parsed
  type: dict
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.xdsl_profiles.xdsl_profiles import (
    Xdsl_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_profiles.xdsl_profiles import (
    Xdsl_profiles,
)


def main():
    module = AnsibleModule(
        argument_spec=Xdsl_profilesArgs.argument_spec,
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

    # Every state goes through the config class (gathered/parsed via Facts, as in the other modules).
    result = Xdsl_profiles(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
