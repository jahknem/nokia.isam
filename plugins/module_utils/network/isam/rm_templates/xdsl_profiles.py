# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type


PROFILE_TYPES = {
    "service_profiles": "service-profile",
    "spectrum_profiles": "spectrum-profile",
    "dpbo_profiles": "dpbo-profile",
    "vect_profiles": "vect-profile",
    "vce_profiles": "vce-profile",
}

CLI_TO_KEY = {
    "version": "version",
    "max-bitrate-down": "max_bitrate_down",
    "max-bitrate-up": "max_bitrate_up",
    "max-delay-down": "max_delay_down",
    "max-delay-up": "max_delay_up",
    "dis-ansi-t1413": "dis_ansi_t1413",
    "dis-etsi-dts": "dis_etsi_dts",
    "dis-g992-1-a": "dis_g992_1_a",
    "dis-g992-1-b": "dis_g992_1_b",
    "dis-g992-2-a": "dis_g992_2_a",
    "dis-g992-3-a": "dis_g992_3_a",
    "dis-g992-3-b": "dis_g992_3_b",
    "g992-5-b": "g992_5_b",
    "g992-5-aj": "g992_5_aj",
    "dis-etsi-ts": "dis_etsi_ts",
    "g993-2-17a": "g993_2_17a",
    "rf-band-list": "rf_band_list",
    "es-elect-length": "es_elect_length",
    "es-cable-model-a": "es_cable_model_a",
    "es-cable-model-b": "es_cable_model_b",
    "es-cable-model-c": "es_cable_model_c",
    "min-usable-signal": "min_usable_signal",
    "min-frequency": "min_frequency",
    "max-frequency": "max_frequency",
    "rs-elect-length": "rs_elect_length",
    "band-control-up": "band_control_up",
    "band-control-dn": "band_control_dn",
    "vce-join-timeout": "vce_join_timeout",
}

KEY_TO_CLI = dict((value, key) for key, value in CLI_TO_KEY.items())
BOOL_KEYS = set([
    "active",
    "dis_ansi_t1413",
    "dis_etsi_dts",
    "dis_g992_1_a",
    "dis_g992_1_b",
    "dis_g992_2_a",
    "dis_g992_3_a",
    "dis_g992_3_b",
    "g992_5_b",
    "g992_5_aj",
    "dis_etsi_ts",
    "g993_2_17a",
])
INT_KEYS = set([
    "id",
    "version",
    "max_bitrate_down",
    "max_bitrate_up",
    "max_delay_down",
    "max_delay_up",
    "es_elect_length",
    "es_cable_model_a",
    "es_cable_model_b",
    "es_cable_model_c",
    "min_usable_signal",
    "min_frequency",
    "max_frequency",
    "rs_elect_length",
])


