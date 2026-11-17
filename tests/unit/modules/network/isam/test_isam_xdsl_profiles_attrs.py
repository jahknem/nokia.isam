"""isam_xdsl_profiles: every attribute of the detail capture (service/spectrum/dpbo/vect/vce).

Per attribute (walked from the template schemas): parse of the flat device line,
``no <keyword>`` (detail default) not reported, render/parse round trip, merged
idempotent and minimal, replaced reset (delete + full render), deleted.
"""
import os

import pytest

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config_tree import (
    gap_report,
    parse_config_tree,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_profiles import (
    PROFILE_TYPES,
    SCHEMAS,
    Xdsl_profilesTemplate,
)
from ansible_collections.nokia.isam.plugins.modules import isam_xdsl_profiles
from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

from .isam_module import TestIsamModule, set_module_args

FACTS = "ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.xdsl_profiles.xdsl_profiles.Xdsl_profilesFacts.get_config"
SAMPLE = {"int": 7, "str": "val-x", "flag": True}


def _attributes(schema, tokens=(), keys=()):
    """(tokens before the keyword, option path, keyword, kind) for every leaf attribute."""
    for option, keyword, kind in schema["attrs"]:
        if option in ("name",):
            continue
        yield list(tokens), list(keys) + [option], keyword, kind
    for option, keyword, sub in schema["nodes"]:
        for item in _attributes(sub, list(tokens) + [keyword], list(keys) + [option]):
            yield item
    for option, keyword, sub in schema["lists"]:
        for item in _attributes(sub, list(tokens) + [keyword, "3"], list(keys) + [(option, 3)]):
            yield item


def _leaf(keys, value):
    """Nested want/facts dict for one attribute."""
    if len(keys) == 1:
        return {keys[0]: value}
    head = keys[0]
    rest = _leaf(keys[1:], value)
    if isinstance(head, tuple):
        entry = {"index": head[1]}
        entry.update(rest)
        return {head[0]: [entry]}
    return {head: rest}


CASES = []
for _type, _schema in sorted(SCHEMAS.items()):
    for _tokens, _keys, _keyword, _kind in _attributes(_schema):
        CASES.append((_type, _tokens, _keys, _keyword, _kind))
IDS = ["%s:%s" % (case[0], " ".join(case[1] + [case[3]])) for case in CASES]


def _line(profile_type, tokens, keyword, value):
    words = ["configure xdsl", PROFILE_TYPES[profile_type], "9"] + tokens
    words += [keyword] if value is True else [keyword, str(value)]
    return " ".join(words)


@pytest.mark.parametrize("profile_type,tokens,keys,keyword,kind", CASES, ids=IDS)
def test_attribute_parse_default_and_round_trip(profile_type, tokens, keys, keyword, kind):
    template = Xdsl_profilesTemplate()
    value = SAMPLE[kind]
    line = _line(profile_type, tokens, keyword, value)
    expected = dict(_leaf(keys, value), id=9)

    parsed = template.normalize(template.parse(line))[profile_type]
    assert parsed == [expected]

    default = " ".join(["configure xdsl", PROFILE_TYPES[profile_type], "9"] + tokens + ["no", keyword])
    assert template.normalize(template.parse(default))[profile_type] == [{"id": 9}]

    rendered = template.render_profile(profile_type, expected, full=False)
    assert rendered == [line]
    assert template.normalize(template.parse("\n".join(rendered)))[profile_type] == [expected]


class TestXdslProfilesAttributes(TestIsamModule):
    module = isam_xdsl_profiles

    def setUp(self):
        super(TestXdslProfilesAttributes, self).setUp()
        self.mock_get_config = patch(FACTS)
        self.get_config = self.mock_get_config.start()
        self.mock_conn = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base.get_resource_connection"
        )
        self.mock_conn.start()
        self.mock_conn_facts = patch(
            "ansible_collections.ansible.netcommon.plugins.module_utils.network.common.facts.facts.get_resource_connection"
        )
        self.mock_conn_facts.start()

    def tearDown(self):
        super(TestXdslProfilesAttributes, self).tearDown()
        self.mock_get_config.stop()
        self.mock_conn.stop()
        self.mock_conn_facts.stop()

    def run_state(self, state, config, device, changed):
        self.get_config.return_value = device
        set_module_args({"state": state, "config": config}, True)
        return self.execute_module(changed=changed)

    def test_every_attribute_merged_replaced_deleted(self):
        for profile_type, tokens, keys, keyword, kind in CASES:
            with self.subTest(profile_type=profile_type, keyword=" ".join(tokens + [keyword])):
                value = SAMPLE[kind]
                line = _line(profile_type, tokens, keyword, value)
                prefix = "configure xdsl %s 9" % PROFILE_TYPES[profile_type]
                profile = dict(_leaf(keys, value), id=9, name="p")
                device = "%s name p\n%s" % (prefix, line)

                # merged: idempotent against the device, minimal when the attribute is missing
                self.run_state("merged", {profile_type: [profile]}, device, False)
                result = self.run_state("merged", {profile_type: [profile]}, prefix + " name p", True)
                self.assertEqual(result["commands"], [line])

                # replaced: a profile without the attribute resets it (delete + full render)
                result = self.run_state("replaced", {profile_type: [{"id": 9, "name": "p"}]}, device, True)
                self.assertEqual(result["commands"], ["configure xdsl no %s 9" % PROFILE_TYPES[profile_type], prefix + " name p"])
                self.run_state("replaced", {profile_type: [profile]}, device, False)

                # deleted removes the profile
                result = self.run_state("deleted", {profile_type: [{"id": 9}]}, device, True)
                self.assertEqual(result["commands"], ["configure xdsl no %s 9" % PROFILE_TYPES[profile_type]])

    def test_flag_false_equals_absent_and_negates_a_set_flag(self):
        prefix = "configure xdsl vect-profile 10"
        self.run_state("merged", {"vect_profiles": [{"id": 10, "name": "v", "fext_cancel_up": False}]},
                       prefix + " name v", False)
        result = self.run_state("merged", {"vect_profiles": [{"id": 10, "name": "v", "fext_cancel_up": False}]},
                                prefix + " name v fext-cancel-up", True)
        self.assertEqual(result["commands"], [prefix + " no fext-cancel-up"])

    def test_legacy_commands_for_modelled_sub_nodes_stay_idempotent(self):
        device = "configure xdsl spectrum-profile 2 name s\nconfigure xdsl spectrum-profile 2 vdsl pbo 1 param-a 4000 param-b 0"
        config = {"spectrum_profiles": [{"id": 2, "name": "s", "commands": ["vdsl pbo 1 param-a 4000 param-b 0"]}]}
        self.run_state("merged", config, device, False)
        self.run_state("replaced", config, device, False)

    def test_parsed_detail_lines(self):
        set_module_args({"state": "parsed", "running_config": "\n".join(DETAIL)}, True)
        result = self.execute_module(changed=False)
        self.assertEqual(result["parsed"], PARSED_DETAIL)


