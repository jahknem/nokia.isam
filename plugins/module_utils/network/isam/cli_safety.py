# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""Control-character check for CLI command strings (defence in depth).

Values from module parameters are interpolated into ISAM CLI commands. A raw control
character in such a value changes what the device executes: a new line or carriage
return ends the command and starts another one (``admin equipment reboot-isam``), a tab
triggers command completion, and control keys such as control-u/-w/-x edit or cancel
the line being entered (ISAM CLI guide, "Command Repetition"). A printable string can
carry such characters only in their escaped form (``\\n``, ``\\r``, ``\\t``), never raw.

Every command is therefore checked for C0 control characters (U+0000-U+001F) and DEL
(U+007F) before it leaves a module, a targeted read, or the cliconf plugin. The error
names the command position (and the source) only, never the command text: a command can
carry a password, a secret or an SNMP community.
"""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

_CONTROL_RE = re.compile("[\x00-\x1f\x7f]")


class UnsafeCliCommandError(ValueError):
    """A CLI command contains a control character (see the module docstring)."""


def unsafe_command_indexes(commands):
    """Indexes (0-based) of the commands that are not strings or contain a control character.

    Bytes are checked byte-wise (the control characters are ASCII, so latin-1 maps
    each byte to the same code point)."""
    bad = []
    for index, command in enumerate(commands):
        if isinstance(command, bytes):
            command = command.decode("latin-1")
        if not isinstance(command, str) or _CONTROL_RE.search(command):
            bad.append(index)
    return bad


def check_cli_commands(commands, source="commands"):
    """Raise UnsafeCliCommandError unless every command is free of control characters.

    commands: a command string or a list of them. source names where they come from
    (a resource or the plugin) for the message. The message gives the 1-based positions
    of the offending commands, never their text (they may contain secrets). Returns
    the commands unchanged when they are safe.
    """
    listed = [commands] if isinstance(commands, str) else list(commands or [])
    bad = unsafe_command_indexes(listed)
    if bad:
        raise UnsafeCliCommandError(
            "%s: refusing to send command%s %s of %d: a value contains a control character "
            "(new line, carriage return, tab or another C0/DEL character), which would inject "
            "or alter CLI input. The command text is withheld because it may contain secrets."
            % (source, "s" if len(bad) > 1 else "", ", ".join("#%d" % (index + 1) for index in bad), len(listed)))
    return commands
