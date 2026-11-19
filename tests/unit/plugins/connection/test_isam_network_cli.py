from unittest.mock import Mock

from ansible.errors import AnsibleConnectionFailure

from ansible_collections.nokia.isam.plugins.connection.isam_network_cli import Connection


def test_edit_config_delegates_to_cliconf_and_resets_transport():
    connection = object.__new__(Connection)
    plugin = Mock()
    connection._sub_plugin = {"obj": plugin}
    connection._ssh_shell = Mock()
    transport = connection._ssh_type_conn = Mock()
    connection._connected = True

    result = connection.edit_config(candidate=["configure system"])

    assert result is plugin.edit_config.return_value
    plugin.edit_config.assert_called_once_with(candidate=["configure system"])
    assert connection._ssh_shell is None
    # the transport is closed but kept: it holds the options (remote_addr, ...) that a
    # newly created libssh transport would lack ("Hostname required")
    assert connection._ssh_type_conn is transport
    transport.close.assert_called_once_with()
    assert connection._connected is False


def test_edit_config_resets_transport_when_cliconf_fails():
    connection = object.__new__(Connection)
    plugin = Mock()
    plugin.edit_config.side_effect = RuntimeError("device rejected command")
    connection._sub_plugin = {"obj": plugin}
    connection._ssh_shell = Mock()
    transport = connection._ssh_type_conn = Mock()
    connection._connected = True

    try:
        connection.edit_config(candidate=["configure system"])
    except RuntimeError as exc:
        assert str(exc) == "device rejected command"
    else:
        raise AssertionError("edit_config should propagate cliconf failures")

    assert connection._ssh_shell is None
    # the transport is closed but kept: it holds the options (remote_addr, ...) that a
    # newly created libssh transport would lack ("Hostname required")
    assert connection._ssh_type_conn is transport
    transport.close.assert_called_once_with()
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


def test_reset_keeps_transport_options_for_reconnect():
    """Live finding: after a reset the next connect failed with 'Hostname required'."""
    class Transport(object):
        def __init__(self):
            self.options = {"remote_addr": "192.0.2.10"}
            self.closed = 0

        def close(self):
            self.closed += 1

        def get_option(self, name):
            return self.options[name]

    connection = object.__new__(Connection)
    connection._ssh_shell = None
    transport = connection._ssh_type_conn = Transport()
    connection._connected = True
    connection._reset_transport()
    assert connection._ssh_type_conn.get_option("remote_addr") == "192.0.2.10"
    assert transport.closed == 1


def test_reset_tolerates_a_transport_that_fails_to_close():
    connection = object.__new__(Connection)
    connection._ssh_shell = Mock(**{"close.side_effect": RuntimeError("gone")})
    transport = connection._ssh_type_conn = Mock(**{"close.side_effect": AttributeError("no session")})
    connection._connected = True
    connection._reset_transport()
    assert connection._ssh_shell is None and connection._ssh_type_conn is transport
