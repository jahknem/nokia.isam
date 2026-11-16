"""The direct QoS interface parser must give exactly the template parser's facts.

The template parse (one regex and Jinja pass per field and line) took minutes on a
full MSAN; the direct parser is used for facts, gathered, parsed and module state.
"""
import time
from pathlib import Path

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common import utils
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.qos_interfaces.qos_interfaces import (
    Qos_interfacesFacts,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.qos_interfaces import (
    Qos_interfacesTemplate,
)

FIXTURES = Path(__file__).resolve().parents[4] / "fixtures"

SYNTHETIC = "\n".join([
    "configure qos interface 1/1/5/1/3/1/1 scheduler-node name:A cac-profile name:B oper-weight 50 oper-rate 0 ds-num-queue 8",
    "configure qos interface 1/1/5/1/3/1/1 queue 0 priority 6 weight 34 oper-weight 34 queue-profile name:Q shaper-profile none",
    "configure qos interface 1/1/5/1/3/1/1 upstream-queue 4 weight 5 bandwidth-profile name:U bandwidth-sharing uni-sharing",
    "configure qos interface 1/1/5/1/3/1/1 ds-rem-queue 0 priority 6 weight 34",
    "configure qos interface 1/1/5/1/3/1/1 no scheduler-node no ds-queue-sharing queue-stats-on autoschedule",
    "configure qos interface 1/1/5/1/3/1/1 upstream-queue 0 no weight",
    "configure qos interface 1/1/5/1/3/1/1 queue 1 no priority",
    "configure qos interface 1/1/5/1/3/1/1 oper-weight abc unknown-field 7",
    "configure qos interface vlan:1/1/5/1/3/1/1:10 ds-num-queue not-applicable gem-sharing not-applicable",
    "configure qos interface ont:1/1/5/1/3 no mc-scheduler-node us-vlanport-queue",
    "configure qos interface 1/1/9/9/9/1/1",
    "info configure qos interface 1/1/5/1/3/1/1 flat",
])


def facts_of(parsed, facts, template):
    objs = list(parsed.values())
    for item in objs:
        for key in ("queue", "upstream_queue", "ds_rem_queue"):
            if isinstance(item.get(key), dict):
                item[key] = list(item[key].values())
    return utils.remove_empties(template.validate_config(facts.argument_spec, {"config": objs})).get("config", [])


def both(text, limit=None):
    facts = Qos_interfacesFacts(module=None)
    lines = facts._flatten_config(text)[:limit]
    template = Qos_interfacesTemplate(lines=lines)
    return facts_of(facts._parse_lines(lines), facts, template), facts_of(template.parse(), facts, template)


def test_direct_parser_matches_the_template_on_synthetic_edge_cases():
    fast, slow = both(SYNTHETIC)
    assert fast == slow
    assert fast[0]["queue_stats_on"] is True and fast[0]["ds_queue_sharing"] is False


def test_direct_parser_matches_the_template_on_every_qos_fixture():
    outputs = [path.read_text() for path in FIXTURES.glob("qos_interfaces/**/output.txt")]
    assert outputs
    for text in outputs:
        # The reference (template) parse is slow: compare on the first 1,500 lines.
        fast, slow = both(text, limit=1500)
        assert fast and fast == slow
        facts = Qos_interfacesFacts(module=None)
        assert len(facts._parse_lines(facts._flatten_config(text))) >= len(fast)


def test_direct_parser_scales_to_a_full_msan():
    facts = Qos_interfacesFacts(module=None)
    lines = []
    for ont in range(1, 2001):
        uni = "1/1/%d/%d/%d/1/1" % (5 + ont // 1024, 1 + (ont // 64) % 16, 1 + ont % 64)
        lines += [
            "configure qos interface %s scheduler-node name:A cac-profile name:B oper-weight 50 oper-rate 0" % uni,
            "configure qos interface %s queue 0 priority 6 weight 34 oper-weight 34 queue-profile name:Q shaper-profile none" % uni,
            "configure qos interface %s upstream-queue 0 bandwidth-profile name:U bandwidth-sharing uni-sharing" % uni,
        ]
    flat = facts._flatten_config("\n".join(lines))
    started = time.monotonic()
    parsed = facts._parse_lines(flat)
    assert len(flat) > 20000 and len(parsed) > 1000
    assert time.monotonic() - started < 2
