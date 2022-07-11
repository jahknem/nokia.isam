#
# (c) 2016 Red Hat Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible.plugins.terminal import TerminalBase


class TerminalModule(TerminalBase):
    # My terminal ends with a %, so use that here
    terminal_stdout_re = [
        re.compile(rb"\w+@\w+:[~/\w+]% "),
    ]

    ansi_re = TerminalBase.ansi_re + [
        # Color codes
        re.compile(rb"\x1b\[(\d+(;\d+)*)?m"),
        # Clear line (CSI K)
        re.compile(rb"\x1b\[K"),
        # Change default character set
        re.compile(rb"\x1b\(\w"),
        # Cursor position (CSI <n> <A-G>)
        re.compile(rb"\x1b\[\d+\w"),
        # Partial clear screen (CSI [n] J)
        re.compile(rb"\x1b\[\d*J"),
        # Xterm private sequences (CSI ? <n> <h|l>)
        re.compile(rb"\x1b\[\?\d+(h|l)"),
        # Xterm change keypad (ESC <=|>>)
        re.compile(rb"\x1b(=|>)"),
    ]
