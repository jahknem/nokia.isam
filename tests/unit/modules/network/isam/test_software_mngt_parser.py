from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.software_mngt import (
    Software_mngtTemplate,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.software_mngt.software_mngt import (
    Software_mngtArgs,
)


def test_software_mngt_template_parses_live_flat_configuration():
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt sw-replacement-mode upgrade-via-standby",
            "configure software-mngt oswp 1 primary-file-server-id 10.200.1.11 second-file-server-id 0.0.0.0",
            "configure software-mngt oswp 2 primary-file-server-id 10.199.200.9 second-file-server-id 0.0.0.0",
            "configure software-mngt database backup activate:10.199.200.10:DSLAM_Konfig_Backup_R6-2/DS-LIN-TEST-01/ backupv6 activate:::/DSLAM_Konfig_Backup_R6-2/DS-LIN-TEST-01/",
        ]
    ).parse()

    assert parsed == {
        "database": {
            "backup": "activate:10.199.200.10:DSLAM_Konfig_Backup_R6-2/DS-LIN-TEST-01/",
            "backupv6": "activate:::/DSLAM_Konfig_Backup_R6-2/DS-LIN-TEST-01/",
        },
        "oswp": [
            {
                "id": 1,
                "primary_file_server_id": "10.200.1.11",
                "second_file_server_id": "0.0.0.0",
                "activate": True,
                "auto_verify": True,
            },
            {
                "id": 2,
                "primary_file_server_id": "10.199.200.9",
                "second_file_server_id": "0.0.0.0",
                "activate": True,
                "auto_verify": True,
            },
        ],
        "sw_replacement_mode": {"mode": "upgrade-via-standby"},
    }


def test_software_mngt_template_parses_negated_oswp_flags():
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt oswp 1 primary-file-server-id 10.0.0.1 second-file-server-id 0.0.0.0 no activate no auto-verify",
        ]
    ).parse()

    assert parsed["oswp"] == [
        {
            "id": 1,
            "primary_file_server_id": "10.0.0.1",
            "second_file_server_id": "0.0.0.0",
            "activate": False,
            "auto_verify": False,
        }
    ]


def test_software_mngt_template_parses_on_schedule_time_flag():
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt oswp 1 primary-file-server-id 10.0.0.1 second-file-server-id 0.0.0.0 no on-schedule-time",
        ]
    ).parse()

    assert parsed["oswp"] == [
        {
            "id": 1,
            "primary_file_server_id": "10.0.0.1",
            "second_file_server_id": "0.0.0.0",
            "activate": True,
            "auto_verify": True,
            "on_schedule_time": False,
        }
    ]


def test_software_mngt_template_round_trips_backup_interval_and_scoped_admin_state():
    parsed = Software_mngtTemplate(
        lines=[
            "configure software-mngt database backup backup-v4 backupv6 backup-v6 auto-backup-intvl 60",
            "configure software-mngt oswp 7 no admin-state",
        ]
    ).parse()
    assert parsed["database"]["auto_backup_interval"] == 60
    assert parsed["oswp"] == [{"id": 7, "admin_state": False}]

    rendered = Software_mngtTemplate().render(
        {"database": {"backup": "backup-v4", "auto_backup_interval": 60}},
        "database.backup_options",
    )
    assert rendered == "configure software-mngt database backup backup-v4 auto-backup-intvl 60"


def test_software_mngt_oswp_schema_is_a_list_and_renders_records():
    oswp = Software_mngtArgs.argument_spec["config"]["options"]["oswp"]
    assert oswp["type"] == "list"
    assert oswp["elements"] == "dict"

    rendered = Software_mngtTemplate().render(
        {
            "id": "1",
            "primary_file_server_id": "10.0.0.1",
            "second_file_server_id": "0.0.0.0",
        },
        "oswp.options",
    )
    assert rendered == "configure software-mngt oswp 1 primary-file-server-id 10.0.0.1 second-file-server-id 0.0.0.0"
