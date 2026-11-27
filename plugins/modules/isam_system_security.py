#!/usr/bin/python
# -*- coding: utf-8 -*-
# GNU General Public License v3.0+
# (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
module: isam_system_security
short_description: Manages Nokia ISAM system security (operators, profiles, SNMP, RADIUS, SSH, 802.1X, ...).
description:
  - Manages C(configure system security) on Nokia ISAM.
  - Secret values (operator, SFTP and file transfer passwords, RADIUS secrets, SNMP community strings) are redacted in output.
  - Replayed device or Ansible-redacted credential values preserve existing credentials;
    they are never sent as passwords or secrets and cannot create new entries.
  - With C(merged) or C(replaced), entries whose identity is redacted (such as an SNMP
    community name) are left unchanged with a warning. Supply the concrete identity to
    manage them. Redacted identities are rejected in C(rendered), C(deleted), C(overridden)
    and targeted C(gathered); the module never guesses which hidden object was intended.
  - A redacted community embedded in a notify profile's C(snmp_version) preserves the
    existing version only; supply a concrete community to create or change the version.
  - Instance lists are matched by their identity. Instances that can be created are removed with
    C(no <node> <identity>); fixed instances (slots, MAC filters, 802.1X ports) and settings blocks are
    reset attribute by attribute with C(no <attr>).
  - With I(state=deleted) and I(config), only the sections named in I(config) are deleted; an SNMP view,
    notify view or community given by name alone matches all its subtrees or host addresses.
    An entry given by its identity alone is removed (or, if fixed, fully reset); an entry or
    settings block naming attributes resets only those attributes.
  - Passwords and secrets are never readable from the device, so C(replaced) and C(overridden)
    keep them when an entry omits them; they are only changed when given.
  - C(overridden) fails instead of removing a profile that a kept operator still uses.