# Real lines of `info configure detail flat` (lab ISAM), shortened lists.
DETAIL = [
    "configure xdsl service-profile 11 name YPLAY-30-Privat version 1 no ra-mode-down no ra-mode-up no min-bitrate-down"
    " no min-bitrate-up no sos-minbitrate-dn no sos-minbitrate-up no plan-bitrate-down no plan-bitrate-up max-bitrate-down"
    " 33000 max-bitrate-up 5500 max-delay-down 10 max-delay-up 10 no max-delay-var-dn no max-delay-var-up no memory-down"
    " no imp-noise-prot-dn no imp-noise-prot-up no inp8-dn no inp8-up no inp-wo-erasure-dn no inp-wo-erasure-up no min-l2-br-down",
    "configure xdsl service-profile 11 active",
    "configure xdsl spectrum-profile 6 name VDSL2-17a-SNR6dB-fback version 1 dis-ansi-t1413 dis-etsi-dts dis-g992-1-a"
    " dis-g992-1-b dis-g992-2-a dis-g992-3-a dis-g992-3-b no g992-3-aj no g992-3-l1 no g992-3-l2 no g992-3-am no g992-5-a"
    " no g992-5-b no ansi-t1.424 dis-etsi-ts no itu-g993-1 no ieee-802.3ah no g992-5-aj no g992-5-am no g993-2-8a"
    " no g993-2-8b no g993-2-8c no g993-2-8d no g993-2-12a no g993-2-12b g993-2-17a no g993-2-30a no g993-2-35b"
    " no min-noise-down no min-noise-up no trgt-noise-down no trgt-noise-up no max-noise-down no max-noise-up"
    " no carrier-mask-down no carrier-mask-up rf-band-list not-used no power_mgnt_mode no l0-time no l2-time"
    " no l2-agpow-red-tx no modification no rau-noise-down no rau-noise-up no rau-time-down no rau-time-up"
    " no rad-noise-down no rad-noise-up no rad-time-down no rad-time-up no l2-agpw-to-red-tx",
    "configure xdsl spectrum-profile 6 artificial-noise-down 1 no frequency no psd",
    "configure xdsl spectrum-profile 6 adsl-adsl2 no propr-feat-value no max-agpowlev-down no max-agpowlev-up no max-psd-down"
    " no max-psd-up no pbo-mode-up no max-recv-power-up no psd-mask-up",
    "configure xdsl spectrum-profile 6 adsl2-plus cust-psd-pt-down 1 no frequency no psd",
    "configure xdsl spectrum-profile 6 vdsl no propr-feat-value vdsl-band-plan annex-b-998ade optional-band up optional-endfreq"
    " 276 adsl-band allow-adsl no max-agpowlev-down no max-agpowlev-up no psd-shape-down no psd-shape-up no pbo-mode"
    " no rx-psd-shape-up no ghstones-pwr-mode no max-band max-freq 2208 no m-psd-level-down no m-psd-level-up"
    " no psd-pbo-par-a-up no psd-pbo-par-b-up no cust-psd-sc-down no cust-psd-ty-down no cust-rx-psd-sc-up"
    " no cust-rx-psd-ty-up opt-startfreq 138",
    "configure xdsl spectrum-profile 6 vdsl ghstone-set-pwr-ctrl no a43 no b43 no a43c no v43",
    "configure xdsl spectrum-profile 6 vdsl pbo 2 param-a 4730 param-b 1977",
    "configure xdsl spectrum-profile 6 vdsl2 no propr-feat-value max-agpowlev-down 145 max-agpowlev-up 145 psd-shape-down"
    " regionbm2-psd-down no cs-psd-shape-dn no cs-psd-shape-up psd-shape-up regionbm2-psd-up rx-psd-shape-up equal-fext"
    " no psd-pbo-e-len-up no m-psd-level-down no m-psd-level-up psd-pbo-par-a-up 0f:a0:11:62:11:c6:0f:a0:0f:a0"
    " psd-pbo-par-b-up 00:00:0b:72:06:7c:00:00:00:00 no v-noise-snr-down no v-noise-snr-up no v-noise-psd-down"
    " no v-noise-psd-up no cust-psd-sc-down no cust-psd-ty-down no cust-psd-sc-up no cust-psd-ty-up no cust-rx-psd-sc-up"
    " no cust-rx-psd-ty-up no upbo-aele-mode no upboaele-min-thrs no short-loop-lr no medium-loop-lr no long-loop-lr",
    "configure xdsl spectrum-profile 6 vdsl2 pbo 2 equal-fext 237 param-a 4450 param-b 2930",
    "configure xdsl spectrum-profile 6 vdsl2 v-noise-psd-pt-down 1 no frequency no psd",
    "configure xdsl spectrum-profile 6 active",
    "configure xdsl dpbo-profile 1 name DPBO-ESEL-0249 es-elect-length 249 es-cable-model-a 14 es-cable-model-b 234"
    " es-cable-model-c 8 min-usable-signal -1120 min-frequency 254 max-frequency 1850 rs-elect-length 665 no muf-control"
    " no offset no modification active",
    "configure xdsl dpbo-profile 1 micpsd-pt-down 1 no frequency no psd",
    "configure xdsl dpbo-profile 1 epsd-pt-down 1 no frequency psd 950",
    "configure xdsl dpbo-profile 1 epsd-pt-down 2 frequency 4 psd 950",
    "configure xdsl vect-profile 10 name vect-default version 1 no fext-cancel-up no fext-cancel-dn no leg-can-dn-m1"
    " no leg-can-dn-m2 no dis-gvect-cpe no gvecfriend-cpe no gvecfriend-dn-cpe no legacy-cpe band-control-up 0:0"
    " band-control-dn 59:512 no vect-leav-thresh no vect-feat-bitmap no legacy-upbo no modification active",
    "configure xdsl vce-profile 10 name vce-default version 1 no vce-gain-mode vce-join-timeout auto no vce-min-par-join"
    " no vce-hist-pcoder no vce-band-plan no vce-max-vect-freq no modification active",
]

