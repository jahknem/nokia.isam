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
                r"(?:backup\s(?P<backup>\S+)\s*)?"
                r"(?:backupv6\s(?P<backupv6>\S+)\s*)?"
                r"(?:\sauto-backup-intvl\s(?P<auto_backup_interval>\d+))?$"
            ),
            "setval": "configure software-mngt database{% if database.backup is defined %} backup {{ database.backup }}{% endif %}{% if database.backupv6 is defined %} backupv6 {{ database.backupv6 }}{% endif %}{% if database.auto_backup_interval is defined %} auto-backup-intvl {{ database.auto_backup_interval }}{% endif %}",
            "result": {
                "database": {
                    "backup": "{{ backup|default('') }}",
                    "backupv6": "{{ backupv6|default('') }}",
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
                r"(?:primary-file-server-id\s(?P<primary_file_server_id>\S+)\s)?"
                r"(?:second-file-server-id\s(?P<second_file_server_id>\S+))?"
                r"(?:\s(?P<no_activate>no\s)?activate)?"
                r"(?:\s(?P<no_auto_verify>no\s)?auto-verify)?"
                r"(?:\s(?P<no_on_schedule_time>no\s)?(?P<on_schedule_time>on-schedule-time))?$"
            ),
            "setval": "configure software-mngt oswp {{ id }} primary-file-server-id {{ primary_file_server_id }} second-file-server-id {{ second_file_server_id }}{% if activate is defined %} {{ 'activate' if activate else 'no activate' }}{% endif %}{% if auto_verify is defined %} {{ 'auto-verify' if auto_verify else 'no auto-verify' }}{% endif %}{% if on_schedule_time is defined %} {{ 'on-schedule-time' if on_schedule_time else 'no on-schedule-time' }}{% endif %}",
            "remval": "configure software-mngt no oswp {{ id }}",
            "result": {
                "oswp": [
                    {
                        "id": "{{ id }}",
                        "primary_file_server_id": "{{ primary_file_server_id }}",
                        "second_file_server_id": "{{ second_file_server_id }}",
                        "activate": "{{ False if no_activate is defined else True }}",
                        "auto_verify": "{{ False if no_auto_verify is defined else True }}",
                        "on_schedule_time": "{{ False if no_on_schedule_time is defined else (True if on_schedule_time is defined else '') }}",
                    }
                ],
            },
            "shared": True,
        },
        {
            "name": "oswp.admin_state",
            "compval": "admin_state",
            "getval": re.compile(
                r"^configure\ssoftware-mngt\soswp\s(?P<id>\S+)\s(?P<negate>no\s)?(?P<admin_state>admin-state)$"
            ),
            "setval": "configure software-mngt oswp {{ id }} {{ 'no ' if admin_state == false else '' }}admin-state",
            "result": {
                "oswp": [{
                    "id": "{{ id }}",
                    "admin_state": "{{ False if negate is defined else True }}",
                }],
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
