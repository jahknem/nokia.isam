# Nokia ISAM Command Tree

This tree was derived from `DS-LIN-TEST-01` using the read-only commands
`info configure flat` and `info configure <family> detail`.

The counts show how many configured lines were observed for each command family on that device. They are not a complete product command reference. Use the Nokia CLI PDFs in `docs/nokia_docs/` as the source of truth for command syntax and options.

## Live Configure Tree

```text
configure
|-- alarm                     66
|   |-- custom-profile         1
|   |-- delta-log              1
|   |-- entry                  1
|   |-- filter                62
|   `-- log-sev-level          1
|-- ani                       48
|   `-- ont                   48
|-- bridge                   811
|   |-- ageing-time            1
|   `-- port                 810
|-- dhcp-server                1
|   `-- start-addr             1
|-- equipment                163
|   |-- applique               1
|   |-- ont                  146
|   |-- protection-group       2
|   |-- replan                 1
|   |-- shelf                  1
|   `-- slot                  12
|-- ethernet                 160
|   |-- line                  72
|   `-- ont                   88
|-- generic-pon                1
|   `-- dpinteg-threshold      1
|-- igmp                       1
|   `-- mcast-svc-context      1
|-- interface               1054
|   |-- alarm                  3
|   |-- cage                  64
|   `-- port                 987
|-- iphost                     1
|-- li_vlan                    1
|   `-- vlan-id                1
|-- link-agg                 108
|   |-- group                 72
|   `-- port                  36
|-- mcast                      2
|   `-- general                2
|-- mcast-control              1
|   `-- mcast-svc-context      1
|-- ntp                       48
|   `-- ont                   48
|-- pon                      129
|   `-- interface            129
|-- qos                     1621
|   |-- dn-ctrl-pkt            9
|   |-- dscp-map-dot1p        64
|   |-- interface           1394
|   |-- profiles             137
|   |-- tc-map-dot1p           8
|   `-- up-ctrl-pkt            9
|-- software-mngt              4
|   |-- database               1
|   |-- oswp                   2
|   `-- sw-replacement-mode    1
|-- system                    63
|   |-- id                     1
|   |-- loop-id-syntax         1
|   |-- max-lt-link-speed      1
|   |-- relay-id-syntax        1
|   |-- security              33
|   |-- sntp                   4
|   |-- sync-if-timing        13
|   |-- syslog                 8
|   `-- transaction            1
|-- trap                      34
|   |-- definition            33
|   `-- manager                1
|-- vlan                     101
|   |-- broadcast-frames       1
|   |-- id                    88
|   |-- priority-regen        10
|   |-- tpid                   1
|   `-- vmac-address-format    1
|-- voice                      5
|   `-- sip                    5
|-- xdsl                     182
|   |-- board                  2
|   |-- dpbo-profile          28
|   |-- line                  96
|   |-- service-profile       10
|   |-- spectrum-profile      42
|   |-- vce-profile            1
|   |-- vect-profile           1
|   `-- vp-board               2
|-- xdsl-bonding               1
|   `-- group-assembly-time    1
`-- xstp                      37
    |-- general                1
    `-- port                  36