version_added: 1.0.0
author: Jan Kühnemund (@jahknem)
options:
  config:
    description: The provided system security configuration.
    type: dict
    suboptions:
      operators:
        type: list
        elements: dict
        description:
          - 'Local CLI operators (C(configure system security operator <name>)).'
          - 'An operator is created with I(profile) and I(password), both mandatory at creation; removal uses C(no operator <name>).'
        suboptions:
          name:
            type: str
            required: true
            description: 'Operator (login) name.'
          password:
            type: str
            description:
              - 'Login password (C(password)), as printed by the device (encrypted) or a new plain value.'
              - 'A masked or redacted value keeps the device value. Not logged.'
          profile:
            type: str
            description: 'Operator profile the operator belongs to (C(profile)), see I(profiles); only settable at creation.'
          prompt:
            type: str
            description: 'CLI prompt specification of the operator (C(prompt)); device default empty (the profile''s prompt applies).'
          description:
            type: str
            description: 'Free-text description of the operator (C(description)).'
          more:
            type: bool
            description: 'Pass CLI output through the C(more) pager (C(more)).'
          confirm_prompt:
            type: bool
            description: 'Ask for confirmation before executing a command (C(confirm-prompt)).'
          bgn_time:
            type: str
            description: 'Start of the operator''s validity period (C(bgn-time)), C(YYYY-MM-DD:hh:mm:ss); device default C(1970-01-01:00:00:00).'
          end_time:
            type: str
            description: 'End of the operator''s validity period (C(end-time)), C(YYYY-MM-DD:hh:mm:ss); device default C(2035-12-31:23:59:59).'
      profiles:
        type: list
        elements: dict
        description:
          - 'Operator profiles (C(configure system security profile <name>)): prompt, timeouts and per-area access rights.'
          - 'Removal uses C(no profile <name>).'
        suboptions:
          name:
            type: str
            required: true
            description: 'Profile name.'
          description:
            type: str
            description: 'Free-text description of the profile (C(description)).'
          slot_numbering:
            type: str
            description: 'Slot numbering scheme shown to the profile''s operators (C(slot-numbering)): C(type-based), C(position-based) or C(legacy-based) (device default).'
          prompt:
            type: str
            description: 'CLI prompt specification (C(prompt)), for example C(%s:%n%d%c ) (the device default).'
          password_timeout:
            type: str
            description: 'Maximum number of days a password may stay unchanged (C(password-timeout), 0-365); device default C(0), no expiry.'
          terminal_timeout:
            type: str
            description: 'Terminal inactivity timeout in minutes (C(terminal-timeout), 0-120); device default C(30).'
          permissions:
            type: dict
            description:
              - 'Access right per command area (for example C(aaa), C(alarm), C(equipment), C(security)), value C(read), C(write) or C(none).'
              - 'Rendered as C(<area> <value>) flags of the profile; C(none) is the device default.'
      snmp_communities:
        type: list
        elements: dict
        description:
          - SNMP communities, identified by I(name) and I(host_address) (one community can be bound to several host addresses).
          - Removal uses C(configure system security snmp no community <name> host-address <address>) (standard ISAM form, not verified on a device).
        suboptions:
          name:
            type: str
            required: true
            description:
              - 'SNMP community string (C(snmp community <name>)).'
              - 'It is the SNMP access secret, so it is not logged and is redacted in output.'
          host_address:
            type: str
            description: 'IPv4/IPv6 address and prefix length of the hosts allowed to use the community (C(host-address)), for example C(192.0.2.0/24).'
          context:
            type: str
            description: 'SNMP context the community gives access to (C(context)), for example C(nt) (device default), C(shub), C(ihub) or C(xvps1).'
          privilege:
            type: str
            description: 'Access privilege of the community (C(privilege)): C(read-only), C(read-write) (device default) or C(write-only).'
          read_view:
            type: str
            description: 'SNMP view used for read access (C(read-view)); device default C(everything).'
          write_view:
            type: str
            description: 'SNMP view used for write access (C(write-view)); device default C(everything).'
          notify_view:
            type: str
            description: 'SNMP view filtering the notifications (C(notify-view)); device default C(everything).'
      snmp_views:
        type: list
        elements: dict
        description:
          - SNMP views, identified by I(name) and I(subtree) (one view can hold several subtrees).
          - Removal uses C(configure system security snmp no view <name> subtree <oid>) (standard ISAM form, not verified on a device).
        suboptions:
          name:
            type: str
            required: true
            description: 'View name.'
          subtree:
            type: str
            description: 'OID subtree of the view entry (name or numeric, for example C(vacmAccessTable.*.7)).'
          type:
            type: str
            description: 'Whether variables matching the subtree are included in or excluded from the view (C(type)): C(include) or C(exclude).'
      snmp_managers:
        type: list
        elements: dict
        description:
          - 'SNMP element managers receiving notifications (C(snmp manager <name>)).'
          - 'I(destination) and I(notify_profile) are mandatory at creation; removal uses C(snmp no manager <name>).'
        suboptions:
          name:
            type: str
            required: true
            description: 'Element manager name.'
          destination:
            type: str
            description: 'Address of the element manager (C(destination)), C(<ipv4>:<port>) or C(ipv6:<ipv6>/<port>); only settable at creation.'
          notify_profile:
            type: str
            description: 'Notification profile used for this manager (C(notify-profile)), see I(snmp_notify_profiles).'
          nt:
            type: bool
            description: 'Store notifications for this manager on the NT (C(nt)).'
          shub:
            type: bool
            description: 'Store notifications for this manager on the SHUB (C(shub)).'
          ihub:
            type: bool
            description: 'Store notifications for this manager on the IHUB (C(ihub)).'
          epon:
            type: bool
            description: 'Store notifications for this manager on the EPON context (C(epon)).'
          vvpsa:
            type: bool
            description: 'Store notifications for this manager on the VVPSA context (C(vvpsa)).'
          xvps1:
            type: bool
            description: 'Store notifications for this manager on the xVPS1 context (C(xvps1)).'
          xvps2:
            type: bool
            description: 'Store notifications for this manager on the xVPS2 context (C(xvps2)).'
          xvps3:
            type: bool
            description: 'Store notifications for this manager on the xVPS3 context (C(xvps3)).'
          xvps4:
            type: bool
            description: 'Store notifications for this manager on the xVPS4 context (C(xvps4)).'
          xvps5:
            type: bool
            description: 'Store notifications for this manager on the xVPS5 context (C(xvps5)).'
          xvps6:
            type: bool
            description: 'Store notifications for this manager on the xVPS6 context (C(xvps6)).'
          xvps7:
            type: bool
            description: 'Store notifications for this manager on the xVPS7 context (C(xvps7)).'
          xvps8:
            type: bool
            description: 'Store notifications for this manager on the xVPS8 context (C(xvps8)).'
      snmp_notify_profiles:
        type: list
        elements: dict
        description:
          - 'SNMP notification profiles (C(snmp notify-profile <name>)).'
          - 'Removal uses C(snmp no notify-profile <name>).'
        suboptions:
          name:
            type: str
            required: true
            description: 'Notification profile name.'
          snmp_version:
            type: str
            description:
              - 'SNMP version of the profile (C(snmp-version)): C(v1:<community>), C(v2:<community>) or C(v3:<security name>:<none|authentication|privacy-and-auth>); only settable at creation.'
              - 'An embedded community string is treated as a secret and redacted in output.'
      radius_auth_servers:
        type: list
        elements: dict
        description:
          - 'RADIUS authentication servers (C(radius auth-server <name> router-instance <router>)).'
          - 'I(ip_address) and I(secret) are mandatory at creation. A server still used by a RADIUS policy cannot be deleted (device rule).'
        suboptions:
          name:
            type: str
            required: true
            description: 'Name of the RADIUS authentication server.'
          router_instance:
            type: str
            description: 'Router instance the server belongs to (C(router-instance)), for example C(base).'
          ip_address:
            type: str
            description: 'IP address of the RADIUS authentication server (C(ip-address)).'
          secret:
            type: str
            description: 'Shared secret between the RADIUS server and the ISAM (C(secret)); a masked value keeps the device value. Not logged.'
          port:
            type: int
            description: 'UDP port the authentication requests are sent to (C(port)); device default C(1812).'
          timeout_limit:
            type: int
            description: 'Seconds between retransmissions to the server (C(timeout-limit)); device default C(3).'
          dead_interval:
            type: int
            description: 'Seconds before the operational state changes from down to unknown (C(dead-interval)); device default C(600).'
          retry_limit:
            type: int
            description: 'Number of attempts before the server is given up (C(retry-limit)); device default C(3).'
          admin_down:
            type: bool
            description: 'Administratively disable the server (C(admin-down) / C(no admin-down)).'
      radius_policies:
        type: list
        elements: dict
        description:
          - Radius policies (C(radius policy <name>)).
          - The authentication/accounting servers of a policy are the C(radius policy <name> servers <index>) sub-entries, see I(servers).
          - A policy is removed with C(configure system security radius no policy <name>).
        suboptions:
          name:
            type: str
            required: true
            description: 'Name of the RADIUS policy.'
          nas_id:
            type: str
            description: 'NAS-Identifier sent in messages towards the RADIUS servers (C(nas-id)); mandatory at creation.'
          nas_ip_address:
            type: str
            description: 'NAS-IP-Address (IPv4) sent in messages towards the RADIUS servers (C(nas-ip-address)); mandatory at creation.'
          keep_domain_name:
            type: bool
            description: 'Do not strip the domain name from the user name sent to the RADIUS server (C(keep-domain-name)).'
          disable_accnt_msg:
            type: bool
            description: 'Disable RADIUS accounting messages for this policy (C(disable-accnt-msg)).'
          disable_eap:
            type: bool
            description: 'Disable EAP for this policy (C(disable-eap)).'
          acc_interval:
            type: int
            description: 'Interim accounting interval in seconds (C(acc-interval)); device default C(0).'
          auth_server:
            type: str
            description:
              - Legacy flat form of C(servers[index=1].auth_server); the device keeps this per C(servers <index>) entry.
              - When set, it is applied to the I(servers) entry with I(index) C(1) (an explicit value there wins). Facts never return it.
          auth_router_inst:
            type: str
            description: Legacy flat form of C(servers[index=1].auth_router_inst), see I(auth_server).
          acc_server:
            type: str
            description: Legacy flat form of C(servers[index=1].acc_server), see I(auth_server).
          acc_router_inst:
            type: str
            description: Legacy flat form of C(servers[index=1].acc_router_inst), see I(auth_server).
          priority:
            type: int
            description: Legacy flat form of C(servers[index=1].priority), see I(auth_server).
          servers:
            type: list
            elements: dict
            description:
              - Servers of the policy (C(radius policy <name> servers <index> auth-server ... priority ...)).
              - With I(state=merged) only the given entries are added or changed; with I(state=replaced) or I(state=overridden)
                entries missing from the list are removed and attributes not given are reset with C(no <attr>).
              - Removal uses C(configure system security radius policy <name> no servers <index>) (derived from the CLI
                syntax, not verified on a device).
            suboptions:
              index:
                type: int
                required: true
                description: Server entry index (C(servers <index>)).
              auth_server:
                type: str
                description: Authentication server, e.g. C(name:RADAuthServ1) (C(auth-server)).
              auth_router_inst:
                type: str
                description: Router instance of the authentication server, e.g. C(base) (C(auth-router-inst)).
              acc_server:
                type: str
                description: Accounting server (C(acc-server)).
              acc_router_inst:
                type: str
                description: Router instance of the accounting server (C(acc-router-inst)).
              priority:
                type: int
                description: Priority of the server entry (C(priority)).
      radius_auth_super_user:
        type: dict
        description:
          - 'RADIUS client settings of the bare C(radius) node (C(configure system security radius)).'
        suboptions:
          operator_policy:
            type: str
            description: 'RADIUS policy used to authenticate operators (C(operator-policy)), C(name:<policy>) or C(none) (device default).'
          aut_s_unreach_act:
            type: str
            description: 'Action for 802.1X users when the authentication server is unreachable (C(aut-s-unreach-act)): C(reject-all) (device default) or C(accept-all).'
      radius_dyn_auth_clients:
        type: list
        elements: dict
        description:
          - 'RADIUS dynamic authorization clients (C(radius dyn-auth-client <name> router-instance <router>)).'
          - 'I(ip_address) and I(secret) are mandatory at creation.'
        suboptions:
          name:
            type: str
            required: true
            description: 'Name of the RADIUS dynamic authorization client.'
          ip_address:
            type: str
            description: 'IP address of the dynamic authorization client (C(ip-address)).'
          secret:
            type: str
            description: 'Shared secret between the client and the ISAM (C(secret)); a masked value keeps the device value. Not logged.'
          router_instance:
            type: str
            description: 'Router instance the client belongs to (C(router-instance)), for example C(base).'
          admin_down:
            type: bool
            description: Administratively disable the dynamic authorization client (C(admin-down) / C(no admin-down)).
      snmp_notify_views:
        type: list
        elements: dict
        description:
          - SNMP notify views (C(snmp notify-view <name> subtree <oid>)).
          - An entry is identified by I(name) and I(subtree); one view name can hold several subtrees.
          - Removal uses C(configure system security snmp no notify-view <name> subtree <oid>) (standard ISAM form, not verified on a device).
        suboptions:
          name:
            type: str
            required: true
            description: Notify view name.
          subtree:
            type: str
            description: OID subtree (name or numeric), or C(*) for everything.
          type:
            type: str
            description: Whether the subtree is included or excluded (C(include), C(exclude)).
      general:
        type: dict
        description:
          - Attributes of the bare C(configure system security) node (banners, operator policy priority, forwarding checks).
          - Removal resets an attribute with C(no <attr>).
        suboptions:
          oper_policy_prio:
            type: str
            description: Priority of the operator authentication policies (C(oper-policy-prio)).
          login_banner:
            type: str
            description: Banner shown before login (C(login-banner)).
          welcome_banner:
            type: str
            description:
              - Banner shown after login (C(welcome-banner)). Device escapes such as C(\\t) and C(\\n) are kept literally.
              - Note that M(nokia.isam.isam_system) also reads this banner as C(security.welcome_banner).
          login_setting:
            type: str
            description: Login setting (C(login-setting)).
          cli_session:
            type: str
            description: CLI session setting (C(cli-session)).
          unauth_fwd:
            type: bool
            description: Forward traffic of unauthenticated users (C(unauth-fwd)).
          src_mac_check:
            type: bool
            description: Source MAC address check (C(src-mac-check)).
      default_profile:
        type: dict
        description:
          - The default operator profile (C(default-profile)), used for operators authenticated without a local profile.
          - Removal resets an attribute or permission with C(no <attr>).
        suboptions:
          description:
            type: str
            description: 'Free-text description of the default profile (C(description)).'
          slot_numbering:
            type: str
            description: Slot numbering scheme, for example C(type-based).
          prompt:
            type: str
            description: CLI prompt.
          terminal_timeout:
            type: str
            description: Terminal inactivity timeout.
          permissions:
            type: dict
            description:
              - Permission per command area, value C(read), C(write) or C(none) (for example C(aaa), C(liadmin), C(ai)).
              - Unlike I(profiles), the device prints C(no <area>) for an unset permission, which is not returned; an explicit C(none) is.
      password:
        type: dict
        description:
          - Operator password policy (C(configure system security password)).
          - Removal resets an attribute with C(no <attr>) (not verified for the numeric attributes).
        suboptions:
          min_length:
            type: int
            description: Minimum password length (C(min-length)).
          min_num_numeric_char:
            type: int
            description: Minimum number of numeric characters (C(min-num-numeric-char)).
          min_num_special_char:
            type: int
            description: Minimum number of special characters (C(min-num-special-char)).
          mixed_case:
            type: str
            choices: [mandatory, not-mandatory]
            description: Require upper and lower case characters (C(mixed-case)).
      ssh:
        type: dict
        description: SSH server, access protocols and SFTP users (C(configure system security ssh)).
        suboptions:
          server_profile:
            type: dict
            description:
              - SSH server profile (C(ssh server-profile)). Removal resets an attribute with C(no <attr>).
            suboptions:
              server_retries:
                type: int
                description: Allowed authentication retries (C(server-retries)).
              idle_timeout:
                type: int
                description: Idle timeout of an SSH session (C(idle-timeout)).
              server_host_key:
                type: str
                description: Host key type of the SSH server (C(server-host-key)), for example C(rsa).
              dis_hmac_sha_1:
                type: bool
                description: Disable the SSH algorithm C(hmac-sha-1) (C(dis-hmac-sha-1)).
              dis_hmac_sha_1_96:
                type: bool
                description: Disable the SSH algorithm C(hmac-sha-1-96) (C(dis-hmac-sha-1-96)).
              dis_hmac_sha2_256:
                type: bool
                description: Disable the SSH algorithm C(hmac-sha2-256) (C(dis-hmac-sha2-256)).
              dis_hmac_sha2_512:
                type: bool
                description: Disable the SSH algorithm C(hmac-sha2-512) (C(dis-hmac-sha2-512)).
              dis_hmac_md5:
                type: bool
                description: Disable the SSH algorithm C(hmac-md5) (C(dis-hmac-md5)).
              dis_hmac_md5_96:
                type: bool
                description: Disable the SSH algorithm C(hmac-md5-96) (C(dis-hmac-md5-96)).
              dis_aes:
                type: bool
                description: Disable the SSH algorithm C(aes) (C(dis-aes)).
              dis_des_3:
                type: bool
                description: Disable the SSH algorithm C(des-3) (C(dis-des-3)).
              dis_blowfish:
                type: bool
                description: Disable the SSH algorithm C(blowfish) (C(dis-blowfish)).
              dis_des_56:
                type: bool
                description: Disable the SSH algorithm C(des-56) (C(dis-des-56)).
              dis_cast_128_cbc:
                type: bool
                description: Disable the SSH algorithm C(cast-128-cbc) (C(dis-cast-128-cbc)).
              dis_arcfour:
                type: bool
                description: Disable the SSH algorithm C(arcfour) (C(dis-arcfour)).
              dis_aes_192_cbc:
                type: bool
                description: Disable the SSH algorithm C(aes-192-cbc) (C(dis-aes-192-cbc)).
              dis_aes_256_cbc:
                type: bool
                description: Disable the SSH algorithm C(aes-256-cbc) (C(dis-aes-256-cbc)).
              dis_aes_128_ctr:
                type: bool
                description: Disable the SSH algorithm C(aes-128-ctr) (C(dis-aes-128-ctr)).
              dis_aes_192_ctr:
                type: bool
                description: Disable the SSH algorithm C(aes-192-ctr) (C(dis-aes-192-ctr)).
              dis_aes_256_ctr:
                type: bool
                description: Disable the SSH algorithm C(aes-256-ctr) (C(dis-aes-256-ctr)).
              dis_dh_grp1_sha1:
                type: bool
                description: Disable the SSH algorithm C(dh-grp1-sha1) (C(dis-dh-grp1-sha1)).
              dis_dh_grp14_sha1:
                type: bool
                description: Disable the SSH algorithm C(dh-grp14-sha1) (C(dis-dh-grp14-sha1)).
              dis_ecdh_nistp256:
                type: bool
                description: Disable the SSH algorithm C(ecdh-nistp256) (C(dis-ecdh-nistp256)).
          access:
            type: dict
            description:
              - Management access protocols (C(ssh access)). Removal resets an attribute with C(no <attr>) (not verified for C(protocol), C(cli), C(tl1)).
            suboptions:
              protocol:
                type: str
                description: File transfer protocol, for example C(ftp) or C(sftp).
              cli:
                type: str
                description: CLI access protocol, for example C(ssh), C(telnet) or C(telnet-ssh).
              tl1:
                type: str
                description: TL1 access protocol, for example C(none) or C(ssh).
              debug:
                type: str
                choices: [none, ssh, udp, udp-ssh]
                description: Debug access (C(debug)).
              debugkernel:
                type: str
                choices: [none, ssh]
                description: Kernel debug access (C(debugkernel)).
          sftp_users:
            type: list
            elements: dict
            description:
              - SFTP users (C(ssh sftp-user <name>)).
              - Removal uses C(configure system security ssh no sftp-user <name>) (standard ISAM form, not verified on a device).
            suboptions:
              name:
                type: str
                required: true
                description: User name.
              password:
                type: str
                description: Password, as printed by the device (encrypted) or a new plain value. A masked value keeps the device value.
              auth_type:
                type: str
                description: Authentication type (C(auth-type)).
              key_type:
                type: str
                description: Key type (C(key-type)).
      tacacs:
        type: dict
        description:
          - TACACS+ operator authentication settings (C(configure system security tacacs)). Removal resets an attribute with C(no <attr>).
        suboptions:
          auth_super_user:
            type: str
            description: Super user authentication (C(auth-super-user)).
          operator_policy:
            type: str
            description: Operator policy (C(operator-policy)).
      li:
        type: dict
        description: Lawful interception settings (C(configure system security li)).
        suboptions:
          separate:
            type: bool
            description: Separate lawful interception administration (C(separate)). Removal resets it with C(no separate).
      slots:
        type: list
        elements: dict
        description:
          - Per-slot security settings (C(configure system security slot <slot>)).
          - Slots are fixed on the device; an entry is never removed, its attributes are reset with C(no <attr>).
        suboptions:
          slot:
            type: str
            required: true
            description: Slot, for example C(nt-a).
          debug_usb:
            type: bool
            description: USB debug access (C(debug-usb)).
      domains:
        type: list
        elements: dict
        description:
          - Authentication domains (C(configure system security domain <name>)).
          - Removal uses C(configure system security no domain <name>) (standard ISAM form, not verified on a device).
        suboptions:
          name:
            type: str
            required: true
            description: Domain name.
          authenticator:
            type: str
            description: Authenticator, for example C(radius:<policy>) (C(authenticator)).
          vlan_id:
            type: int
            description: VLAN (C(vlan-id)).
          primary_dns:
            type: str
            description: Primary DNS server (C(primary-dns)).
          second_dns:
            type: str
            description: Secondary DNS server (C(second-dns)).
          primary_nbns:
            type: str
            description: Primary NetBIOS name server (C(primary-nbns)).
          second_nbns:
            type: str
            description: Secondary NetBIOS name server (C(second-nbns)).
          sess_timeout:
            type: int
            description: Session timeout (C(sess-timeout)).
          qos_policy:
            type: str
            description: QoS policy (C(qos-policy)).
          admin_down:
            type: bool
            description: Administratively down (C(admin-down)).
      filetransfer:
        type: dict
        description:
          - File transfer settings and servers (C(configure system security filetransfer)).
          - Removal resets the protocol settings with C(no <attr>) (not verified for C(protocol)).
        suboptions:
          protocol:
            type: str
            description: File transfer protocol, for example C(ftp), C(tftp) or C(sftp).
          tftp_rollovr:
            type: int
            description: TFTP block number roll-over (C(tftp-rollovr)).
          servers:
            type: list
            elements: dict
            description:
              - File transfer servers (C(filetransfer server <address>)).
              - Removal uses C(configure system security filetransfer no server <address>) (standard ISAM form, not verified on a device).
            suboptions:
              server:
                type: str
                required: true
                description: Server address.
              user_name:
                type: str
                description: User name (C(user-name)).
              password:
                type: str
                description: Password, as printed by the device (encrypted) or a new plain value. A masked value keeps the device value.
              auth_type:
                type: str
                description: Authentication type (C(auth-type)).
              key_type:
                type: str
                description: Key type (C(key-type)).
      peripheral_mgnt:
        type: dict
        description: Peripheral management (C(configure system security peripheral-mgnt)).
        suboptions:
          mac_filters:
            type: list
            elements: dict
            description:
              - MAC address filters of the peripheral management port (C(peripheral-mgnt mac-filter <index>)).
              - The filter indexes are fixed on the device; an entry is never removed, removal resets it with C(no filter).
            suboptions:
              index:
                type: int
                required: true
                description: Filter index (1 to 20 on the lab device).
              filter:
                type: str
                description: Allowed MAC address (C(filter)).
      pae:
        type: dict
        description: IEEE 802.1X port access entity (C(configure system security pae)).
        suboptions:
          port_access:
            type: bool
            description: Enable 802.1X port access control system-wide (C(port-access)). Removal resets it with C(no port-access).
          ports:
            type: list
            elements: dict
            description:
              - Per-port 802.1X settings, gathered from the C(pae port), C(pae authenticator) and C(pae ext-authenticator) nodes of a port.
              - Ports are fixed on the device; an entry is never removed, its attributes are reset with C(no <attr>).
            suboptions:
              port:
                type: str
                required: true
                description: Port, for example C(1/1/4/19) or C(1/1/2/1/1/1/1).
              initialize:
                type: bool
                description: Initialize the port access state machine (C(pae port <port> initialize)).
              authenticator:
                type: dict
                description: Authenticator settings (C(pae authenticator <port>)).
                suboptions:
                  controlled_port:
                    type: str
                    description: Controlled port state, for example C(auto), C(force-authorized) or C(force-unauthorized) (C(controlled-port)).
                  quiet_period:
                    type: int
                    description: Quiet period after a failed authentication, seconds (C(quiet-period)).
                  tx_period:
                    type: int
                    description: EAP request/identity retransmission period, seconds (C(tx-period)).
                  supp_timeout:
                    type: int
                    description: Supplicant timeout, seconds (C(supp-timeout)).
                  server_timeout:
                    type: int
                    description: Authentication server timeout, seconds (C(server-timeout)).
                  max_req:
                    type: int
                    description: Maximum EAP request retransmissions (C(max-req)).
                  re_auth_enabled:
                    type: bool
                    description: Periodic re-authentication (C(re-auth-enabled)).
                  re_auth_period:
                    type: int
                    description: Re-authentication period, seconds (C(re-auth-period)).
              ext_authenticator:
                type: dict
                description: Extended authenticator settings (C(pae ext-authenticator <port>)).
                suboptions:
                  authentication:
                    type: bool
                    description: Enable authentication on the port (C(authentication)).
                  init_authreq_off:
                    type: bool
                    description: Do not send the initial authentication request (C(init-authreq-off)).
                  handshake:
                    type: bool
                    description: Handshake (C(handshake)).
                  handshake_period:
                    type: int
                    description: Handshake period, seconds (C(handshake-period)).
                  mac_auth:
                    type: bool
                    description: MAC authentication (C(mac-auth)).
                  mab_auth:
                    type: bool
                    description: MAC authentication bypass (C(mab-auth)).
                  dyn_vlan_assign:
                    type: bool
                    description: Dynamic VLAN assignment (C(dyn-vlan-assign)).
  running_config:
    description:
      - 'Device configuration to parse with I(state=parsed).'
      - 'With I(state) C(merged), C(replaced), C(overridden) or C(deleted), the current configuration to render against instead of reading the device (offline preview): this CLI text, or the canonical resource JSON as returned by C(gathered) (validated against the I(config) options).'
      - 'Offline, no command is sent and nothing is read from the device; the result holds the C(commands) that would be sent and C(before) (the supplied configuration), with C(changed) false.'
    type: str
  state:
    description:
    - The state the configuration should be left in.
    - C(overridden) acts only on the list types and settings blocks named in I(config); within a named list, entries that are not listed are removed; a list type or block that is not named is left alone. A profile that a kept operator uses is never removed (the module fails instead). To empty a list type use C(deleted).
    - C(deleted) without I(config) removes every operator, profile, SNMP, RADIUS, SSH and PAE entry and resets every settings block, which can lock out device access; name the sections to delete instead.
    - With C(gathered) and I(config), only the instances named in I(config) are read from the device, selected by their C(name) in each list (C(slot) in I(slots), C(server) in I(filetransfer.servers), C(index) in I(peripheral_mgnt.mac_filters), C(port) in I(pae.ports); an SNMP view, notify view or community is read with all its subtrees or host addresses) (targeted gathering). Other fields are ignored and absent instances are not returned; an instance with only default values is read with C(flat detail) and returned with its identity only, and C(read_outcomes) reports each named instance present or confirmed absent where the device allows it (an SFTP user, read from the shared ssh node, is present or unknown). Without I(config) the whole resource is read. Settings blocks (C(radius_auth_super_user), C(general), C(default_profile), C(password), C(ssh.server_profile), C(ssh.access), C(tacacs), C(li), the C(filetransfer) and C(pae) attributes) are read whole.
    type: str
    choices: [merged, replaced, overridden, deleted, gathered, rendered, parsed]
    default: merged
