from unittest.mock import Mock, patch

from ansible_collections.nokia.isam.plugins.connection.isam_network_cli import Connection


class TestIsamNetworkCliConnection(object):
    def test_transient_connect_failure_resets_transport_and_retries(self):
        connection = object.__new__(Connection)
        connection._messages = []
        connection.get_option = Mock(
            side_effect=lambda option: 1 if option == "isam_connect_retries" else False
        )
        connection._reset_transport = Mock()
        parent_connect = Mock(
            side_effect=[RuntimeError("CLI session closed before prompt"), "connected"]
        )

        with patch.object(Connection.__mro__[1], "_connect", parent_connect), patch(
            "ansible_collections.nokia.isam.plugins.connection.isam_network_cli.time.sleep"
        ) as sleep:
            result = connection._connect()

        assert result == "connected"
        connection._reset_transport.assert_called_once_with()
        sleep.assert_called_once_with(2)

    def test_paramiko_eof_during_shell_request_is_retried(self):
        connection = object.__new__(Connection)
        connection._messages = []
        connection.get_option = Mock(
            side_effect=lambda option: 1 if option == "isam_connect_retries" else False
        )
        connection._reset_transport = Mock()
        parent_connect = Mock(side_effect=[EOFError(), "connected"])

        with patch.object(Connection.__mro__[1], "_connect", parent_connect), patch(
            "ansible_collections.nokia.isam.plugins.connection.isam_network_cli.time.sleep"
        ):
            assert connection._connect() == "connected"

        connection._reset_transport.assert_called_once_with()

    def test_connect_retry_is_disabled_by_default(self):
        connection = object.__new__(Connection)
        connection._messages = []
        connection.get_option = Mock(return_value=0)
        parent_connect = Mock(side_effect=RuntimeError("Max. Sessions Reached."))

        with patch.object(Connection.__mro__[1], "_connect", parent_connect):
            try:
                connection._connect()
            except Exception as exc:
                assert str(exc) == (
                    "ISAM connection failed during connect (RuntimeError): "
                    "Max. Sessions Reached."
                )
            else:
                raise AssertionError("expected session-limit failure")

        parent_connect.assert_called_once_with()

    def test_authentication_failure_is_never_retried(self):
        connection = object.__new__(Connection)
        connection._messages = []
        connection.get_option = Mock(
            side_effect=lambda option: 3 if option == "isam_connect_retries" else False
        )
        parent_connect = Mock(side_effect=RuntimeError("Failed to authenticate"))

        with patch.object(Connection.__mro__[1], "_connect", parent_connect):
            try:
                connection._connect()
            except RuntimeError as exc:
                assert str(exc) == "Failed to authenticate"
            else:
                raise AssertionError("expected authentication failure")

        parent_connect.assert_called_once_with()

    def test_authentication_retry_requires_explicit_opt_in(self):
        connection = object.__new__(Connection)
        connection._messages = []
        connection.get_option = Mock(
            side_effect=lambda option: 1
            if option == "isam_connect_retries"
            else option == "isam_retry_authentication"
        )
        connection._reset_transport = Mock()
        parent_connect = Mock(
            side_effect=[RuntimeError("Failed to authenticate"), "connected"]
        )

        with patch.object(Connection.__mro__[1], "_connect", parent_connect), patch(
            "ansible_collections.nokia.isam.plugins.connection.isam_network_cli.time.sleep"
        ):
            assert connection._connect() == "connected"

        connection._reset_transport.assert_called_once_with()

    def test_reset_transport_discards_shell_and_ssh_connection(self):
        connection = object.__new__(Connection)
        connection._ssh_shell = Mock()
        connection._ssh_type_conn = Mock()
        connection._connected = True

        shell = connection._ssh_shell
        ssh_connection = connection._ssh_type_conn
        connection._reset_transport()

        shell.close.assert_called_once_with()
        ssh_connection.close.assert_called_once_with()
        assert connection._ssh_shell is None
        assert connection._ssh_type_conn is None
        assert connection._connected is False

    def test_unknown_connect_error_is_not_retried(self):
        connection = object.__new__(Connection)
        connection._messages = []
        connection.get_option = Mock(
            side_effect=lambda option: 3 if option == "isam_connect_retries" else False
        )
        parent_connect = Mock(side_effect=ValueError("bad plugin state"))

        with patch.object(Connection.__mro__[1], "_connect", parent_connect):
            try:
                connection._connect()
            except Exception as exc:
                assert "ValueError" in str(exc)
                assert "bad plugin state" in str(exc)
            else:
                raise AssertionError("expected connection failure")

        parent_connect.assert_called_once_with()
