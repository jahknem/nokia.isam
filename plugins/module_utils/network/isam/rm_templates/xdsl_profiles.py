# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""Parser/renderer for ``configure xdsl {service,spectrum,dpbo,vect,vce}-profile``.

Every profile type is described by a node schema::

    {"attrs": [(option, keyword, kind), ...],      # kind: flag | int | str
     "nodes": [(option, keyword, schema), ...],    # sub-node -> nested dict
     "lists": [(option, keyword, schema), ...]}    # sub-node with an index -> list of dicts ("index")

The device prints every attribute flat (``configure xdsl spectrum-profile 1 vdsl2
pbo 2 equal-fext 237 param-a 4450``); ``info ... detail`` also prints the defaults as
``no <keyword>``, which are not reported. Unknown keywords never fail the read: they
are kept in the profile's ``commands`` (relative to the profile, like before).
"""

PROFILE_TYPES = {
    "service_profiles": "service-profile",
    "spectrum_profiles": "spectrum-profile",
    "dpbo_profiles": "dpbo-profile",
    "vect_profiles": "vect-profile",
    "vce_profiles": "vce-profile",
}

FLAG, INT, STR = "flag", "int", "str"


def _a(keyword, kind=INT, option=None):
    return (option or keyword.replace("-", "_").replace(".", "_"), keyword, kind)


def _node(attrs=(), nodes=(), lists=()):
    return {"attrs": list(attrs), "nodes": list(nodes), "lists": list(lists)}


# Breakpoint list entry (frequency / psd pair), e.g. ``epsd-pt-down 2 frequency 4 psd 950``.
PSD_POINT = _node([_a("frequency"), _a("psd")])

COMMON_HEAD = [_a("name", STR), _a("version")]

SERVICE = _node(COMMON_HEAD + [
    _a("ra-mode-down", STR), _a("ra-mode-up", STR),
    _a("min-bitrate-down"), _a("min-bitrate-up"),
    _a("sos-minbitrate-dn"), _a("sos-minbitrate-up"),
    _a("plan-bitrate-down"), _a("plan-bitrate-up"),
    _a("max-bitrate-down"), _a("max-bitrate-up"),
    _a("max-delay-down"), _a("max-delay-up"),
    _a("max-delay-var-dn"), _a("max-delay-var-up"),
    _a("memory-down"),
    _a("imp-noise-prot-dn"), _a("imp-noise-prot-up"),
    _a("inp8-dn"), _a("inp8-up"),
    _a("inp-wo-erasure-dn"), _a("inp-wo-erasure-up"),
    _a("min-l2-br-down"),
])

ADSL_COMMON = [
    _a("propr-feat-value", STR),
    _a("max-agpowlev-down"), _a("max-agpowlev-up"),
    _a("max-psd-down"), _a("max-psd-up"),
]

ADSL_ADSL2 = _node(ADSL_COMMON + [_a("pbo-mode-up", STR), _a("max-recv-power-up"), _a("psd-mask-up", STR)])
RE_ADSL = _node(ADSL_COMMON + [_a("pbo-mode-up", STR), _a("max-recv-power-up")])
ADSL2_PLUS = _node(
    ADSL_COMMON + [_a("psd-shape-down", STR), _a("pbo-mode-up", STR), _a("max-recv-power-up"), _a("psd-mask-up", STR)],
    lists=[_a("cust-psd-pt-down", PSD_POINT)],
)

VDSL = _node(
    [
        _a("propr-feat-value", STR), _a("vdsl-band-plan", STR), _a("optional-band", STR), _a("optional-endfreq"),
        _a("adsl-band", STR), _a("max-agpowlev-down"), _a("max-agpowlev-up"),
        _a("psd-shape-down", STR), _a("psd-shape-up", STR), _a("pbo-mode", STR), _a("rx-psd-shape-up", STR),
        _a("ghstones-pwr-mode", STR), _a("max-band", STR), _a("max-freq"),
        _a("m-psd-level-down"), _a("m-psd-level-up"),
        _a("psd-pbo-par-a-up", STR), _a("psd-pbo-par-b-up", STR),
        _a("cust-psd-sc-down", STR), _a("cust-psd-ty-down", STR),
        _a("cust-rx-psd-sc-up", STR), _a("cust-rx-psd-ty-up", STR),
        _a("opt-startfreq"),
    ],
    nodes=[_a("ghstone-set-pwr-ctrl", _node([_a("a43", STR), _a("b43", STR), _a("a43c", STR), _a("v43", STR)]))],
    lists=[
        _a("cust-psd-pt-down", PSD_POINT),
        _a("cust-rx-psd-pt-up", PSD_POINT),
        _a("pbo", _node([_a("param-a"), _a("param-b")])),
    ],
)

VDSL2 = _node(
    [
        _a("propr-feat-value", STR), _a("max-agpowlev-down"), _a("max-agpowlev-up"),
        _a("psd-shape-down", STR), _a("cs-psd-shape-dn", STR), _a("cs-psd-shape-up", STR),
        _a("psd-shape-up", STR), _a("rx-psd-shape-up", STR), _a("psd-pbo-e-len-up", STR),
        _a("m-psd-level-down"), _a("m-psd-level-up"),
        _a("psd-pbo-par-a-up", STR), _a("psd-pbo-par-b-up", STR),
        _a("v-noise-snr-down", STR), _a("v-noise-snr-up", STR),
        _a("v-noise-psd-down", STR), _a("v-noise-psd-up", STR),
        _a("cust-psd-sc-down", STR), _a("cust-psd-ty-down", STR),
        _a("cust-psd-sc-up", STR), _a("cust-psd-ty-up", STR),
        _a("cust-rx-psd-sc-up", STR), _a("cust-rx-psd-ty-up", STR),
        _a("upbo-aele-mode", STR), _a("upboaele-min-thrs"),
        _a("short-loop-lr", STR), _a("medium-loop-lr", STR), _a("long-loop-lr", STR),
    ],
    lists=[
        _a("cust-psd-pt-down", PSD_POINT),
        _a("cust-psd-pt-up", PSD_POINT),
        _a("cust-rx-psd-pt-up", PSD_POINT),
        _a("v-noise-psd-pt-down", PSD_POINT),
        _a("v-noise-psd-pt-up", PSD_POINT),
        _a("pbo", _node([_a("equal-fext"), _a("param-a"), _a("param-b")])),
    ],
)

SPECTRUM_MODES = [
    "dis-ansi-t1413", "dis-etsi-dts", "dis-g992-1-a", "dis-g992-1-b", "dis-g992-2-a", "dis-g992-3-a",
    "dis-g992-3-b", "g992-3-aj", "g992-3-l1", "g992-3-l2", "g992-3-am", "g992-5-a", "g992-5-b",
    "ansi-t1.424", "dis-etsi-ts", "itu-g993-1", "ieee-802.3ah", "g992-5-aj", "g992-5-am",
    "g993-2-8a", "g993-2-8b", "g993-2-8c", "g993-2-8d", "g993-2-12a", "g993-2-12b", "g993-2-17a",
    "g993-2-30a", "g993-2-35b",
]

SPECTRUM = _node(
    COMMON_HEAD + [_a(mode, FLAG) for mode in SPECTRUM_MODES] + [
        _a("min-noise-down"), _a("min-noise-up"), _a("trgt-noise-down"), _a("trgt-noise-up"),
        _a("max-noise-down"), _a("max-noise-up"),
        _a("carrier-mask-down", STR), _a("carrier-mask-up", STR),
        _a("rf-band-list", STR), _a("power_mgnt_mode", STR),
        _a("l0-time"), _a("l2-time"), _a("l2-agpow-red-tx"),
        _a("modification", STR),
        _a("rau-noise-down"), _a("rau-noise-up"), _a("rau-time-down"), _a("rau-time-up"),
        _a("rad-noise-down"), _a("rad-noise-up"), _a("rad-time-down"), _a("rad-time-up"),
        _a("l2-agpw-to-red-tx"),
    ],
    nodes=[
        _a("adsl-adsl2", ADSL_ADSL2),
        _a("re-adsl", RE_ADSL),
        _a("adsl2-plus", ADSL2_PLUS),
        _a("vdsl", VDSL),
        _a("vdsl2", VDSL2),
    ],
    lists=[_a("artificial-noise-down", PSD_POINT)],
)

DPBO = _node(
    COMMON_HEAD + [
        _a("es-elect-length"), _a("es-cable-model-a"), _a("es-cable-model-b"), _a("es-cable-model-c"),
        _a("min-usable-signal"), _a("min-frequency"), _a("max-frequency"), _a("rs-elect-length"),
        _a("muf-control", STR), _a("offset"), _a("modification", STR),
    ],
    lists=[_a("micpsd-pt-down", PSD_POINT), _a("epsd-pt-down", PSD_POINT)],
)

VECT = _node(COMMON_HEAD + [
    _a("fext-cancel-up", FLAG), _a("fext-cancel-dn", FLAG),
    _a("leg-can-dn-m1", FLAG), _a("leg-can-dn-m2", FLAG),
    _a("dis-gvect-cpe", FLAG), _a("gvecfriend-cpe", FLAG), _a("gvecfriend-dn-cpe", FLAG), _a("legacy-cpe", FLAG),
    _a("band-control-up", STR), _a("band-control-dn", STR),
    _a("vect-leav-thresh"), _a("vect-feat-bitmap", STR),
    _a("legacy-upbo", FLAG),
    _a("modification", STR),
])

VCE = _node(COMMON_HEAD + [
    _a("vce-gain-mode", STR), _a("vce-join-timeout", STR), _a("vce-min-par-join", STR),
    _a("vce-hist-pcoder", STR), _a("vce-band-plan", STR), _a("vce-max-vect-freq", STR),
    _a("modification", STR),
])

SCHEMAS = {
    "service_profiles": SERVICE,
    "spectrum_profiles": SPECTRUM,
    "dpbo_profiles": DPBO,
    "vect_profiles": VECT,
    "vce_profiles": VCE,
}

# ``active`` is rendered last, after every attribute and sub-node of the profile.
ACTIVE = ("active", "active", FLAG)


def _to_int(value):
    text = str(value)
    return int(text) if text.lstrip("-").isdigit() else value


class Xdsl_profilesTemplate(object):
    """Parser/renderer helpers for configure xdsl profile resources."""

    profile_types = PROFILE_TYPES
    schemas = SCHEMAS

    def __init__(self):
        # Statement paths the parser read without reporting them although they are not
        # known defaults: a valued keyword without a value, ``no <unknown keyword>``.
        # Never fails the read; for tests and diagnostics.
        self.skipped = []

    # ------------------------------------------------------------------ parse
    def parse(self, config):
        result = dict((key, []) for key in PROFILE_TYPES)
        index = {}

        def profile_for(profile_type, profile_id):
            key = (profile_type, profile_id)
            if key not in index:
                index[key] = {"id": profile_id}
                result[profile_type].append(index[key])
            return index[key]

        for profile_type, profile_id, tokens in self._statements(config):
            profile = profile_for(profile_type, profile_id)
            self.parse_tokens(profile_type, profile, tokens)
        return result

    def parse_tokens(self, profile_type, profile, tokens):
        """Apply one statement (tokens after ``<type> <id>``) to a profile dict."""
        self._parse_node(SCHEMAS[profile_type], profile, list(tokens), [], profile, root=True)

    def _statements(self, config):
        """(profile_type, id, tokens) per statement of flat or indented output."""
        header = None  # (profile_type, id, indent)
        stack = []  # [(indent, tokens)] containers below the profile header
        entries = []
        for raw in (config or "").splitlines():
            stripped = raw.strip()
            if not stripped or stripped.startswith("#") or stripped.startswith("echo"):
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if stripped == "configure xdsl":
                continue
            flat = stripped.startswith("configure xdsl ")
            if flat:
                stripped = stripped[len("configure xdsl "):]
            entries.append((indent, stripped, flat))

        for position, (indent, content, flat) in enumerate(entries):
            if content == "exit":
                continue
            tokens = content.split()
            profile_type = self._profile_key(tokens[0]) if len(tokens) > 1 else None
            if profile_type and (flat or header is None or indent <= header[2]):
                profile_id = _to_int(tokens[1])
                header = (profile_type, profile_id, indent)
                stack = []
                if len(tokens) > 2:
                    yield profile_type, profile_id, tokens[2:]
                continue
            if header is None or indent <= header[2]:
                continue
            stack = [item for item in stack if item[0] < indent]
            path = [token for _indent, item in stack for token in item]
            next_indent = entries[position + 1][0] if position + 1 < len(entries) else -1
            if next_indent > indent and not entries[position + 1][2]:
                stack.append((indent, tokens))
                continue
            yield header[0], header[1], path + tokens

    def _parse_node(self, schema, target, tokens, path, profile, root=False):
        attrs = dict((keyword, (option, kind)) for option, keyword, kind in schema["attrs"])
        if root:
            attrs["active"] = ("active", FLAG)
        nodes = dict((keyword, (option, sub)) for option, keyword, sub in schema["nodes"])
        lists = dict((keyword, (option, sub)) for option, keyword, sub in schema["lists"])
        known = set(attrs) | set(nodes) | set(lists) | set(["no"])

        position = 0
        while position < len(tokens):
            token = tokens[position]
            following = tokens[position + 1] if position + 1 < len(tokens) else None
            if token == "no":
                # ``no <keyword>``: the default (printed by ``detail``), not reported.
                if following is None or following not in known:
                    self.skipped.append(" ".join(path + [token] + ([following] if following else [])))
                position += 2
                continue
            if token in nodes:
                option, sub = nodes[token]
                child = target.get(option)
                if not isinstance(child, dict):
                    child = target[option] = {}
                self._parse_node(sub, child, tokens[position + 1:], path + [token], profile)
                self._prune(target, option)
                return
            if token in lists and following is not None:
                option, sub = lists[token]
                entries = target.get(option)
                if not isinstance(entries, list):
                    entries = target[option] = []
                entry_index = _to_int(following)
                entry = next((item for item in entries if item.get("index") == entry_index), None)
                if entry is None:
                    entry = {"index": entry_index}
                    entries.append(entry)
                self._parse_node(sub, entry, tokens[position + 2:], path + [token, following], profile)
                if len(entry) == 1:  # every attribute at its default
                    entries.remove(entry)
                self._prune(target, option)
                return
            if token in attrs:
                option, kind = attrs[token]
                if kind == FLAG:
                    target[option] = True
                    position += 1
                    continue
                if following is None or following in known:
                    self.skipped.append(" ".join(path + [token]))
                    position += 1  # no value (unexpected): skip, never fail
                    continue
                target[option] = _to_int(following) if kind == INT else following
                position += 2
                continue
            # Unknown keyword: keep it (with its value) as a profile-relative command.
            if following is not None and following not in known:
                profile.setdefault("commands", []).append(" ".join(path + [token, following]))
                position += 2
            else:
                profile.setdefault("commands", []).append(" ".join(path + [token]))
                position += 1

    @staticmethod
    def _prune(target, option):
        if target.get(option) in ({}, []):
            target.pop(option, None)

    # ----------------------------------------------------------------- render
    def render_profile(self, profile_type, profile, full=True):
        cli_type = PROFILE_TYPES[profile_type]
        prefix = "configure xdsl %s %s" % (cli_type, profile.get("id"))
        commands = []
        if full or profile.get("name"):
            commands.append("%s name %s" % (prefix, profile.get("name")))
        body = dict((k, v) for k, v in profile.items() if k not in ("id", "name", "commands", "active"))
        commands.extend("%s %s" % (prefix, line) for line in self.render_lines(SCHEMAS[profile_type], body))
        if "active" in profile and profile["active"] is not None:
            commands.append("%s %sactive" % (prefix, "" if profile["active"] else "no "))
        for command in profile.get("commands") or []:
            commands.append("%s %s" % (prefix, command))
        return commands

    def render_lines(self, schema, data, path=None):
        """Profile-relative lines for the attributes/sub-nodes present in data."""
        path = path or []
        lines = []
        for option, keyword, kind in schema["attrs"]:
            if option == "name" or data.get(option) is None:
                continue
            value = data[option]
            if kind == FLAG:
                lines.append(" ".join(path + [("" if value else "no ") + keyword]))
            else:
                lines.append(" ".join(path + [keyword, str(value)]))
        for option, keyword, sub in schema["nodes"]:
            if isinstance(data.get(option), dict):
                lines.extend(self.render_lines(sub, data[option], path + [keyword]))
        for option, keyword, sub in schema["lists"]:
            for entry in data.get(option) or []:
                if entry.get("index") is None:
                    continue
                lines.extend(self.render_lines(sub, entry, path + [keyword, str(entry["index"])]))
        return lines

    def removal_lines(self, schema, data, path=None):
        """Profile-relative ``no <keyword>`` lines resetting what data sets."""
        path = path or []
        lines = []
        for option, keyword, kind in schema["attrs"]:
            if option == "name" or data.get(option) is None or (kind == FLAG and not data[option]):
                continue
            lines.append(" ".join(path + ["no " + keyword]))
        for option, keyword, sub in schema["nodes"]:
            if isinstance(data.get(option), dict):
                lines.extend(self.removal_lines(sub, data[option], path + [keyword]))
        for option, keyword, sub in schema["lists"]:
            for entry in data.get(option) or []:
                if entry.get("index") is not None:
                    lines.extend(self.removal_lines(sub, entry, path + [keyword, str(entry["index"])]))
        return lines

    def diff_lines(self, schema, want, have, path=None):
        """Profile-relative lines setting what want changes against have (merged).

        Flags compare ``False`` equal to absent (``no <flag>`` is the default the
        facts do not report).
        """
        path = path or []
        lines = []
        have = have or {}
        for option, keyword, kind in schema["attrs"]:
            if option == "name":
                continue
            value = want.get(option)
            if value is None:
                continue
            current = have.get(option)
            if kind == FLAG:
                if bool(value) != bool(current):
                    lines.append(" ".join(path + [("" if value else "no ") + keyword]))
            elif value != current:
                lines.append(" ".join(path + [keyword, str(value)]))
        for option, keyword, sub in schema["nodes"]:
            if isinstance(want.get(option), dict):
                lines.extend(self.diff_lines(sub, want[option], have.get(option), path + [keyword]))
        for option, keyword, sub in schema["lists"]:
            haved = dict((entry.get("index"), entry) for entry in have.get(option) or [])
            for entry in want.get(option) or []:
                if entry.get("index") is None:
                    continue
                lines.extend(self.diff_lines(sub, entry, haved.get(entry["index"]), path + [keyword, str(entry["index"])]))
        return lines

    def delete_profile(self, profile_type, profile):
        return "configure xdsl no %s %s" % (PROFILE_TYPES[profile_type], profile.get("id"))

    # -------------------------------------------------------------- normalize
    def normalize(self, data):
        """Drop empty values, coerce ids/ints, and fold structured commands.

        A profile-relative command that the schema models (e.g. the
        ``vdsl pbo 1 param-a 4000`` facts used to return in ``commands``) is
        folded into its option, so want and have compare alike. Commands with
        ``no`` stay verbatim.
        """
        normalized = dict((key, []) for key in PROFILE_TYPES)
        for profile_type in PROFILE_TYPES:
            schema = SCHEMAS[profile_type]
            for item in (data or {}).get(profile_type) or []:
                profile = self._clean(schema, item, root=True)
                if "id" in profile:
                    profile["id"] = _to_int(profile["id"])
                commands = profile.pop("commands", None) or []
                for command in commands:
                    tokens = str(command).split()
                    if not tokens or "no" in tokens:
                        profile.setdefault("commands", []).append(command)
                        continue
                    self.parse_tokens(profile_type, profile, tokens)
                if profile.get("commands"):
                    profile["commands"] = list(dict.fromkeys(profile["commands"]))
                normalized[profile_type].append(profile)
        return normalized

    def _clean(self, schema, item, root=False):
        result = {}
        kinds = dict((option, kind) for option, _keyword, kind in schema["attrs"])
        nodes = dict((option, sub) for option, _keyword, sub in schema["nodes"])
        lists = dict((option, sub) for option, _keyword, sub in schema["lists"])
        for key, value in (item or {}).items():
            if value is None or value == [] or value == {}:
                continue
            if key in nodes and isinstance(value, dict):
                cleaned = self._clean(nodes[key], value)
                if cleaned:
                    result[key] = cleaned
            elif key in lists and isinstance(value, list):
                entries = []
                for entry in value:
                    cleaned = self._clean(lists[key], entry)
                    if cleaned.get("index") is not None:
                        cleaned["index"] = _to_int(cleaned["index"])
                        entries.append(cleaned)
                if entries:
                    result[key] = entries
            elif kinds.get(key) == INT or key == "index":
                result[key] = _to_int(value)
            else:
                result[key] = value
        return result

    def canonical(self, profile_type, profile):
        """Comparison form: False flags dropped (equal to absent), lists sorted by index."""
        return self._canonical(SCHEMAS[profile_type], profile or {}, root=True)

    def _canonical(self, schema, data, root=False):
        result = {}
        kinds = dict((option, kind) for option, _keyword, kind in schema["attrs"])
        if root:
            kinds["active"] = FLAG
        nodes = dict((option, sub) for option, _keyword, sub in schema["nodes"])
        lists = dict((option, sub) for option, _keyword, sub in schema["lists"])
        for key, value in data.items():
            if value is None or value == [] or value == {}:
                continue
            if kinds.get(key) == FLAG:
                if value:
                    result[key] = True
            elif key in nodes:
                cleaned = self._canonical(nodes[key], value)
                if cleaned:
                    result[key] = cleaned
            elif key in lists:
                entries = [self._canonical(lists[key], entry) for entry in value]
                entries = sorted((entry for entry in entries if len(entry) > 1), key=lambda entry: str(entry.get("index")))
                if entries:
                    result[key] = entries
            elif key == "commands":
                result[key] = sorted(set(value))
            else:
                result[key] = value
        return result

    def key_for(self, profile):
        return str(profile.get("id") if profile.get("id") is not None else profile.get("name"))

    def _profile_key(self, token):
        for key, cli_type in PROFILE_TYPES.items():
            if token == cli_type:
                return key
        return None
