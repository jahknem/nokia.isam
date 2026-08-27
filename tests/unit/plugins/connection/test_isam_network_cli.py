from unittest.mock import Mock

from ansible.errors import AnsibleConnectionFailure

from ansible_collections.nokia.isam.plugins.connection.isam_network_cli import Connection


def test_edit_config_delegates_to_cliconf_and_resets_transport():
    connection = object.__new__(Connection)
    plugin = Mock()
    connection._sub_plugin = {"obj": plugin}
    connection._ssh_shell = Mock()
    connection._ssh_type_conn = Mock()
    connection._connected = True

    result = connection.edit_config(candidate=["configure system"])

    assert result is plugin.edit_config.return_value
    plugin.edit_config.assert_called_once_with(candidate=["configure system"])
    assert connection._ssh_shell is None
    assert connection._ssh_type_conn is None
    assert connection._connected is False


def test_edit_config_resets_transport_when_cliconf_fails():
    connection = object.__new__(Connection)
    plugin = Mock()
    plugin.edit_config.side_effect = RuntimeError("device rejected command")
    connection._sub_plugin = {"obj": plugin}
    connection._ssh_shell = Mock()
    connection._ssh_type_conn = Mock()
    connection._connected = True

    try:
        connection.edit_config(candidate=["configure system"])
    except RuntimeError as exc:
        assert str(exc) == "device rejected command"
    else:
        raise AssertionError("edit_config should propagate cliconf failures")

    assert connection._ssh_shell is None
    assert connection._ssh_type_conn is None
    assert connection._connected is False


def test_edit_config_requires_cliconf_plugin():
    connection = object.__new__(Connection)
    connection._sub_plugin = {}

    try:
        connection.edit_config(candidate=[])
    except AnsibleConnectionFailure as exc:
        assert "cliconf plugin" in str(exc)
    else:
        raise AssertionError("missing cliconf plugin should fail")
