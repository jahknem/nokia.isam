# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    dict_merge,
)
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import (
    ResourceModule,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts import (
    Facts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.voice_sip import (
    Isam_voice_sipTemplate,
)


LINEID_SYN_PROF_FIELDS = [
    ("syntax_pattern", "syntax-pattern", "bool"),
    ("pots_syntax", "pots-syntax", "bool"),
    ("cas_r2_syntax", "cas-r2-syntax", "bool"),
    ("cas_r1_syntax", "cas-r1-syntax", "bool"),
    ("isdn_syntax", "isdn-syntax", "str"),
]

VSP_FIELDS = [
    ("domain_name", "domain-name", "str"),
    ("admin_status", "admin-status", "bool"),
    ("tinfo", "tinfo", "bool"),
    ("ta4", "ta4", "bool"),
    ("ttir1", "ttir1", "bool"),
    ("t_acm_delta", "t-acm-delta", "bool"),
    ("access_held_time", "access-held-time", "bool"),
    ("awaiting_time", "awaiting-time", "bool"),
    ("digit_send_mode", "digit-send-mode", "bool"),
    ("overlap_484_act", "overlap-484-act", "bool"),
    ("dmpm_intdgt_expid", "dmpm-intdgt-expid", "bool"),
    ("dial_start_timer", "dial-start-timer", "bool"),
    ("dial_long_timer", "dial-long-timer", "bool"),
    ("dial_short_timer", "dial-short-timer", "bool"),
    ("uri_type", "uri-type", "bool"),
    ("rfc2833_pl_type", "rfc2833-pl-type", "bool"),
    ("rfc2833_process", "rfc2833-process", "bool"),
    ("min_data_jitter", "min-data-jitter", "bool"),
    ("init_data_jitter", "init-data-jitter", "bool"),
    ("max_data_jitter", "max-data-jitter", "bool"),
    ("release_mode", "release-mode", "bool"),
    ("dyn_pt_nego_type", "dyn-pt-nego-type", "bool"),
    ("vbd_g711a_pl_type", "vbd-g711a-pl-type", "bool"),
    ("vbd_g711u_pl_type", "vbd-g711u-pl-type", "bool"),
    ("vbd_mode", "vbd-mode", "bool"),
    ("warmline_dl_timer", "warmline-dl-timer", "bool"),
    ("reg_sub", "reg-sub", "bool"),
    ("dtmf_sip_info", "dtmf-sip-info", "bool"),
    ("sub_period", "sub-period", "bool"),
    ("sub_head_start", "sub-head-start", "bool"),
    ("t38_same_udp", "t38-same-udp", "bool"),
    ("dhcp_option82", "dhcp-option82", "bool"),
    ("sspprofile", "sspprofile", "bool"),
    ("signaling_ipmode", "signaling-ipmode", "bool"),
    ("tls_cafile", "tls-cafile", "bool"),
    ("media_ipmode", "media-ipmode", "bool"),
    ("timer_b", "timer-b", "int"),
    ("timer_f", "timer-f", "int"),
    ("timer_t1", "timer-t1", "int"),
    ("timer_t2", "timer-t2", "int"),
]

REGISTER_FIELDS = [
    ("register_uri", "register-uri", "bool"),
    ("register_intv", "register-intv", "bool"),
    ("reg_retry_intv", "reg-retry-intv", "bool"),
    ("reg_prev_ava_intv", "reg-prev-ava-intv", "bool"),
    ("reg_head_start", "reg-head-start", "bool"),
    ("reg_start_min", "reg-start-min", "bool"),
    ("init_reg_delay", "init-reg-delay", "bool"),
]

REDUNDANCY_FIELDS = [
    ("support_redun", "support-redun", "bool"),
    ("dns_purge_timer", "dns-purge-timer", "bool"),
    ("dns_ini_retr_int", "dns-ini-retr-int", "bool"),
    ("dns_max_retr_nbr", "dns-max-retr-nbr", "bool"),
    ("fg_monitor_method", "fg-monitor-method", "bool"),
    ("fg_monitor_int", "fg-monitor-int", "bool"),
    ("bg_monitor_method", "bg-monitor-method", "bool"),
    ("bg_monitor_int", "bg-monitor-int", "bool"),
    ("stable_obs_period", "stable-obs-period", "bool"),
    ("fo_hystersis", "fo-hystersis", "bool"),
    ("del_upd_threshold", "del-upd-threshold", "bool"),
    ("auto_server_fo", "auto-server-fo", "bool"),
    ("auto_server_fb", "auto-server-fb", "bool"),
    ("auto_sos_fo", "auto-sos-fo", "bool"),
    ("auto_sos_fb", "auto-sos-fb", "bool"),
    ("rtry_after_thrsh", "rtry-after-thrsh", "bool"),
    ("options_max_fwd", "options-max-fwd", "bool"),
    ("dns_redun_mode", "dns-redun-mode", "bool"),
    ("fail_obs_timer", "fail-obs-timer", "bool"),
    ("fg_intv_503", "fg-intv-503", "bool"),
    ("time_thrsh_503", "time-thrsh-503", "bool"),
    ("nbr_thrsh_503", "nbr-thrsh-503", "bool"),
    ("auto_srv_fo_timer", "auto-srv-fo-timer", "bool"),
]

SYSTEM_FIELDS = [
    ("session_timer", "session-timer", "bool"),
    ("status", "status", "bool"),
    ("min_se_time", "min-se-time", "bool"),
    ("se_time", "se-time", "bool"),
    ("admin_status", "admin-status", "bool"),
]

REDUNDANCY_CMD_FIELDS = [
    ("start_time", "start-time", "bool"),
    ("end_time", "end-time", "bool"),
    ("fail_x_type", "fail-x-type", "str"),
    ("geo_fail_over", "geo-fail-over", "str"),
]

STATISTICS_BOOL_FIELDS = [
    ("stats_5min_config", "stats-5min-config", "bool"),
    ("cdr_config", "cdr-config", "bool"),
]

STATISTICS_CONFIG_FIELDS = [
    ("per_line", "per-line"),
    ("per_board", "per-board"),
    ("per_system", "per-system"),
    ("per_call", "per-call"),
    ("out_any_rsp", "out-any-rsp"),
    ("out_180_rsp", "out-180-rsp"),
    ("out_200_rsp", "out-200-rsp"),
    ("in_any_rsp", "in-any-rsp"),
    ("in_180_rsp", "in-180-rsp"),
    ("in_200_rsp", "in-200-rsp"),
]

CAS_NSM_PROF_FIELDS = [
    ("international_prefix", "international-prefix", "str"),
    ("country_code", "country-code", "str"),
    ("outg_cpn_length", "outg-cpn-length", "int"),
    ("version_nbr", "version-nbr", "bool"),
    ("outg_from_no_cgpn", "outg-from-no-cgpn", "bool"),
    ("national_prefix", "national-prefix", "bool"),
]


class Isam_voice_sip(ResourceModule):
    """The isam_voice_sip config class."""

    def __init__(self, module):
        super(Isam_voice_sip, self).__init__(
            empty_fact_val={},
            facts_module=Facts(module),
            module=module,
            resource="voice_sip",
            tmplt=Isam_voice_sipTemplate(),
        )

    def execute_module(self):
        if self.state == "rendered":
            self.generate_commands()
        elif self.state not in ["parsed", "gathered"]:
            self.generate_commands()
            self.run_commands()
        return self.result

    def addcmd(self, data, tmplt, negate=False):
        # Voice SIP remvals already contain the device's `no` syntax.
        if negate:
            parser = self._tmplt.get_parser(tmplt)
            if parser.get("remval"):
                command = self._tmplt._template(
                    value=parser["remval"],
                    variables=data,
                    fail_on_undefined=False,
                )
                if command:
                    self.commands.extend(command if isinstance(command, list) else [command])
                return
        super(Isam_voice_sip, self).addcmd(data, tmplt, negate)

    def generate_commands(self):
        requested = self.want or {}
        want = requested
        have = self.have or {}

        if self.state == "merged":
            want = dict_merge(have, want)

        if self.state == "deleted" and not requested:
            want = {}

        scoped = self.state in ("replaced", "deleted") and bool(requested)
        if not scoped or "lineid_syn_prof" in requested:
            self._compare_lineid_syn_prof(want.get("lineid_syn_prof", []), have.get("lineid_syn_prof", []))
        if not scoped or "vsp" in requested:
            self._compare_vsp(want.get("vsp", []), have.get("vsp", []))
        if not scoped or "register" in requested:
            self._compare_register(want.get("register", []), have.get("register", []))
        if not scoped or "redundancy" in requested:
            self._compare_redundancy(want.get("redundancy", []), have.get("redundancy", []))
        if not scoped or "system" in requested:
            self._compare_system(want.get("system", {}), have.get("system", {}))
        if not scoped or "redundancy_cmd" in requested:
            self._compare_redundancy_cmd(want.get("redundancy_cmd", []), have.get("redundancy_cmd", []))
        if not scoped or "statistics" in requested:
            self._compare_statistics(want.get("statistics", {}), have.get("statistics", {}))
        if not scoped or "cas_nsm_prof" in requested:
            self._compare_cas_nsm_prof(want.get("cas_nsm_prof", []), have.get("cas_nsm_prof", []))

    def _compare_lineid_syn_prof(self, want, have):
        want_dict = {e["name"]: e for e in want}
        have_dict = {e["name"]: e for e in have}

        if self.state == "deleted":
            for name in (want_dict or have_dict):
                if name in have_dict:
                    self.addcmd(have_dict[name], "lineid_syn_prof", negate=True)
            return
        if self.state in ("replaced", "overridden"):
            for name, entry in have_dict.items():
                if name not in want_dict:
                    self.addcmd(entry, "lineid_syn_prof", negate=True)

        for name, want_entry in want_dict.items():
            have_entry = have_dict.get(name, {})
            cmd = self._build_named_cmd(
                "lineid-syn-prof", name, want_entry, have_entry,
                LINEID_SYN_PROF_FIELDS,
            )
            if cmd:
                self.commands.append(cmd)

    def _compare_vsp(self, want, have):
        want_dict = {e["name"]: e for e in want}
        have_dict = {e["name"]: e for e in have}

        if self.state == "deleted":
            for name in (want_dict or have_dict):
                if name in have_dict:
                    self.addcmd(have_dict[name], "vsp.id", negate=True)
            return
        if self.state in ("replaced", "overridden"):
            for name, entry in have_dict.items():
                if name not in want_dict:
                    self.addcmd(entry, "vsp.id", negate=True)

        for name, want_entry in want_dict.items():
            have_entry = have_dict.get(name, {})
            cmd = self._build_named_cmd(
                "vsp", name, want_entry, have_entry, VSP_FIELDS,
            )
            if cmd:
                self.commands.append(cmd)

    def _compare_register(self, want, have):
        want_dict = {e["name"]: e for e in want}
        have_dict = {e["name"]: e for e in have}

        if self.state == "deleted":
            for name in (want_dict or have_dict):
                if name in have_dict:
                    self.addcmd(have_dict[name], "register.id", negate=True)
            return
        if self.state in ("replaced", "overridden"):
            for name, entry in have_dict.items():
                if name not in want_dict:
                    self.addcmd(entry, "register.id", negate=True)

        for name, want_entry in want_dict.items():
            have_entry = have_dict.get(name, {})
            cmd = self._build_named_cmd(
                "register", name, want_entry, have_entry, REGISTER_FIELDS,
            )
            if cmd:
                self.commands.append(cmd)

    def _compare_redundancy(self, want, have):
        want_dict = {e["name"]: e for e in want}
        have_dict = {e["name"]: e for e in have}

        if self.state == "deleted":
            for name in (want_dict or have_dict):
                if name in have_dict:
                    self.addcmd(have_dict[name], "redundancy.id", negate=True)
            return
        if self.state in ("replaced", "overridden"):
            for name, entry in have_dict.items():
                if name not in want_dict:
                    self.addcmd(entry, "redundancy.id", negate=True)

        for name, want_entry in want_dict.items():
            have_entry = have_dict.get(name, {})
            cmd = self._build_named_cmd(
                "redundancy", name, want_entry, have_entry, REDUNDANCY_FIELDS,
            )
            if cmd:
                self.commands.append(cmd)

    def _compare_system(self, want, have):
        want = want or {}
        have = have or {}

        if self.state in ("replaced", "overridden", "deleted"):
            for py_name, cli_name, ftype in SYSTEM_FIELDS:
                if py_name not in want and have.get(py_name) is True:
                    self.commands.append(
                        "configure voice sip system no %s" % cli_name
                    )

        cmd = self._build_named_cmd("system", None, want, have, SYSTEM_FIELDS)
        if cmd:
            self.commands.append(cmd)

    def _compare_redundancy_cmd(self, want, have):
        want_dict = {e["name"]: e for e in want}
        have_dict = {e["name"]: e for e in have}

        if self.state == "deleted":
            for name in (want_dict or have_dict):
                if name in have_dict:
                    self.addcmd(have_dict[name], "redundancy_cmd.id", negate=True)
            return
        if self.state in ("replaced", "overridden"):
            for name, entry in have_dict.items():
                if name not in want_dict:
                    self.addcmd(entry, "redundancy_cmd.id", negate=True)

        for name, want_entry in want_dict.items():
            have_entry = have_dict.get(name, {})
            cmd = self._build_named_cmd(
                "redundancy-cmd", name, want_entry, have_entry,
                REDUNDANCY_CMD_FIELDS,
            )
            if cmd:
                self.commands.append(cmd)

    def _compare_statistics(self, want, have):
        want = want or {}
        have = have or {}

        if self.state in ("replaced", "overridden", "deleted"):
            for py_name, cli_name, ftype in STATISTICS_BOOL_FIELDS:
                if py_name not in want and have.get(py_name) is True:
                    self.commands.append(
                        "configure voice sip statistics no %s" % cli_name
                    )

        for py_name, cli_name, ftype in STATISTICS_BOOL_FIELDS:
            if py_name in want and want[py_name] != have.get(py_name):
                if want[py_name] is True:
                    self.commands.append(
                        "configure voice sip statistics %s" % cli_name
                    )
                elif want[py_name] is False:
                    self.commands.append(
                        "configure voice sip statistics no %s" % cli_name
                    )

        want_config = {}
        have_config = {}
        for py_name, cli_name in STATISTICS_CONFIG_FIELDS:
            if py_name in want:
                want_config[py_name] = want[py_name]
            if py_name in have:
                have_config[py_name] = have[py_name]

        if self.state == "merged" and want_config:
            merged_config = dict(have_config)
            merged_config.update(want_config)
        else:
            merged_config = want_config

        if merged_config and merged_config != have_config:
            parts = ["configure voice sip statistics stats-config"]
            for py_name, cli_name in STATISTICS_CONFIG_FIELDS:
                if merged_config.get(py_name) is True:
                    parts.append(cli_name)
            self.commands.append(" ".join(parts))

    def _compare_cas_nsm_prof(self, want, have):
        want_dict = {e["name"]: e for e in want}
        have_dict = {e["name"]: e for e in have}

        if self.state == "deleted":
            for name in (want_dict or have_dict):
                if name in have_dict:
                    self.addcmd(have_dict[name], "cas_nsm_prof.id", negate=True)
            return
        if self.state in ("replaced", "overridden"):
            for name, entry in have_dict.items():
                if name not in want_dict:
                    self.addcmd(entry, "cas_nsm_prof.id", negate=True)

        for name, want_entry in want_dict.items():
            have_entry = have_dict.get(name, {})
            cmd = self._build_named_cmd(
                "cas-nsm-prof", name, want_entry, have_entry,
                CAS_NSM_PROF_FIELDS,
            )
            if cmd:
                self.commands.append(cmd)

    @staticmethod
    def _build_named_cmd(cli_section, name, want_entry, have_entry, field_defs):
        parts = ["configure", "voice", "sip", cli_section]
        if name:
            parts.append(name)
        has_diff = False

        for py_name, cli_name, ftype in field_defs:
            if py_name in want_entry:
                wval = want_entry[py_name]
                hval = have_entry.get(py_name)
                if wval != hval:
                    has_diff = True
                    if ftype == "bool":
                        if wval is True:
                            parts.append(cli_name)
                        elif wval is False:
                            parts.extend(["no", cli_name])
                    elif ftype == "str":
                        if wval is not None:
                            value = str(wval)
                            if not value or any(char.isspace() for char in value) or value.startswith("#"):
                                value = '"' + value.replace('"', '\\"') + '"'
                            parts.extend([cli_name, value])
                    elif ftype == "int":
                        if wval is not None:
                            parts.extend([cli_name, str(wval)])

        if has_diff:
            return " ".join(parts)
        return None
