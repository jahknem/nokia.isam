# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.network_template import (
    NetworkTemplate,
)


class Software_mngtTemplate(NetworkTemplate):
    def __init__(self, lines=None, module=None):
        super(Software_mngtTemplate, self).__init__(lines=lines, tmplt=self, module=module)

    # fmt: off
    PARSERS = [
        {
            "name": "database.version",
            "compval": "version",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\sdatabase\sversion\s(?P<version>\S+)$"
            ),
            "setval": "configure software-mngt database version {{ database.version }}",
            "result": {
                "database": {
                    "version": "{{ version }}",
                },
            },
        },
        {
            "name": "database.url",
            "compval": "url",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\sdatabase\surl\s(?P<url>\S+)$"
            ),
            "setval": "configure software-mngt database url {{ database.url }}",
            "result": {
                "database": {
                    "url": "{{ url }}",
                },
            },
        },
        {
            "name": "database.backup_options",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\sdatabase\s"
                r"backup\s(?P<backup>\S+)\s"
                r"backupv6\s(?P<backupv6>\S+)"
                r"(?:\sauto-backup-intvl\s(?P<auto_backup_interval>\d+))?$"
            ),
            "setval": "configure software-mngt database backup {{ database.backup }} backupv6 {{ database.backupv6 }}",
            "result": {
                "database": {
                    "backup": "{{ backup }}",
                    "backupv6": "{{ backupv6 }}",
                    "auto_backup_interval": "{{ auto_backup_interval }}",
                },
            },
        },
        {
            "name": "database.auto_backup_interval",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\sdatabase\s"
                r"auto-backup-intvl\s(?P<auto_backup_interval>\d+)$"
            ),
            "setval": "configure software-mngt database auto-backup-intvl {{ database.auto_backup_interval }}",
            "result": {
                "database": {
                    "auto_backup_interval": "{{ auto_backup_interval }}",
                },
            },
        },
        {
            "name": "oswp.options",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\soswp\s(?P<id>\S+)\s"
                r"primary-file-server-id\s(?P<primary_file_server_id>\S+)\s"
                r"second-file-server-id\s(?P<second_file_server_id>\S+)"
                r"(?:\s(?P<no_activate>no\s)?activate)?"
                r"(?:\s(?P<no_auto_verify>no\s)?auto-verify)?$"
            ),
            "setval": "configure software-mngt oswp {{ id }} primary-file-server-id {{ primary_file_server_id }} second-file-server-id {{ second_file_server_id }}",
            "result": {
                "oswp": [
                    {
                        "id": "{{ id }}",
                        "primary_file_server_id": "{{ primary_file_server_id }}",
                        "second_file_server_id": "{{ second_file_server_id }}",
                        "activate": "{{ False if no_activate is defined else True }}",
                        "auto_verify": "{{ False if no_auto_verify is defined else True }}",
                    }
                ],
            },
            "shared": True,
        },
        {
            "name": "oswp.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\soswp\s(?P<negate>no\s)?(?P<admin_state>admin-state)$"
            ),
            "setval": "configure software-mngt oswp {{ 'no ' if oswp.admin_state == false else '' }}admin-state",
            "result": {
                "oswp": {
                    "admin_state": "{{ False if negate is defined else True }}",
                },
            },
        },
        {
            "name": "sw_replacement_mode.mode",
            "compval": "mode",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\ssw-replacement-mode\s(?P<mode>\S+)$"
            ),
            "setval": "configure software-mngt sw-replacement-mode {{ sw_replacement_mode.mode }}",
            "result": {
                "sw_replacement_mode": {
                    "mode": "{{ mode }}",
                },
            },
        },
    ]
    # fmt: on
