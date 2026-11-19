from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    NODES_BY_KEY,
    Software_mngtTemplate,
    diff_commands,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import (
    Software_mngtArgs,
)


def test_software_mngt_template_parses_live_flat_configuration():
    # the actual lab ISAM 'info configure software-mngt detail flat' lines
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt sw-replacement-mode upgrade-via-standby",
            "configure software-mngt oswp 1 primary-file-server-id 192.0.2.11 second-file-server-id 0.0.0.0 no activate no auto-verify no on-schedule-time",
            "configure software-mngt oswp 2 primary-file-server-id 192.0.2.9 second-file-server-id 0.0.0.0 no activate no auto-verify no on-schedule-time",
            "configure software-mngt database no activate backup activate:192.0.2.10:backup/ backupv6 activate:::/backup/ no auto-backup-intvl",
        ]
    ).parse()

    assert parsed == {
        "database": {
            "activate": None,
            "backup": "activate:192.0.2.10:backup/",
            "backupv6": "activate:::/backup/",
            "auto_backup_interval": None,
        },
        "oswp": [
            {"id": "1", "primary_file_server_id": "192.0.2.11", "second_file_server_id": "0.0.0.0",
             "activate": None, "auto_verify": None, "on_schedule_time": None},
            {"id": "2", "primary_file_server_id": "192.0.2.9", "second_file_server_id": "0.0.0.0",
             "activate": None, "auto_verify": None, "on_schedule_time": None},
        ],
        "sw_replacement_mode": {"mode": "upgrade-via-standby"},
    }


def test_software_mngt_template_parses_negated_oswp_values():
    # 'no activate'/'no auto-verify' are the device default: read as unset (None), not False
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt oswp 1 primary-file-server-id 192.0.2.1 second-file-server-id 0.0.0.0 no activate no auto-verify",
        ]
    ).parse()

    assert parsed["oswp"] == [
        {
            "id": "1",
            "primary_file_server_id": "192.0.2.1",
            "second_file_server_id": "0.0.0.0",
            "activate": None,
            "auto_verify": None,
        }
    ]


def test_software_mngt_template_parses_set_oswp_values():
    # data loss before: activate after-download / auto-verify enabled were read as True
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt oswp 1 primary-file-server-id 192.0.2.1 second-file-server-id 0.0.0.0 activate after-download auto-verify enabled",
        ]
    ).parse()

    assert parsed["oswp"][0]["activate"] == "after-download"
    assert parsed["oswp"][0]["auto_verify"] == "enabled"


def test_software_mngt_template_parses_on_schedule_time_value():
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt oswp 1 primary-file-server-id 192.0.2.1 second-file-server-id 0.0.0.0 no on-schedule-time",
        ]
    ).parse()
    assert parsed["oswp"][0]["on_schedule_time"] is None


def test_software_mngt_template_round_trips_backup_interval_and_scoped_admin_state():
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt database backup backup-v4 backupv6 backup-v6 auto-backup-intvl 60",
            "configure software-mngt oswp 7 no admin-state",
        ]
    ).parse()
    assert parsed["database"]["auto_backup_interval"] == 60
    assert parsed["oswp"] == [{"id": "7", "admin_state": False}]

    rendered = diff_commands(
        NODES_BY_KEY["database"], None,
        {"backup": "backup-v4", "auto_backup_interval": 60}, {}, "rendered",
    )
    assert rendered == ["configure software-mngt database backup backup-v4 auto-backup-intvl 60"]


def test_software_mngt_oswp_schema_is_a_list_and_renders_records():
    oswp = Software_mngtArgs.argument_spec["config"]["options"]["oswp"]
    assert oswp["type"] == "list"
    assert oswp["elements"] == "dict"

    rendered = diff_commands(
        NODES_BY_KEY["oswp"], "1",
        {"primary_file_server_id": "192.0.2.1", "second_file_server_id": "0.0.0.0"}, {}, "rendered",
    )
    assert rendered == ["configure software-mngt oswp 1 primary-file-server-id 192.0.2.1 second-file-server-id 0.0.0.0"]
