from unittest.mock import Mock

from ansible.errors import AnsibleConnectionFailure

from ansible_collections.nokia.isam.plugins.terminal.isam import TerminalModule


class TestIsamTerminal(object):
    def test_session_limit_is_both_error_and_terminal_response(self):
        terminal = TerminalModule(Mock())
        response = b"Max. Sessions Reached.\r\n"

        assert any(regex.search(response) for regex in terminal.terminal_stdout_re)
        assert any(regex.search(response) for regex in terminal.terminal_stderr_re)

    def test_open_shell_initializes_batch_mode(self):
        connection = Mock()
        connection.exec_command.return_value = ""

        TerminalModule(connection).on_open_shell()

        assert connection.exec_command.call_args_list == [
            (("environment mode batch",),),
            (("environment inhibit-alarms",),),
            (("exit",),),
        ]

    def test_closed_session_is_detected_before_commands_are_sent(self):
        connection = Mock()
        connection.exec_command.return_value = None

        try:
            TerminalModule(connection).on_open_shell()
        except AnsibleConnectionFailure as exc:
            assert str(exc) == "CLI session closed before prompt"
        else:
            raise AssertionError("expected closed session failure")

        connection.exec_command.assert_called_once_with("environment mode batch")
