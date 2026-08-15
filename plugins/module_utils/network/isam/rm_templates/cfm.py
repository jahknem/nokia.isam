import shlex

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import NetworkTemplate
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import (
    canonical_key,
    parse_cli_fields,
)


class CfmTemplate(NetworkTemplate):
    """Parser for the flat CFM command form returned by ISAM."""
    BOOL_OPTIONS = {
        "ccm-aware",
        "dual-tag-aware",
        "cci-enable",
        "slm-resp-enable",
        "dm-resp-enable",
        "slm-init-enable",
        "ais-enable",
        "portshut-enable",
    }
    INT_OPTIONS = {
        "level",
        "ccm_priority",
        "fng_alarm_time",
        "fng_reset_time",
        "meg_level",
        "period",
        "priority",
    }

    def __init__(self, lines=None, module=None):
        super(CfmTemplate, self).__init__(lines=lines, tmplt=self, module=module)
        self.lines = lines

    def parse(self):
        result = {"domains": [], "slm": {}, "y1731pm": []}
        domains = {}
        for raw in self.lines or []:
            words = shlex.split(raw.strip())
            if len(words) < 3 or words[:2] != ["configure", "cfm"]:
                continue
            if words[2] == "slm":
                if len(words) >= 5 and words[3] == "inactivity-time":
                    result["slm"]["inactivity_time"] = int(words[4])
                continue
            if words[2] == "y1731pm":
                self._parse_pm(words[3:], result["y1731pm"])
                continue
            if words[2] != "domain" or len(words) < 5:
                continue
            domain = domains.setdefault(int(words[3]), {"domain_index": int(words[3]), "associations": []})
            if words[4] == "name":
                level = words.index("level", 5) if "level" in words[5:] else len(words)
                domain["name"] = " ".join(words[5:level])
                if level < len(words) - 1:
                    domain["level"] = int(words[level + 1])
                continue
            if words[4] != "association" or len(words) < 6:
                continue
            association = self._child(domain["associations"], "association_index", int(words[5]))
            if len(words) == 6:
                continue
            if words[6] == "remote-mep":
                association.setdefault("remote_meps", []).append(int(words[7]))
                continue
            if words[6] == "mep" and len(words) >= 8:
                mep = self._child(association.setdefault("meps", []), "mepid", int(words[7]))
                if len(words) > 8 and words[8] == "active-remote-mep":
                    mep.setdefault("active_remote_meps", []).append(int(words[9]))
                elif len(words) > 8 and words[8] == "y1731ais":
                    self._options(words[9:], mep.setdefault("y1731ais", {}), self.OPTIONS)
                else:
                    self._options(words[8:], mep, self.OPTIONS)
            else:
                self._options(words[6:], association, self.OPTIONS)
        result["domains"] = sorted(domains.values(), key=lambda x: x["domain_index"])
        return result

    OPTIONS = {"bridgeport": "bridgeport", "vlan": "vlan", "mhf-creation": "mhf_creation", "name": "name", "ccm-interval": "ccm_interval", "ccm-aware": "ccm_aware", "ccm-admin-state": "ccm_admin_state", "mhf-location": "mhf_location", "ltm-filtering": "ltm_filtering", "dual-tag-aware": "dual_tag_aware", "location": "location", "cci-enable": "cci_enable", "ccm-priority": "ccm_priority", "equipment": "equipment", "low-pri-defect": "low_pri_defect", "fng-alarm-time": "fng_alarm_time", "fng-reset-time": "fng_reset_time", "slm-resp-enable": "slm_resp_enable", "dm-resp-enable": "dm_resp_enable", "lm-resp": "lm_resp", "slm-init-enable": "slm_init_enable", "lm-init": "lm_init", "ais-enable": "ais_enable", "meg-level": "meg_level", "period": "period", "priority": "priority", "portshut-enable": "portshut_enable"}

    def _options(self, words, target, mapping):
        value_fields = {
            key: "int" if mapping[key] in self.INT_OPTIONS else "str"
            for key in mapping
            if key not in self.BOOL_OPTIONS
        }
        parsed = parse_cli_fields(
            words,
            bool_fields=self.BOOL_OPTIONS.intersection(mapping),
            value_fields=value_fields,
        )
        for key, field in mapping.items():
            parsed_key = canonical_key(key)
            if parsed_key in parsed:
                target[field] = parsed[parsed_key]

    @staticmethod
    def _child(items, key, value):
        for item in items:
            if item.get(key) == value:
                return item
        item = {key: value}
        items.append(item)
        return item

    def _parse_pm(self, words, items):
        if len(words) < 6 or words[0] != "domain":
            return
        item = {"domain_index": int(words[1]), "association": int(words[3]), "mep": int(words[5]), "session_id": int(words[7])}
        self._options(words[8:], item, {"type": "type", "target-mac": "target_mac", "priority": "priority", "admin-up": "admin_up", "interval": "interval", "size": "size", "measurement-intvl": "measurement_intvl"})
        items.append(item)
