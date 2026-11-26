"""Targeted gathering cases: system security slice 2 and system sync-if-timing."""



def case(module, config, lines, sibling_config, sibling, marker, sibling_marker):
    return {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
            "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}


_SEC = "configure system security "
_SYNC = "configure system sync-if-timing "

CASES = {
    "isam_system_security:snmp_notify_views": case(
        "isam_system_security", {"snmp_notify_views": [{"name": "everything"}]},
        [_SEC + "snmp notify-view everything subtree * type include"],
        {"snmp_notify_views": [{"name": "nothing"}]},
        [_SEC + "snmp notify-view nothing subtree * type exclude"],
        "everything", "nothing"),
    "isam_system_security:domains": case(
        "isam_system_security", {"domains": [{"name": "DomA"}]},
        [_SEC + "domain DomA authenticator radius:PolA"],
        {"domains": [{"name": "DomB"}]},
        [_SEC + "domain DomB authenticator radius:PolB"],
        "radius:PolA", "radius:PolB"),
    "isam_system_security:slots": case(
        "isam_system_security", {"slots": [{"slot": "nt-a"}]},
        [_SEC + "slot nt-a debug-usb"],
        {"slots": [{"slot": "nt-b"}]},
        [_SEC + "slot nt-b debug-usb"],
        "nt-a", "nt-b"),
    "isam_system_security:ssh.sftp_users": case(
        "isam_system_security", {"ssh": {"sftp_users": [{"name": "sftp-a"}]}},
        [_SEC + "ssh sftp-user sftp-a auth-type password"],
        {"ssh": {"sftp_users": [{"name": "sftp-b"}]}},
        [_SEC + "ssh sftp-user sftp-b auth-type password"],
        "sftp-a", "sftp-b"),
    "isam_system_security:filetransfer.servers": case(
        "isam_system_security", {"filetransfer": {"servers": [{"server": "10.0.0.1"}]}},
        [_SEC + "filetransfer server 10.0.0.1 user-name ftp-a"],
        {"filetransfer": {"servers": [{"server": "10.0.0.2"}]}},
        [_SEC + "filetransfer server 10.0.0.2 user-name ftp-b"],
        "ftp-a", "ftp-b"),
    "isam_system_security:peripheral_mgnt.mac_filters": case(
        "isam_system_security", {"peripheral_mgnt": {"mac_filters": [{"index": 1}]}},
        [_SEC + "peripheral-mgnt mac-filter 1 filter 00:11:22:33:44:01"],
        {"peripheral_mgnt": {"mac_filters": [{"index": 10}]}},
        [_SEC + "peripheral-mgnt mac-filter 10 filter 00:11:22:33:44:10"],
        "00:11:22:33:44:01", "00:11:22:33:44:10"),
    "isam_system_security:pae.ports": case(
        "isam_system_security", {"pae": {"ports": [{"port": "1/1/4/19"}]}},
        [_SEC + "pae port 1/1/4/19 initialize",
         _SEC + "pae authenticator 1/1/4/19 quiet-period 61",
         _SEC + "pae ext-authenticator 1/1/4/19 handshake-period 31"],
        {"pae": {"ports": [{"port": "1/1/4/20"}]}},
        [_SEC + "pae port 1/1/4/20 initialize",
         _SEC + "pae authenticator 1/1/4/20 quiet-period 62"],
        "1/1/4/19", "1/1/4/20"),
    "system:sync_if_timing.ssm": case(
        "isam_system", {"sync_if_timing": {"ssm": [{"reference": "bits-a"}]}},
        [_SYNC + "ssm bits-a ssmenable default-ql clk-ql-prc target-ql clk-ql-dnu"],
        {"sync_if_timing": {"ssm": [{"reference": "synce-1"}]}},
        [_SYNC + "ssm synce-1 ssmenable default-ql clk-ql-prc target-ql clk-ql-dnu"],
        "bits-a", "synce-1"),
    "system:sync_if_timing.synce": case(
        "isam_system", {"sync_if_timing": {"synce": [{"reference": "synce-1"}]}},
        [_SYNC + "synce synce-1 nt-a:xfp:1"],
        {"sync_if_timing": {"synce": [{"reference": "synce-2"}]}},
        [_SYNC + "synce synce-2 nt-b:xfp:1"],
        "nt-a:xfp:1", "nt-b:xfp:1"),
    "system:sync_if_timing.ssmout_synce": case(
        "isam_system", {"sync_if_timing": {"ssmout_synce": [{"port": "nt-a:xfp:1"}]}},
        [_SYNC + "ssmout-synce nt-a:xfp:1 ssmout-enable"],
        {"sync_if_timing": {"ssmout_synce": [{"port": "nt-b:xfp:2"}]}},
        [_SYNC + "ssmout-synce nt-b:xfp:2 ssmout-enable"],
        "nt-a:xfp:1", "nt-b:xfp:2"),
}
