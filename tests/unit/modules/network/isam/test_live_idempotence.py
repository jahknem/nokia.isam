"""Idempotence against the targeted 'flat detail' comparison read (live finding, 2026-11-18).

replaced/merged read the named instances with 'flat detail', which prints every default
('no polling-period', 'no admin-up'); config taken from a plain read omits them. In
0.3.13 replaced therefore "reset" all defaults -- for PON interfaces wrapped in
admin-state down/up, taking every ONT of the PON offline -- and ethernet_line /
xdsl_bonding overridden were never idempotent.
"""
from .test_deleted_regressions import run

PON_DETAIL = "\n".join([
    "configure pon interface 1/1/2/1 no label no ber-calc-period no polling-period no sig-degrade-th"
    " no sig-fail-th fec-dn enable no raman-reduct no closest-ont no diff-reach no pon-tag no pon-id"
    " no mcast-encrypt no auth-method no ponid-interval no ponid-odn no ponid-identifier no max-ranging-onts"
    " no pon-speed no burst-overhead no onu-prov-mode",
    "configure pon interface 1/1/2/1 tc-layer no pm-collect",
    "configure pon interface 1/1/2/1 admin-state up",
])
PON_WANT = [{"name": "1/1/2/1", "fec_dn": "enable", "admin_state": "up"}]


def test_pon_replaced_with_plain_read_config_sends_nothing(monkeypatch):
    for state in ("replaced", "merged"):
        result = run(monkeypatch, "isam_pon_interfaces", {"state": state, "config": PON_WANT}, PON_DETAIL)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == [], (state, result["commands"])


def test_pon_restricted_change_still_bounces_admin_state(monkeypatch):
    want = [dict(PON_WANT[0], diff_reach=40)]
    result = run(monkeypatch, "isam_pon_interfaces", {"state": "replaced", "config": want}, PON_DETAIL)
    assert result["commands"][0] == "configure pon interface 1/1/2/1 admin-state down"
    assert result["commands"][-1] == "configure pon interface 1/1/2/1 admin-state up"
    assert any("diff-reach 40" in c for c in result["commands"])


def test_pon_merged_explicit_default_is_sent_when_the_device_differs(monkeypatch):
    detail = PON_DETAIL.replace("no polling-period", "polling-period 50")
    want = [dict(PON_WANT[0], polling_period=100)]
    result = run(monkeypatch, "isam_pon_interfaces", {"state": "merged", "config": want}, detail)
    assert result["commands"] == ["configure pon interface 1/1/2/1 polling-period 100"]
    replaced = run(monkeypatch, "isam_pon_interfaces", {"state": "replaced", "config": PON_WANT}, detail)
    assert replaced["commands"] == ["configure pon interface 1/1/2/1 no polling-period"]


IF_DETAIL = "\n".join([
    'configure interface port bonding:1/1/3/1 no admin-up no link-updown-trap user "" severity no-value no port-type',
    "configure interface port uni:1/1/2/1/1/1/1 admin-up no link-updown-trap user YTest no severity no port-type",
])


def test_interfaces_replaced_does_not_resend_default_flags(monkeypatch):
    want = [{"name": "bonding:1/1/3/1", "severity": "no-value"},
            {"name": "uni:1/1/2/1/1/1/1", "admin_up": True, "user": "YTest"}]
    for state in ("replaced", "merged"):
        result = run(monkeypatch, "isam_interfaces", {"state": state, "config": want}, IF_DETAIL)
        assert not result.get("failed"), result.get("msg")
        assert result["commands"] == [], (state, result["commands"])


def test_interfaces_merged_explicit_false_still_shuts_an_up_port(monkeypatch):
    want = [{"name": "uni:1/1/2/1/1/1/1", "admin_up": False}]
    result = run(monkeypatch, "isam_interfaces", {"state": "merged", "config": want}, IF_DETAIL)
    assert result["commands"] == ["configure interface port uni:1/1/2/1/1/1/1 no admin-up"]