"""

EXAMPLES = """

- name: Read the whole system security configuration
  nokia.isam.isam_system_security:
    state: gathered

- name: Read only one operator (targeted gathering)
  nokia.isam.isam_system_security:
    config:
      operators:
        - name: isadmin
    state: gathered

- name: Merge an SNMP view
  nokia.isam.isam_system_security:
    config:
      snmp_views:
        - name: everything
          subtree: "*"
          type: include
    state: merged
"""

RETURN = """
# BEGIN read_outcomes (synced from plugins/doc_fragments/read_outcomes.py; do not edit)
read_outcomes:
  description:
    - Sanitized per-instance read outcomes for a targeted read (I(state) is C(gathered)
      and I(config) names instances).
    - Each outcome names the config section that addressed the instance (for example
      C(config)) and the selector -- the instance identity, a composite identity
      recorded joined by C(/). Instances in different sections that share an identity
      value are different instances and are reported separately.
    - Each outcome records the command axis (C(ok), C(rejected) or C(failed)) and the
      instance-existence axis (C(present), C(confirmed_absent) or C(unknown)).
    - Only C(confirmed_absent) -- the device's explicit "instance does not exist" signal
      about that instance -- is evidence the instance is gone. C(unknown) (a header-only
      reply, an invalid-token rejection, a missing dependency, or a failed read) is never
      treated as absence; keep, do not remove, configuration for C(unknown) instances.
    - When one instance is addressed by several reads, it is reported C(confirmed_absent)
      only if every read confirmed absence; a single present read proves presence; a
      failed read is reported as C(failed); anything less is C(unknown).
    - The parse axis (C(failed) or C(unverified)) is reported at resource level under
      C(parse); C(failed) means the family parser could not process the reply,
      C(unverified) that no parser records its coverage of the reply (a read never claims
      a complete parse).
    - A named instance the device rejected (C(invalid token)) is missing from C(gathered)
      exactly like an absent one; the module also warns, naming the rejected selectors.
    - The output is sanitized to stable enums, the section, the selector, and an error
      class; raw device text is never recorded. A failed targeted read fails the module
      carrying this same sanitized result.
  version_added: 1.1.0
  returned: when I(state) is C(gathered) and the read is targeted
  type: dict