PARSED_DETAIL = {
    "service_profiles": [{
        "id": 11, "name": "YPLAY-30-Privat", "version": 1, "max_bitrate_down": 33000, "max_bitrate_up": 5500,
        "max_delay_down": 10, "max_delay_up": 10, "active": True,
    }],
    "spectrum_profiles": [{
        "id": 6, "name": "VDSL2-17a-SNR6dB-fback", "version": 1, "dis_ansi_t1413": True, "dis_etsi_dts": True,
        "dis_g992_1_a": True, "dis_g992_1_b": True, "dis_g992_2_a": True, "dis_g992_3_a": True, "dis_g992_3_b": True,
        "dis_etsi_ts": True, "g993_2_17a": True, "rf_band_list": "not-used", "active": True,
        "vdsl": {
            "vdsl_band_plan": "annex-b-998ade", "optional_band": "up", "optional_endfreq": 276, "adsl_band": "allow-adsl",
            "max_freq": 2208, "opt_startfreq": 138, "pbo": [{"index": 2, "param_a": 4730, "param_b": 1977}],
        },
        "vdsl2": {
            "max_agpowlev_down": 145, "max_agpowlev_up": 145, "psd_shape_down": "regionbm2-psd-down",
            "psd_shape_up": "regionbm2-psd-up", "rx_psd_shape_up": "equal-fext",
            "psd_pbo_par_a_up": "0f:a0:11:62:11:c6:0f:a0:0f:a0", "psd_pbo_par_b_up": "00:00:0b:72:06:7c:00:00:00:00",
            "pbo": [{"index": 2, "equal_fext": 237, "param_a": 4450, "param_b": 2930}],
        },
    }],
    "dpbo_profiles": [{
        "id": 1, "name": "DPBO-ESEL-0249", "es_elect_length": 249, "es_cable_model_a": 14, "es_cable_model_b": 234,
        "es_cable_model_c": 8, "min_usable_signal": -1120, "min_frequency": 254, "max_frequency": 1850,
        "rs_elect_length": 665, "active": True,
        "epsd_pt_down": [{"index": 1, "psd": 950}, {"index": 2, "frequency": 4, "psd": 950}],
    }],
    "vect_profiles": [{
        "id": 10, "name": "vect-default", "version": 1, "band_control_up": "0:0", "band_control_dn": "59:512", "active": True,
    }],
    "vce_profiles": [{"id": 10, "name": "vce-default", "version": 1, "vce_join_timeout": "auto", "active": True}],
}


