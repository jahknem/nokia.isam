# Nokia ISAM Command Tree

This tree was derived from `DS-LIN-TEST-01` using the read-only command `info configure flat`.

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
