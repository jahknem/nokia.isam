from ansible_collections.nokia.isam.plugins.cliconf.isam import Cliconf


def _cliconf():
    plugin = object.__new__(Cliconf)
    plugin._device_info = {}
    plugin.sent = []

    def send_command(command, *a, **k):
        plugin.sent.append(command)
        return "ok"

    plugin.send_command = send_command
    plugin.get_device_operations = lambda *a, **k: {}
    plugin.check_edit_config_capability = lambda *a, **k: None
    return plugin


def test_edit_config_resets_context_before_configure_and_admin():
    plugin = _cliconf()
    plugin.edit_config(candidate=[
        "configure system id 1",
        "admin security ext-authenticator 1/1/1/1 clear-statistics",
    ])
    # both hierarchies are absolute paths from the root: reset before each
    assert plugin.sent == [
        "exit all", "configure system id 1",
        "exit all", "admin security ext-authenticator 1/1/1/1 clear-statistics",
    ]


def test_edit_config_does_not_reset_before_read_commands():
    plugin = _cliconf()
    plugin.edit_config(candidate=["info configure flat"])
    assert plugin.sent == ["info configure flat"]


def test_edit_config_returns_request_and_response():
    plugin = _cliconf()
    resp = plugin.edit_config(candidate=["admin security ext-authenticator 1/1/1/1 clear-statistics"])
    assert resp["request"] == ["admin security ext-authenticator 1/1/1/1 clear-statistics"]
    assert resp["response"] == ["ok"]