```

## Currently Covered Command Areas

These areas have resource modules today, at least partially:

| Command family | Module |
| --- | --- |
| `configure interface port` | `nokia.isam.isam_interfaces` |
| `configure bridge ageing-time` | `nokia.isam.isam_bridges` |
| `configure bridge port` | `nokia.isam.isam_bridges` |
| `configure vlan id` | `nokia.isam.isam_vlans` |
| `configure ethernet line` | `nokia.isam.isam_ethernet_line` |

## Detail Vocabulary Confirmed

The detail suffix exposed these additional words on the current target. These
are emitted words observed in configured output, not a complete product-wide
CLI reference.

| Family | Detail words observed |
| --- | --- |
| `ani ont` | `tca-thresh`, `lower-optical-th`, `upper-optical-th`, `rssi-profile` |
| `voice sip` | `lineid-syn-prof`, `vsp`, `register`, `redundancy`, `system`, `redundancy-cmd`, `statistics`, `cas-nsm-prof`, `session-timer`, `stats-config` |
| `software-mngt` | `sw-replacement-mode`, `oswp`, `primary-file-server-id`, `second-file-server-id`, `activate`, `auto-verify`, `on-schedule-time`, `database`, `backup`, `backupv6`, `auto-backup-intvl` |
| `pon interface` | `label`, `fec-dn`, `ponid-interval`, `ponid-identifier`, `tconts-per-frame`, `tc-layer`, `fec-tc-layer`, `xg-tc-layer`, `mcast-tc-layer`, `deact-ont-tca`, `otdr`, `phy-layer`, `oper-state`, `admin-state` |
| `qos` | `interface`, `profiles`, `queue`, `queue-profile`, `shaper-profile`, `bandwidth-profile`, `cac-profile`, `up-ctrl-pkt`, `dn-ctrl-pkt`, `dscp-map-dot1p`, `tc-map-dot1p`, `pbit-scheduling`, `upstr-prot-dsl` |
| `system` | `id`, `security`, `sntp`, `sync-if-timing`, `syslog`, `transaction`, `loop-id-syntax`, `relay-id-syntax`, `max-lt-link-speed`, `welcome-banner`, `zero-touch-provision` |
| `vlan` | `id`, `name`, `mode`, `broadcast-frames`, `priority-regen`, `priority-policy`, `tpid`, `vmac-address-format`, `circuit-id-dhcp`, `remote-id-dhcp`, `circuit-id-pppoe`, `remote-id-pppoe`, `dhcpv6-itf-id`, `dhcpv6-remote-id` |
| `xdsl` | `board`, `line`, `dpbo-profile`, `service-profile`, `spectrum-profile`, `vce-profile`, `vect-profile`, `vp-board`, `adsl2-plus`, `vdsl`, `vdsl2`, `service-profile-name`, `spectrum-profile-name`, `tca-line-threshold` |

The optional PON modules use the PDF-defined paths `info configure epon
interface flat`, `info configure channel-group flat`, and `info configure
channel-pair interface flat`. If a corresponding hardware/software feature is
not installed, ISAM may return `invalid token`; the collection treats that
response as an empty gathered resource while still surfacing authentication,
transport, and other command failures.

The complete sanitized command responses remain available in `/tmp/opencode/detail_*.out` for parser-by-parser comparison. No credentials or mutating commands were used.

## Live Examples By Family

```text
configure alarm log-sev-level critical log-full-action wrap non-itf-rep-sev-level major
configure ani ont tca-thresh 1/1/2/1/1
configure bridge port 1/1/8/1 max-unicast-mac 100 qos-profile name:P2PqpsUP20Mbps
configure equipment shelf 1/1 planned-type nfxs-b
configure ethernet ont 1/1/5/1/1/1/1 cust-info Y654321 auto-detect auto
configure interface port pon:1/1/2/1 admin-up user ""
configure link-agg group 1/1/8/1 load-sharing-policy mac-src swo-revert enable mode static master-iwf unset
configure pon interface 1/1/5/1 label 5/1 fec-dn enable ponid-interval 1 ponid-identifier cccccc5a1ccccc tconts-per-frame 64
configure qos interface 1/1/8/1 upstream-queue 0 bandwidth-profile name:qpsUP20Mbps
configure system sntp server-ip-addr 10.199.145.57 polling-rate 60 enable timezone-offset 60
configure vlan id 720 name VOICE-720 mode residential-bridge
configure xdsl line 1/1/1/1 service-profile 11 spectrum-profile 101
configure xstp port 1/1/8/1 path-cost 200000
```

## Safe Discovery Rules

When expanding this tree from a live MSAN, use only read-only commands such as:

```text
info configure flat
info configure <family> flat
info configure <family> detail
show <family>
```

Do not use live `configure`, `clear`, `admin`, `test`, or `debug` commands during discovery.
