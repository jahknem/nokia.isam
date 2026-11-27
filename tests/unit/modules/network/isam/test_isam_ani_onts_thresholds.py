"""isam_ani_onts: thresholds of an existing tca-thresh entry are compared."""
from .module_runner import run_module

ONT = "1/1/6/1/1"
# Created with every ONT (lab DS-LIN-TEST-01 2026-11-27): the whole read shows the
# bare entry; thresholds appear once set.
BARE = "configure ani ont tca-thresh %s\n" % ONT
SET = "configure ani ont tca-thresh %s lower-optical-th -28\n" % ONT




def test_merged_sets_a_threshold_on_an_existing_entry(monkeypatch):
    result = run_module(monkeypatch, "isam_ani_onts",
                        {"state": "merged", "config": [{"ont_idx": ONT, "lower_optical_th": "-28"}]}, BARE)
    assert result["commands"] == ["configure ani ont tca-thresh %s lower-optical-th -28" % ONT]


def test_merged_with_the_set_value_is_idempotent(monkeypatch):
    result = run_module(monkeypatch, "isam_ani_onts",
                        {"state": "merged", "config": [{"ont_idx": ONT, "lower_optical_th": "-28.0"}]}, SET)
    assert result["commands"] == []


def test_replaced_resets_an_unrequested_threshold(monkeypatch):
    result = run_module(monkeypatch, "isam_ani_onts",
                        {"state": "replaced", "config": [{"ont_idx": ONT, "upper_optical_th": "-8"}]}, SET)
    assert result["commands"] == ["configure ani ont tca-thresh %s no lower-optical-th upper-optical-th -8" % ONT]


def test_merged_creates_a_missing_entry(monkeypatch):
    result = run_module(monkeypatch, "isam_ani_onts", {"state": "merged", "config": [{"ont_idx": ONT}]}, "")
    assert result["commands"] == ["configure ani ont tca-thresh %s" % ONT]


def test_deleted_resets_the_entry_instead_of_removing_it(monkeypatch):
    # Lab: "no tca-thresh" leaves the entry (it lives as long as its ONT).
    result = run_module(monkeypatch, "isam_ani_onts", {"state": "deleted", "config": [{"ont_idx": ONT}]}, SET)
    assert result["commands"] == ["configure ani ont tca-thresh %s no lower-optical-th" % ONT]


def test_deleted_of_an_entry_at_its_defaults_sends_nothing(monkeypatch):
    result = run_module(monkeypatch, "isam_ani_onts", {"state": "deleted", "config": [{"ont_idx": ONT}]}, BARE)
    assert result["commands"] == []


def test_overridden_resets_unrequested_entries(monkeypatch):
    other = "configure ani ont tca-thresh 1/1/6/1/2 upper-optical-th -8\n"
    result = run_module(monkeypatch, "isam_ani_onts", {"state": "overridden", "config": [{"ont_idx": ONT}]}, BARE + other)
    assert result["commands"] == ["configure ani ont tca-thresh 1/1/6/1/2 no upper-optical-th"]
