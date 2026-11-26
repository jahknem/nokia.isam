# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Attribute table of the isam_voice_sip resource (global SIP voice settings).

The device prints each node as one packed line ('info configure voice sip detail
flat', lab ISAM), e.g.::

    configure voice sip vsp vsp1 domain-name DomainName.com no admin-status no ta4 ...
    configure voice sip system session-timer no status no min-se-time no se-time no admin-status
    configure voice sip statistics stats-config per-line per-board no out-180-rsp ...

TABLE (CLI guide) drives the facts, the config class and the argument spec (see
attribute_table.py). The statistics counters live on their own CLI node
``statistics stats-config`` (``node=``); values without a removal form, mandatory at
creation (vsp domain-name, cas-nsm-prof prefixes), are ``removable=False``.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import (
    Attr,
    AttributeTable,
    Node,
    TableTemplate,
)

TABLE = AttributeTable("configure voice sip", (
    Node("lineid_syn_prof", "lineid-syn-prof", (
        Attr("syntax_pattern", "syntax-pattern", "str", "terminationuriordn", ["rpregisterdialog", "rpregister", "physicallineid", "terminationuriordn"]),
        Attr("pots_syntax", "pots-syntax", "str"),
        Attr("isdn_syntax", "isdn-syntax", "str"),
        Attr("cas_r2_syntax", "cas-r2-syntax", "str"),
        Attr("cas_r1_syntax", "cas-r1-syntax", "str"),
    ), identity="name"),
    Node("vsp", "vsp", (
        Attr("domain_name", "domain-name", "str", removable=False),
        Attr("admin_status", "admin-status", "str", "down", ["up", "down"]),
        Attr("tinfo", "tinfo", "int", 1000),
        Attr("ta4", "ta4", "int", 4000),
        Attr("ttir1", "ttir1", "int", 100),
        Attr("t_acm_delta", "t-acm-delta", "int", 18000),
        Attr("access_held_time", "access-held-time", "int", 600),
        Attr("awaiting_time", "awaiting-time", "int", 60),
        Attr("digit_send_mode", "digit-send-mode", "str", "en-bloc", ["en-bloc", "overlap-invite", "overlap-indialog"]),
        Attr("overlap_484_act", "overlap-484-act", "str", "release-call", ["release-call", "continue"]),
        Attr("dmpm_intdgt_expid", "dmpm-intdgt-expid", "str", "send-invite", ["send-invite", "release-call"]),
        Attr("dial_start_timer", "dial-start-timer", "int", 10),
        Attr("dial_long_timer", "dial-long-timer", "int", 20),
        Attr("dial_short_timer", "dial-short-timer", "int", 5),
        Attr("uri_type", "uri-type", "str", "sip-uri", ["sip-uri", "tel-uri", "sips-uri"]),
        Attr("rfc2833_pl_type", "rfc2833-pl-type", "int", 96),
        Attr("rfc2833_process", "rfc2833-process", "str", "audio", ["audio", "rfc2833", "both", "mandatory-audio"]),
        Attr("min_data_jitter", "min-data-jitter", "int", 50),
        Attr("init_data_jitter", "init-data-jitter", "int", 50),
        Attr("max_data_jitter", "max-data-jitter", "int", 50),
        Attr("release_mode", "release-mode", "str", "normal", ["normal", "caller", "callee", "both"]),
        Attr("dyn_pt_nego_type", "dyn-pt-nego-type", "str", "far-end", ["far-end", "asymmetric"]),
        Attr("vbd_g711a_pl_type", "vbd-g711a-pl-type", "int", 97),
        Attr("vbd_g711u_pl_type", "vbd-g711u-pl-type", "int", 98),
        Attr("vbd_mode", "vbd-mode", "str", "autoswitch", ["autoswitch", "renegotiation", "v152fb-autoswitch", "v152fb-reneg"]),
        Attr("warmline_dl_timer", "warmline-dl-timer", "int", 4),
        Attr("reg_sub", "reg-sub", "str", "disable", ["disable", "enable"]),
        Attr("dtmf_sip_info", "dtmf-sip-info", "str", "disable", ["disable", "enable"]),
        Attr("sub_period", "sub-period", "int", 3600),
        Attr("sub_head_start", "sub-head-start", "int", 600),
        Attr("t38_same_udp", "t38-same-udp", "str", "disable", ["disable", "enable"]),
        Attr("dhcp_option82", "dhcp-option82", "str", "disable", ["enable", "disable"]),
        Attr("sspprofile", "sspprofile", "str"),
        Attr("signaling_ipmode", "signaling-ipmode", "str", "legacy-ipv4", ["legacy-ipv4", "ipv4", "ipv6"]),
        Attr("tls_cafile", "tls-cafile", "str"),
        Attr("media_ipmode", "media-ipmode", "str", "legacy-ipv4", ["legacy-ipv4", "ipv4", "ipv6"]),
        Attr("timer_b", "timer-b", "int", removable=False),
        Attr("timer_f", "timer-f", "int", removable=False),
        Attr("timer_t1", "timer-t1", "int", removable=False),
        Attr("timer_t2", "timer-t2", "int", removable=False),
    ), identity="name", mandatory=("domain_name",)),
    Node("register", "register", (
        Attr("register_uri", "register-uri", "str"),
        Attr("register_intv", "register-intv", "int", 3600),
        Attr("reg_retry_intv", "reg-retry-intv", "int", 60),
        Attr("reg_prev_ava_intv", "reg-prev-ava-intv", "int", 500),
        Attr("reg_head_start", "reg-head-start", "int", 600),
        Attr("reg_start_min", "reg-start-min", "int", 50),
        Attr("init_reg_delay", "init-reg-delay", "int", 180),
    ), identity="name"),
    Node("redundancy", "redundancy", (
        Attr("support_redun", "support-redun", "str", "disable", ["enable", "disable"]),
        Attr("dns_purge_timer", "dns-purge-timer", "int", 86400),
        Attr("dns_ini_retr_int", "dns-ini-retr-int", "int", 500),
        Attr("dns_max_retr_nbr", "dns-max-retr-nbr", "int", 2),
        Attr("fg_monitor_method", "fg-monitor-method", "str", "register-method", ["register-method", "options-method", "passive-heartbeat"]),
        Attr("fg_monitor_int", "fg-monitor-int", "int", 90),
        Attr("bg_monitor_method", "bg-monitor-method", "str", "options-method", ["options-method"]),
        Attr("bg_monitor_int", "bg-monitor-int", "int", 3600),
        Attr("stable_obs_period", "stable-obs-period", "int", 21600),
        Attr("fo_hystersis", "fo-hystersis", "int", 0),
        Attr("del_upd_threshold", "del-upd-threshold", "int", 0),
        Attr("auto_server_fo", "auto-server-fo", "str", "disable", ["enable", "disable"]),
        Attr("auto_server_fb", "auto-server-fb", "int", 0),
        Attr("auto_sos_fo", "auto-sos-fo", "str", "disable", ["enable", "disable"]),
        Attr("auto_sos_fb", "auto-sos-fb", "int", 0),
        Attr("rtry_after_thrsh", "rtry-after-thrsh", "int", 0),
        Attr("options_max_fwd", "options-max-fwd", "int", 0),
        Attr("dns_redun_mode", "dns-redun-mode", "str", "dns-redun-primary", ["dns-redun-primary", "dns-redun-success"]),
        Attr("fail_obs_timer", "fail-obs-timer", "int", 240),
        Attr("fg_intv_503", "fg-intv-503", "int", 2),
        Attr("time_thrsh_503", "time-thrsh-503", "int", 0),
        Attr("nbr_thrsh_503", "nbr-thrsh-503", "int", 1),
        Attr("auto_srv_fo_timer", "auto-srv-fo-timer", "int", 86400),
    ), identity="name"),
    Node("system", "system session-timer", (
        Attr("enable", "enable", "flag"),
        Attr("status", "status", "str", "disable", ["enable", "disable", "enable-uas"]),
        Attr("min_se_time", "min-se-time", "int", 90),
        Attr("se_time", "se-time", "int", 1800),
        Attr("admin_status", "admin-status", "str", "down", ["up", "down"]),
    )),
    Node("redundancy_cmd", "redundancy-cmd", (
        Attr("start_time", "start-time", "int", 0),
        Attr("end_time", "end-time", "int", 0),
        Attr("fail_x_type", "fail-x-type", "str", None, ["geo-fail-over", "geo-fail-back"], removable=False),
    ), identity="name"),
    Node("statistics", "statistics", (
        Attr("stats_5min_config", "stats-5min-config", "str", "disable", ["disable", "enable"]),
        Attr("cdr_config", "cdr-config", "str", "disable", ["disable", "enable"]),
        Attr("per_line", "per-line", "flag", node="statistics stats-config"),
        Attr("per_board", "per-board", "flag", node="statistics stats-config"),
        Attr("per_system", "per-system", "flag", node="statistics stats-config"),
        Attr("per_call", "per-call", "flag", node="statistics stats-config"),
        Attr("out_any_rsp", "out-any-rsp", "flag", node="statistics stats-config"),
        Attr("out_180_rsp", "out-180-rsp", "flag", node="statistics stats-config"),
        Attr("out_200_rsp", "out-200-rsp", "flag", node="statistics stats-config"),
        Attr("in_any_rsp", "in-any-rsp", "flag", node="statistics stats-config"),
        Attr("in_180_rsp", "in-180-rsp", "flag", node="statistics stats-config"),
        Attr("in_200_rsp", "in-200-rsp", "flag", node="statistics stats-config"),
    )),
    Node("cas_nsm_prof", "cas-nsm-prof", (
        Attr("version_nbr", "version-nbr", "int", 1),
        Attr("outg_from_no_cgpn", "outg-from-no-cgpn", "str", "impu-gdn", ["impu-gdn", "unavailable"]),
        Attr("international_prefix", "international-prefix", "str", removable=False),
        Attr("national_prefix", "national-prefix", "str"),
        Attr("country_code", "country-code", "str", removable=False),
        Attr("outg_cpn_length", "outg-cpn-length", "int", removable=False),
    ), identity="name", mandatory=("international_prefix", "country_code", "outg_cpn_length")),
))


class Isam_voice_sipTemplate(TableTemplate):
    TABLE = TABLE
