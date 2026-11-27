"""isam_xdsl_boards: deleted resets only what it names; overridden only named sections (review of #15)."""
from .module_runner import run_module

DEVICE = (
    "configure xdsl board 1/1/1 card-type ndlt-f admin-state up vce-profile 10\n"
    "configure xdsl board 1/1/1 vect-fallback spectrum-profile 2 rtx-profile 3\n"
    "configure xdsl vp-board 1/1/9 admin-state up\n"
    "configure xdsl vp-board 1/1/9 vp-link 1 lt-expect 1/1/4\n"
    "configure xdsl vp-board 1/1/9 vp-link 2 lt-expect 1/1/3\n"
)


def commands(monkeypatch, state, config):
    result = run_module(monkeypatch, "isam_xdsl_boards", {"state": state, "config": config}, DEVICE)
    assert not result.get("failed"), result
    return result["commands"]


def test_deleted_named_vp_link_attribute_resets_only_it(monkeypatch):
    got = commands(monkeypatch, "deleted", {"vp_boards": [{"vp_board_id": "1/1/9", "vp_links": [
        {"link_id": 1, "lt_expect": "1/1/4"}]}]})
    assert got == ["configure xdsl vp-board 1/1/9 vp-link 1 no lt-expect"], got


def test_deleted_named_vp_board_attribute_keeps_the_board(monkeypatch):
    got = commands(monkeypatch, "deleted", {"vp_boards": [{"vp_board_id": "1/1/9", "admin_state": "up"}]})
    assert got and not any("no vp-board" in c for c in got), got
    assert all("vp-link" not in c for c in got), got


def test_deleted_vp_board_identity_removes_it(monkeypatch):
    got = commands(monkeypatch, "deleted", {"vp_boards": [{"vp_board_id": "1/1/9"}]})
    assert got == ["configure xdsl no vp-board 1/1/9"], got


def test_deleted_named_sub_node_attribute_resets_only_it(monkeypatch):
    got = commands(monkeypatch, "deleted", {"boards": [{"board_id": "1/1/1", "vect_fallback": {"spectrum_profile": 2}}]})
    assert got == ["configure xdsl board 1/1/1 vect-fallback no spectrum-profile"], got


def test_deleted_empty_sub_node_counts_as_identity_only(monkeypatch):
    # an empty value names nothing: 'vect_fallback: {}' is the identity alone and resets
    # the whole board, as documented in Xdsl_boards._reset_board
    got = commands(monkeypatch, "deleted", {"boards": [{"board_id": "1/1/1", "vect_fallback": {}}]})
    assert got == commands(monkeypatch, "deleted", {"boards": [{"board_id": "1/1/1"}]}), got
    assert any("vce-profile" in c for c in got), got


def test_overridden_of_boards_leaves_vp_boards(monkeypatch):
    got = commands(monkeypatch, "overridden", {"boards": [{"board_id": "1/1/1", "card_type": "ndlt-f", "admin_state": "up",
                                                           "vce_profile": 10, "vect_fallback": {"spectrum_profile": 2, "rtx_profile": 3}}]})
    assert not any("vp-board" in c for c in got), got


def test_overridden_of_vp_boards_leaves_boards(monkeypatch):
    got = commands(monkeypatch, "overridden", {"vp_boards": [{"vp_board_id": "1/1/9", "admin_state": "up", "vp_links": [
        {"link_id": 1, "lt_expect": "1/1/4"}, {"link_id": 2, "lt_expect": "1/1/3"}]}]})
    assert not any(" board " in c for c in got), got


INM = ("configure xdsl imp-noise-sensor near-end 1/1/3/1 inm-iat-step 3\n"
       "configure xdsl imp-noise-sensor far-end 1/1/3/1 inm-iat-step 4\n")


def test_xdsl_inm_overridden_of_near_end_leaves_far_end(monkeypatch):
    result = run_module(monkeypatch, "isam_xdsl_inm", {"state": "overridden", "config": {
        "near_end": [{"name": "1/1/3/1", "inm_iat_step": 3}]}}, INM)
    assert not result.get("failed"), result
    assert not any("far-end" in c for c in result["commands"]), result["commands"]


def _gathered(monkeypatch, module, config, device):
    result = run_module(monkeypatch, module, {"state": "gathered", "config": config}, device)
    assert not result.get("failed"), result
    return result


def test_a_default_only_xdsl_line_is_gathered_with_its_identity(monkeypatch):
    result = _gathered(monkeypatch, "isam_xdsl_lines", [{"name": "1/1/3/1"}], "configure xdsl line 1/1/3/1\n")
    assert result["gathered"] == [{"name": "1/1/3/1"}], result["gathered"]


def test_a_default_only_ethernet_line_is_gathered_with_its_identity(monkeypatch):
    result = _gathered(monkeypatch, "isam_ethernet_line", [{"if_index": "1/1/8/1"}], "configure ethernet line 1/1/8/1\n")
    assert result["gathered"] == [{"if_index": "1/1/8/1"}], result["gathered"]


def test_a_default_only_xdsl_profile_is_gathered_with_its_id(monkeypatch):
    result = _gathered(monkeypatch, "isam_xdsl_profiles", {"service_profiles": [{"id": 3}]},
                       "configure xdsl service-profile 3\n")
    assert result["gathered"]["service_profiles"] == [{"id": 3}], result["gathered"]
