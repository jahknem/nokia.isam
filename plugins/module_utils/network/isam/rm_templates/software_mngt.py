# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

"""
Attribute table of the isam_software_mngt resource (global software management).

The device prints ('info configure software-mngt detail flat', lab ISAM)::

    configure software-mngt sw-replacement-mode upgrade-via-standby
    configure software-mngt oswp 1 primary-file-server-id 192.0.2.11 second-file-server-id 0.0.0.0 no activate no auto-verify no on-schedule-time
    configure software-mngt database no activate backup activate:192.0.2.10:path/ backupv6 activate:::/path/ no auto-backup-intvl

TABLE (CLI guide) drives the facts, the config class and the argument spec (see
attribute_table.py). database version/url and oswp admin-state are commands of their own
(form "solo"); sw-replacement-mode takes its value directly (form "scalar").
on-schedule-time (a datetime) and backup/backupv6 (activate:host:path/ strings) are kept
as raw string values.
"""

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.attribute_table import (
    Attr,
    AttributeTable,
    Node,
    TableTemplate,
)

TABLE = AttributeTable("configure software-mngt", (
    Node("database", "database", (
        Attr("version", "version", "str", removable=False, form="solo"),
        Attr("url", "url", "str", removable=False, form="solo"),
        Attr("activate", "activate", "str", "manually", ["after-download", "manually"]),
        Attr("backup", "backup", "str", "manually"),
        Attr("backupv6", "backupv6", "str", "manually"),
        Attr("auto_backup_interval", "auto-backup-intvl", "int", 24),
    )),
    Node("oswp", "oswp", (
        Attr("primary_file_server_id", "primary-file-server-id", "str", removable=False),
        Attr("second_file_server_id", "second-file-server-id", "str", removable=False),
        Attr("download_set", "download-set", "str", choices=["min-set", "actual-set", "complete-set"], removable=False),
        Attr("autofetch", "autofetch", "str", choices=["disabled", "enabled"], removable=False),
        Attr("activate", "activate", "str", "manually", ["manually", "after-download", "on-schedule"]),
        Attr("auto_verify", "auto-verify", "str", "disabled", ["disabled", "enabled"]),
        Attr("on_schedule_time", "on-schedule-time", "str"),
        Attr("admin_state", "admin-state", "flag", form="solo"),
    ), identity="id"),
    Node("sw_replacement_mode", "sw-replacement-mode", (
        Attr("mode", "sw-replacement-mode", "str",
             choices=["upgrade-via-active", "upgrade-via-standby", "lt-by-lt"], removable=False, form="scalar"),
    )),
))


class Software_mngtTemplate(TableTemplate):
    TABLE = TABLE