class Xdsl_profilesTemplate(object):
    """Parser/renderer helpers for configure xdsl profile resources."""

    profile_types = PROFILE_TYPES

    def parse(self, config):
        result = dict((key, []) for key in PROFILE_TYPES)
        current = None
        stack = []

        entries = []
        for raw in (config or "").splitlines():
            if not raw.strip() or raw.lstrip().startswith("#") or raw.lstrip().startswith("echo"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            content = raw.strip()
            if content == "configure xdsl":
                continue
            if content.startswith("configure xdsl "):
                content = content[len("configure xdsl "):]
                indent = 0
            entries.append((indent, content))

        for index, (indent, content) in enumerate(entries):
            if content == "exit":
                continue
            level = int(indent / 2)
            next_indent = entries[index + 1][0] if index + 1 < len(entries) else 0
            is_container = next_indent > indent

            profile_key = self._profile_key(content)
            if level == 0 and profile_key:
                candidate = self._new_profile(profile_key, content)
                current = next(
                    (item for item in result[profile_key] if item.get("id") == candidate.get("id")),
                    None,
                )
                if current is None:
                    current = candidate
                    result[profile_key].append(current)
                else:
                    current.update(candidate)
                stack = []
                continue

            if current is None:
                continue

            if level <= 0:
                continue

            stack = stack[:level - 1]
            path = stack + [content]
            if is_container:
                stack = path
                continue

            if len(path) == 1:
                self._parse_profile_leaf(current, content)
            else:
                current.setdefault("commands", []).append(" ".join(path))

        return result

    def render_profile(self, profile_type, profile, full=True):
        cli_type = PROFILE_TYPES[profile_type]
        prefix = "configure xdsl %s %s" % (cli_type, profile.get("id"))
        commands = []
        if full or profile.get("name"):
            commands.append("%s name %s" % (prefix, profile.get("name")))

        for key in self._render_order(profile_type):
            if key not in profile or key in ("id", "name", "commands"):
                continue
            cli_key = KEY_TO_CLI.get(key, key.replace("_", "-"))
            value = profile[key]
            if key in BOOL_KEYS:
                commands.append("%s %s%s" % (prefix, "" if value else "no ", cli_key))
            elif value is not None:
                commands.append("%s %s %s" % (prefix, cli_key, value))

        for command in profile.get("commands") or []:
            commands.append("%s %s" % (prefix, command))
        return commands

    def delete_profile(self, profile_type, profile):
        return "configure xdsl no %s %s" % (PROFILE_TYPES[profile_type], profile.get("id"))

    def normalize(self, data):
        normalized = dict((key, []) for key in PROFILE_TYPES)
        for profile_type in PROFILE_TYPES:
            for item in data.get(profile_type) or []:
                profile = dict((k, v) for k, v in item.items() if v is not None and v != [] and v != {})
                if "id" in profile:
                    profile["id"] = int(profile["id"])
                normalized[profile_type].append(profile)
        return normalized

    def key_for(self, profile):
        return str(profile.get("id") if profile.get("id") is not None else profile.get("name"))

    def _profile_key(self, content):
        for key, cli_type in PROFILE_TYPES.items():
            if content.startswith(cli_type + " "):
                return key
        return None

    def _new_profile(self, profile_key, content):
        cli_type = PROFILE_TYPES[profile_key]
        rest = content[len(cli_type):].strip().split()
        profile = {"id": int(rest[0]) if rest and rest[0].isdigit() else rest[0]}
        if len(rest) >= 3 and rest[1] == "name":
            profile["name"] = rest[2]
            rest = rest[3:]
        else:
            rest = rest[1:]
        index = 0
        while index < len(rest):
            key = rest[index]
            mapped_key = CLI_TO_KEY.get(key, key)
            if mapped_key in BOOL_KEYS or key == "active":
                self._parse_profile_leaf(profile, key)
                index += 1
            elif index + 1 < len(rest):
                self._parse_profile_leaf(profile, "%s %s" % (key, rest[index + 1]))
                index += 2
            else:
                index += 1
        return profile

    def _parse_profile_leaf(self, profile, content):
        parts = content.split(None, 1)
        cli_key = parts[0]
        if cli_key == "active":
            profile["active"] = True
            return
        key = CLI_TO_KEY.get(cli_key)
        if not key:
            profile.setdefault("commands", []).append(content)
            return
        if key in BOOL_KEYS and len(parts) == 1:
            profile[key] = True
        elif len(parts) == 2:
            value = parts[1]
            profile[key] = int(value) if key in INT_KEYS and value.lstrip("-").isdigit() else value

    def _render_order(self, profile_type):
        orders = {
            "service_profiles": ["version", "max_bitrate_down", "max_bitrate_up", "max_delay_down", "max_delay_up", "active"],
            "spectrum_profiles": ["version", "dis_ansi_t1413", "dis_etsi_dts", "dis_g992_1_a", "dis_g992_1_b", "dis_g992_2_a", "dis_g992_3_a", "dis_g992_3_b", "g992_5_b", "g992_5_aj", "dis_etsi_ts", "g993_2_17a", "rf_band_list", "active"],
            "dpbo_profiles": ["es_elect_length", "es_cable_model_a", "es_cable_model_b", "es_cable_model_c", "min_usable_signal", "min_frequency", "max_frequency", "rs_elect_length", "active"],
            "vect_profiles": ["version", "band_control_up", "band_control_dn", "active"],
            "vce_profiles": ["version", "vce_join_timeout", "active"],
        }
        return orders[profile_type]
