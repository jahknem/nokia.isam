"""qos_profiles against `info configure detail flat` of a real ISAM.

Every parameter of the eleven profile types: parse (detail lines incl. `no X`
defaults), render round trip, merged idempotence, replaced/deleted reset forms,
snake_case aliases, and documentation.
"""
from textwrap import dedent

import pytest

from ansible_collections.nokia.isam.plugins.modules import isam_qos_profiles
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.qos_profiles.qos_profiles import (
    Qos_profilesArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_profiles import (
    Qos_profilesTemplate,
)

from .isam_module import set_module_args
from .test_isam_qos_profiles import TestIsamQosProfilesModule as _Base


# Detail-format lines as printed by the device (lab capture), one per profile type.
DETAIL_LINES = dedent(
    """
    configure qos profiles queue FD_BEQ red:24:48:80 no unit
    configure qos profiles scheduler-node GPONShaperDN10Mbps priority 2 weight 50 shaper-profile name:GPONqssShaperDN10Mbps no ext-shaper mcast-inc-shape no-mcast-shap
    configure qos profiles cac DataOnly res-voice-bandwidth 0 max-mcast-bandwidth 0 res-data-bandwidth 0 cac-type generic-pon-cac
    configure qos profiles cac FD_Default res-voice-bandwidth 0 max-mcast-bandwidth 60000 res-data-bandwidth 0 no cac-type
    configure qos profiles marker d1p FD_Marker_CL default-dot1p 3
    configure qos profiles policer qpp5Mbps committed-info-rate 5120 committed-burst-size 256000 no policer-type no excess-info-rate no excess-burst-size no coupling-flag no color-mode no green-action no yellow-action no red-action no policed-size-ctrl no peak-info-rate no peak-burst-size no cos-threshold
    configure qos profiles session FD_Voice logical-flow-type pvc up-policer name:FD_Pol_Voice down-policer name:FD_Pol_Voice up-marker name:FD_Marker_Voice no ing-outer-marker no ds-schedule-tag no up-policer-per-tc no up-dscptotc-prof no dn-dscptotc-prof no up-pbittotc-prof no dn-pbittotc-prof no up-default-tc no dn-default-tc
    configure qos profiles aggrqueuesconfig DefaultDnQueuesConfig q0-priority 6 q1-priority 6 q2-priority 7 q3-priority 8 no q4-priority no q5-priority no q6-priority no q7-priority q0-weight 36 q1-weight 64 q2-weight 0 q3-weight 0 q4-weight 0 q5-weight 0 q6-weight 0 q7-weight 0 no q0-shaper-prof no q1-shaper-prof no q2-shaper-prof no q3-shaper-prof no q4-shaper-prof no q5-shaper-prof no q6-shaper-prof no q7-shaper-prof q0-queue-prof name:NGLT_Default q1-queue-prof name:NGLT_Default q2-queue-prof name:NGLT_Default q3-queue-prof name:NGLT_Default no q4-queue-prof no q5-queue-prof no q6-queue-prof no q7-queue-prof no q0-bandwidth-prof no q1-bandwidth-prof no q2-bandwidth-prof no q3-bandwidth-prof no q4-bandwidth-prof no q5-bandwidth-prof no q6-bandwidth-prof no q7-bandwidth-prof no q0-bw-sharing no q1-bw-sharing no q2-bw-sharing no q3-bw-sharing no q4-bw-sharing no q5-bw-sharing no q6-bw-sharing no q7-bw-sharing
    configure qos profiles shaper GPONqssShaperDN10Mbps committed-info-rate 0 committed-burst-size 0 excess-info-rate 10240 type singletokenbucketgpon no autoshape
    configure qos profiles bandwidth GPONqpp5Mbps committed-info-rate 0 assured-info-rate 0 excessive-info-rate 5120 delay-tolerance 32 no assu-burst-size no exce-burst-size no dbru
    configure qos profiles ingress-qos Ingress_Default dot1-p0-tc 0 dot1-p1-tc 1 dot1-p2-tc 2 dot1-p3-tc 3 dot1-p4-tc 4 dot1-p5-tc 5 dot1-p6-tc 6 dot1-p7-tc 7 no use-dei no dot1-p0-color no dot1-p1-color no dot1-p2-color no dot1-p3-color no dot1-p4-color no dot1-p5-color no dot1-p6-color no dot1-p7-color no dot1-p0-pol-tc no dot1-p1-pol-tc no dot1-p2-pol-tc no dot1-p3-pol-tc no dot1-p4-pol-tc no dot1-p5-pol-tc no dot1-p6-pol-tc no dot1-p7-pol-tc
    configure qos profiles rate-limit defaultllid total-rate 80 total-burst 100 no arp-rate no arp-burst no dhcp-rate no dhcp-burst no igmp-rate no igmp-burst no pppoe-rate no pppoe-burst no nd-rate no nd-burst no icmpv6-rate no icmpv6-burst no mld-rate no mld-burst no dhcpv6-rate no dhcpv6-burst no cfm-rate no cfm-burst
    """
)

# Synthetic lines: every optional parameter set to a non-default value (help syntax).
FULL_LINES = dedent(
    """
    configure qos profiles queue QB tail-drop:64 unit byte
    configure qos profiles scheduler-node SN priority 3 weight 20 shaper-profile name:SH1 ext-shaper name:SH2 mcast-inc-shape mcast-shap-on
    configure qos profiles policer PT committed-info-rate 1000 committed-burst-size 2000 policer-type trtcm excess-info-rate 3000 excess-burst-size 4000 coupling-flag enable color-mode color-aware green-action pass yellow-action setouterdei red-action discard policed-size-ctrl ingress-mode peak-info-rate 5000 peak-burst-size 6000 cos-threshold name:COS
    configure qos profiles session SF logical-flow-type generic up-policer name:P1 down-policer name:P2 up-marker name:M1 ing-outer-marker name:M2 ds-schedule-tag cvlantag up-policer-per-tc name:PPT up-dscptotc-prof name:UD dn-dscptotc-prof name:DD up-pbittotc-prof name:UP dn-pbittotc-prof name:DP up-default-tc 1 dn-default-tc 2
    configure qos profiles aggrqueuesconfig AQ q7-priority 2 q7-weight 9 q7-shaper-prof name:S7 q7-queue-prof name:Q7 q7-bandwidth-prof name:B7 q7-bw-sharing uni-sharing
    configure qos profiles shaper SA committed-info-rate 10 committed-burst-size 64 excess-info-rate 20 type twotokenbuckettworate autoshape autoshape-on
    configure qos profiles bandwidth BA committed-info-rate 1 assured-info-rate 2 excessive-info-rate 3 delay-tolerance 4 assu-burst-size 5 exce-burst-size 6 dbru disable
    configure qos profiles ingress-qos IQ dot1-p3-tc 15 use-dei dot1-p3-color yellow dot1-p3-pol-tc 4
    configure qos profiles rate-limit RA total-rate 10 total-burst 11 arp-rate 1 arp-burst 2 dhcp-rate 3 dhcp-burst 4 igmp-rate 5 igmp-burst 6 pppoe-rate 7 pppoe-burst 8 nd-rate 9 nd-burst 10 icmpv6-rate 11 icmpv6-burst 12 mld-rate 13 mld-burst 14 dhcpv6-rate 15 dhcpv6-burst 16 cfm-rate 17 cfm-burst 18
    """
)


def _parse(text):
    return {(e["profile_type"], e["name"]): e for e in Qos_profilesTemplate(lines=text.splitlines()).parse().values()}


def _strip_false(entries):
    return {k: {f: v for f, v in e.items() if v is not False} for k, e in entries.items()}


def test_detail_lines_parse_every_parameter():
    p = _parse(DETAIL_LINES)
    assert not any("attributes" in e for e in p.values())
    assert p[("queue", "FD_BEQ")] == {"profile_type": "queue", "name": "FD_BEQ", "queue-type": "red:24:48:80"}
    assert p[("scheduler-node", "GPONShaperDN10Mbps")]["shaper-profile"] == "name:GPONqssShaperDN10Mbps"
    assert "ext-shaper" not in p[("scheduler-node", "GPONShaperDN10Mbps")]
    assert p[("cac", "DataOnly")]["cac-type"] == "generic-pon-cac"
    assert "cac-type" not in p[("cac", "FD_Default")]
    assert p[("marker-d1p", "FD_Marker_CL")]["default-dot1p"] == 3
    assert set(p[("policer", "qpp5Mbps")]) == {"profile_type", "name", "committed-info-rate", "committed-burst-size"}
    assert p[("session", "FD_Voice")]["up-marker"] == "name:FD_Marker_Voice"
    aq = p[("aggrqueuesconfig", "DefaultDnQueuesConfig")]
    assert aq["q3-priority"] == 8 and aq["q7-weight"] == 0 and aq["q0-queue-prof"] == "name:NGLT_Default"
    assert "q4-priority" not in aq and "q0-shaper-prof" not in aq and "q0-bw-sharing" not in aq
    assert p[("shaper", "GPONqssShaperDN10Mbps")]["shaper-type"] == "singletokenbucketgpon"
    assert p[("bandwidth", "GPONqpp5Mbps")]["delay-tolerance"] == 32
    iq = p[("ingress-qos", "Ingress_Default")]
    assert iq["dot1-p7-tc"] == 7 and iq["use-dei"] is False and "dot1-p0-color" not in iq
    assert p[("rate-limit", "defaultllid")] == {"profile_type": "rate-limit", "name": "defaultllid", "total-rate": 80, "total-burst": 100}


def test_full_lines_parse_every_optional_parameter():
    p = _parse(FULL_LINES)
    assert p[("queue", "QB")]["unit"] == "byte"
    assert p[("scheduler-node", "SN")]["ext-shaper"] == "name:SH2"
    pol = p[("policer", "PT")]
    assert pol["policer-type"] == "trtcm" and pol["yellow-action"] == "setouterdei" and pol["cos-threshold"] == "name:COS"
    assert pol["policed-size-ctrl"] == "ingress-mode" and pol["peak-burst-size"] == 6000
    ses = p[("session", "SF")]
    assert ses["ds-schedule-tag"] == "cvlantag" and ses["up-policer-per-tc"] == "name:PPT" and ses["dn-default-tc"] == 2
    aq = p[("aggrqueuesconfig", "AQ")]
    assert aq["q7-bandwidth-prof"] == "name:B7" and aq["q7-bw-sharing"] == "uni-sharing" and aq["q7-shaper-prof"] == "name:S7"
    assert p[("shaper", "SA")]["autoshape"] == "autoshape-on"
    assert p[("bandwidth", "BA")]["dbru"] == "disable" and p[("bandwidth", "BA")]["exce-burst-size"] == 6
    iq = p[("ingress-qos", "IQ")]
    assert iq["use-dei"] is True and iq["dot1-p3-color"] == "yellow" and iq["dot1-p3-pol-tc"] == 4 and iq["dot1-p3-tc"] == 15
    assert p[("rate-limit", "RA")]["cfm-burst"] == 18 and p[("rate-limit", "RA")]["icmpv6-rate"] == 11


def test_use_dei_block_format():
    p = _parse("configure qos\nprofiles\ningress-qos A\n  use-dei\nexit\ningress-qos B\n  no use-dei\nexit\n")
    assert p[("ingress-qos", "A")]["use-dei"] is True
    assert p[("ingress-qos", "B")]["use-dei"] is False


def test_gap_options_documented_and_aliased():
    import yaml

    doc = yaml.safe_load(isam_qos_profiles.DOCUMENTATION)["options"]["config"]["suboptions"]
    spec = Qos_profilesArgs.argument_spec["config"]["options"]
    assert set(doc) == set(spec)
    for name, option in spec.items():
        assert doc[name]["type"] == option["type"], name
        assert doc[name].get("aliases") == option.get("aliases"), name
        if "-" in name:
            assert option["aliases"] == [name.replace("-", "_")]


class TestQosProfilesGaps(_Base):
    def _run(self, state, config=None, running=None, changed=False):
        if running is not None:
            class Conn(object):
                def get(self, cmd):
                    return running

            self.get_resource_connection_facts.return_value = Conn()
        args = dict(state=state)
        if config is not None:
            args["config"] = config
        set_module_args(args, True)
        return self.execute_module(changed=changed)

    def test_round_trip_rendered_reparses(self):
        for text in (DETAIL_LINES, FULL_LINES):
            set_module_args(dict(state="parsed", running_config=text), True)
            parsed = self.execute_module(changed=False)["parsed"]
            rendered = self._run("rendered", config=parsed)["rendered"]
            assert not any(c.startswith("no ") for c in rendered)
            assert _strip_false(_parse("\n".join(rendered))) == _strip_false(_parse(text))

    def test_merged_is_idempotent_on_detail_and_full(self):
        for text in (DETAIL_LINES, FULL_LINES):
            set_module_args(dict(state="parsed", running_config=text), True)
            parsed = self.execute_module(changed=False)["parsed"]
            result = self._run("merged", config=parsed, running=text)
            assert result["commands"] == []

    def test_dependent_parameters_go_in_one_command(self):
        """The device rejected 'excess-info-rate' sent before 'type' (EIR needs a two-rate type)."""
        result = self._run(
            "merged",
            config=[{"profile_type": "shaper", "name": "NewTwoRate", "committed_info_rate": 1024,
                     "committed_burst_size": 256000, "shaper_type": "twotokenbuckettworate", "excess_info_rate": 2048}],
            running=DETAIL_LINES,
            changed=True,
        )
        assert len(result["commands"]) == 1
        command = result["commands"][0]
        assert command.startswith("configure qos profiles shaper NewTwoRate committed-info-rate 1024 committed-burst-size 256000")
        assert " type twotokenbuckettworate" in command and " excess-info-rate 2048" in command

    def test_changing_the_type_of_an_existing_shaper_fails_early(self):
        """The device refuses ('changing type is not allowed'); fail before sending."""
        from ansible_collections.nokia.isam.tests.unit.modules.utils import AnsibleFailJson

        running = "configure qos profiles shaper S1 committed-info-rate 1024 committed-burst-size 256000"
        with self.assertRaises((AnsibleFailJson, AssertionError)) as raised:
            self._run("merged", config=[{"profile_type": "shaper", "name": "S1", "shaper_type": "twotokenbuckettworate"}],
                      running=running, changed=True)
        assert "cannot be changed" in str(raised.exception)

    def test_merged_changes_and_aliases(self):
        result = self._run(
            "merged",
            config=[
                {"profile_type": "aggrqueuesconfig", "name": "DefaultDnQueuesConfig", "q4_priority": 3, "q0_bw_sharing": "ont-sharing"},
                {"profile_type": "ingress-qos", "name": "Ingress_Default", "use_dei": True, "dot1_p2_color": "red"},
                {"profile_type": "shaper", "name": "GPONqssShaperDN10Mbps", "excess_info_rate": 20480},
                {"profile_type": "policer", "name": "qpp5Mbps", "committed_info_rate": 6000},
            ],
            running=DETAIL_LINES,
            changed=True,
        )
        # one packed command per profile: mandatory parameters (as on the device) first
        assert sorted(result["commands"]) == [
            "configure qos profiles aggrqueuesconfig DefaultDnQueuesConfig q0-bw-sharing ont-sharing q4-priority 3",
            "configure qos profiles ingress-qos Ingress_Default use-dei dot1-p2-color red",
            "configure qos profiles policer qpp5Mbps committed-info-rate 6000 committed-burst-size 256000",
            "configure qos profiles shaper GPONqssShaperDN10Mbps committed-info-rate 0 committed-burst-size 0 "
            "excess-info-rate 20480",
        ]

    def test_replaced_resets_optional_keeps_mandatory(self):
        from ansible.module_utils import basic
        from ansible_collections.nokia.isam.tests.unit.compat.mock import patch

        with patch.object(basic.AnsibleModule, "warn") as warn:
            result = self._run(
                "replaced",
                config=[
                    {"profile_type": "session", "name": "SF", "logical-flow-type": "generic", "up-policer": "name:P1"},
                    {"profile_type": "policer", "name": "PT", "committed-info-rate": 1000},
                    {"profile_type": "ingress-qos", "name": "IQ", "dot1-p3-tc": 15},
                    {"profile_type": "aggrqueuesconfig", "name": "AQ", "q7-priority": 2},
                ],
                running=FULL_LINES,
                changed=True,
            )
        warnings = [call[0][0] for call in warn.call_args_list]
        commands = result["commands"]
        resets = {
            "session SF": ("down-policer", "up-marker", "ing-outer-marker", "ds-schedule-tag", "up-policer-per-tc",
                           "up-dscptotc-prof", "dn-dscptotc-prof", "up-pbittotc-prof", "dn-pbittotc-prof",
                           "up-default-tc", "dn-default-tc"),
            "policer PT": ("policer-type", "excess-info-rate", "excess-burst-size", "coupling-flag", "color-mode",
                           "green-action", "yellow-action", "red-action", "policed-size-ctrl", "peak-info-rate",
                           "peak-burst-size", "cos-threshold"),
            "ingress-qos IQ": ("use-dei", "dot1-p3-color", "dot1-p3-pol-tc"),
            "aggrqueuesconfig AQ": tuple("q7-" + f for f in ("weight", "shaper-prof", "queue-prof", "bandwidth-prof",
                                                            "bw-sharing")),
        }
        for profile, fields in resets.items():
            command = profile_command(commands, profile)
            for field in fields:
                assert " no %s " % field in command + " ", (profile, field)
        # committed-burst-size is mandatory: never "no committed-burst-size"; kept with a warning.
        assert not any("no committed-burst-size" in c or "no logical-flow-type" in c for c in commands)
        assert any("committed-burst-size" in w for w in warnings)

    def test_deleted_removes_profiles_only(self):
        result = self._run(
            "deleted",
            config=[{"profile_type": "policer", "name": "PT"}, {"profile_type": "rate-limit", "name": "RA"}],
            running=FULL_LINES,
            changed=True,
        )
        assert sorted(result["commands"]) == [
            "configure qos profiles no policer PT",
            "configure qos profiles no rate-limit RA",
        ]


def profile_command(commands, profile):
    """The one packed command of '<type> <name>' (commands are packed per profile)."""
    prefix = "configure qos profiles %s " % profile
    matching = [c for c in commands if c.startswith(prefix)]
    assert len(matching) == 1, (profile, len(matching))
    return matching[0]