# END read_outcomes
# BEGIN resource_returns (generated by tools/sync_resource_return_docs.py; do not edit)
before:
  description:
  - The configuration before the module ran, in the format of I(config).
  - With I(running_config) (offline preview) it is the supplied configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: dict
after:
  description:
  - The configuration read back from the device after the commands were sent, in the format of I(config).
    In check mode nothing is sent, so it shows the unchanged configuration.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted), commands were generated
    and no I(running_config) was given
  type: dict
commands:
  description:
  - 'The commands sent to the device (in check mode: that would be sent).'
  - With I(running_config) (offline preview) they are rendered only, never sent.
  returned: when I(state) is C(merged), C(replaced), C(overridden) or C(deleted)
  type: list
  elements: str
rendered:
  description:
  - The commands rendered from I(config) in device-native format, without a device (offline).
  returned: when I(state) is C(rendered)
  type: list
  elements: str
gathered:
  description:
  - The configuration read from the device, in the format of I(config).
  returned: when I(state) is C(gathered)
  type: dict
parsed:
  description:
  - The I(running_config) text parsed into the format of I(config), without a device.
  returned: when I(state) is C(parsed)
  type: dict
# END resource_returns
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.argspec.system_security.system_security import (
    Isam_system_securityArgs,
)
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.config.system_security.system_security import (
    Isam_system_security,
)


def main():
    module = AnsibleModule(
        argument_spec=Isam_system_securityArgs.argument_spec,
        required_if=[
            ["state", "merged", ["config"]],
            ["state", "replaced", ["config"]],
            ["state", "overridden", ["config"]],
            ["state", "rendered", ["config"]],
            ["state", "parsed", ["running_config"]],
        ],
        supports_check_mode=True,
    )
    result = Isam_system_security(module).execute_module()
    module.exit_json(**result)


if __name__ == "__main__":
    main()
