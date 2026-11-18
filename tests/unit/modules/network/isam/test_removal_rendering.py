from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_boards.xdsl_boards import (
    Xdsl_boards,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_boards import (
    Xdsl_boardsTemplate,
)


def test_isam_resource_removal_is_not_prefixed_with_no():
    resource = object.__new__(Xdsl_boards)
    resource._tmplt = Xdsl_boardsTemplate()
    resource.commands = []
    # (a board has no removal form: 'configure xdsl no board' is an invalid token, lab ISAM)
    resource.addcmd({"vp_board_id": "1/1/1"}, "vp_board", negate=True)
    assert resource.commands == ["configure xdsl no vp-board 1/1/1"]


def test_parser_without_removal_form_fails_instead_of_sending_no_configure():
    """netcommon would render "no configure ..."; the module must refuse instead."""
    import pytest
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.xdsl_lines.xdsl_lines import (
        Xdsl_lines,
    )
    from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.xdsl_lines import (
        Xdsl_linesTemplate,
    )

    class Module:
        def fail_json(self, **kwargs):
            raise RuntimeError(kwargs["msg"])

    resource = object.__new__(Xdsl_lines)
    resource._tmplt = Xdsl_linesTemplate()
    resource._module = Module()
    resource.commands = []
    resource.addcmd({"name": "1/1/3/1", "admin_up": True}, "admin_up", negate=True)
    assert resource.commands == ["configure xdsl line 1/1/3/1 no admin-up"]
    parser = next(p for p in resource._tmplt.PARSERS if p["name"] == "admin_up")
    parser_remval = parser.pop("remval")
    try:
        with pytest.raises(RuntimeError, match="no removal form"):
            resource.addcmd({"name": "1/1/3/1", "admin_up": True}, "admin_up", negate=True)
    finally:
        parser["remval"] = parser_remval
    assert resource.commands == ["configure xdsl line 1/1/3/1 no admin-up"]