def test_unknown_keywords_never_fail_and_stay_commands():
    template = Xdsl_profilesTemplate()
    parsed = template.normalize(template.parse(
        "configure xdsl vect-profile 10 name v future-knob 4 no future-off future-flag\n"
        "configure xdsl spectrum-profile 2 vdsl2 future-node 3 extra 1"
    ))
    assert parsed["vect_profiles"] == [{"id": 10, "name": "v", "commands": ["future-knob 4", "future-flag"]}]
    assert parsed["spectrum_profiles"] == [{"id": 2, "commands": ["vdsl2 future-node 3", "vdsl2 extra 1"]}]


# ---------------------------------------------------------------- lab capture
CAPTURE = os.path.join(
    os.environ.get("ISAM_ROOT_CAPTURES") or os.path.join(
        os.path.dirname(os.path.realpath(__file__)), *([os.pardir] * 6 + ["pon-migration-planner", ".local"])),
    "root-detail-flat.txt",
)
def _read(name):
    path = os.path.join(os.path.dirname(CAPTURE), name)
    if not os.path.exists(path):
        pytest.skip("lab capture not available")
    with open(path, errors="replace") as handle:
        return handle.read()


def _cross_check(tree_node, schema, facts, checked, root=False):
    """Compare the facts with the tree's attribute values where the tree reads them soundly.

    The tree has no grammar for these profiles: it pairs a flag with the next keyword
    and reads ``pbo <index> param-a <v>`` as attributes named by the values, so only
    valued attributes whose value is not itself a keyword of the node are compared.
    """
    attrs = dict((keyword, (option, kind)) for option, keyword, kind in schema["attrs"])
    nodes = dict((keyword, (option, sub)) for option, keyword, sub in schema["nodes"])
    lists = dict((keyword, (option, sub)) for option, keyword, sub in schema["lists"])
    keywords = set(attrs) | set(nodes) | set(lists) | set(["active"])
    for keyword, value in (tree_node.get("__config__") or {}).get("attrs", {}).items():
        if keyword not in attrs or attrs[keyword][1] == "flag":
            continue
        option = attrs[keyword][0]
        if value is False:
            assert option not in facts, (keyword, "default reported")
        elif isinstance(value, str) and value not in keywords:
            expected = int(value) if value.lstrip("-").isdigit() else value
            assert facts.get(option) == expected, keyword
        checked.append(keyword)
    for key, child in tree_node.items():
        if key in nodes:
            _cross_check(child, nodes[key][1], facts.get(nodes[key][0]) or {}, checked)
        elif key in lists:
            option, sub = lists[key]
            entries = dict((str(entry["index"]), entry) for entry in facts.get(option) or [])
            for index, entry_node in child.items():
                if index.isdigit():
                    _cross_check(entry_node, sub, entries.get(index) or {}, checked)


