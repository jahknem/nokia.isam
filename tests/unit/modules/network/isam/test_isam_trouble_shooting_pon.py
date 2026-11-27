"""isam_trouble_shooting_pon: targeted reads of default-only and silent instances."""
from . import targeted_harness as harness
from .targeted_cases_m import CASES

THRESHOLD = "configure trouble-shooting pon statistics threshold interface 1/1/2/1"


def _answer(flat, detail):
    def answer(command, lines):
        if command.endswith(" detail"):
            return detail
        return flat
    return answer


def test_a_default_only_threshold_is_present_with_its_identity(monkeypatch):
    # Live (DS-LIN-TEST-01 2026-11-27, PON 1/1/5/1): 'flat' prints the header only,
    # 'flat detail' the entry with "no bw-th-up no bw-th-dn". The parser crashed on
    # the bare path the probe returns.
    case = CASES["trouble_shooting_pon:threshold.interfaces"]
    device = harness.Device([], answer=_answer("echo x\n#---\n", THRESHOLD + " no bw-th-up no bw-th-dn\n"))
    result = harness.gathered(monkeypatch, case, case["config"], device)
    assert not result.get("failed"), result
    assert result["gathered"] == {"threshold": {"interfaces": [{"name": "1/1/2/1"}]}}
    assert harness.outcome_by_selector(result)["1/1/2/1"]["existence"] == "present"


def test_statistics_off_is_confirmed_absent_and_on_is_present(monkeypatch):
    # Silent switch (targeted.ABSENCE_POLICY): off answers "instance does not exist",
    # on prints the header only, also with detail.
    case = CASES["trouble_shooting_pon:interfaces"]
    off = harness.gathered(monkeypatch, case, case["config"], harness.Device([]))
    assert harness.outcome_by_selector(off)["1/1/2/1"]["existence"] == "confirmed_absent"
    on = harness.gathered(monkeypatch, case, case["config"],
                          harness.Device([], answer=_answer("echo x\n#---\n", "echo x\n#---\n")))
    assert on["gathered"] == {"interfaces": [{"name": "1/1/2/1"}]}
    assert harness.outcome_by_selector(on)["1/1/2/1"]["existence"] == "present"