@pytest.mark.skipif(not os.path.exists(CAPTURE), reason="lab capture not available")
def test_detail_capture_gap_report_tree_and_parser_agree():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import select_resource_config

    text = _read("root-detail-flat.txt")
    tree = parse_config_tree(text)
    assert gap_report(tree)["families"]["xdsl_profiles"]["unmodelled"] == {}

    template = Xdsl_profilesTemplate()
    facts = template.normalize(template.parse(select_resource_config(text, "xdsl_profiles")))
    # Every keyword the device prints (set or ``no <keyword>``) is known: nothing skipped, nothing unknown.
    assert template.skipped == []
    assert not any(profile.get("commands") for profiles in facts.values() for profile in profiles)
    assert sum(len(profiles) for profiles in facts.values()) == 12

    checked = []
    for key, cli_type in PROFILE_TYPES.items():
        for profile in facts[key]:
            _cross_check(tree["xdsl"][cli_type][str(profile["id"])], SCHEMAS[key], profile, checked, root=True)
    assert len(checked) > 500


@pytest.mark.skipif(not os.path.exists(CAPTURE), reason="lab capture not available")
def test_detail_and_configured_capture_parse_alike():
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import select_resource_config

    template = Xdsl_profilesTemplate()
    parsed = [template.normalize(template.parse(select_resource_config(_read(name), "xdsl_profiles")))
              for name in ("root-detail-flat.txt", "root-flat.txt")]
    assert parsed[0] == parsed[1]
    assert not any(profile.get("commands") for profiles in parsed[0].values() for profile in profiles)
    lines = [line for key, profiles in parsed[0].items() for profile in profiles for line in template.render_profile(key, profile)]
    assert template.normalize(template.parse("\n".join(lines))) == parsed[0]
