"""Targeted gathering cases: alarm, traps, system, VLAN globals, software management and voice SIP."""


def case(module, config, lines, sibling_config, sibling, marker, sibling_marker, answer=None):
    built = {"module": module, "config": config, "lines": lines, "sibling_config": sibling_config,
             "sibling": sibling, "marker": marker, "sibling_marker": sibling_marker}
    if answer is not None:
        built["answer"] = answer
    return built


def trap_answer(command, lines):
    """'info configure trap [<resource> <id>]' answered hierarchically (no flat), like the device.

    Flat case lines 'configure trap <resource> <id> <attribute...>' become
    '<resource> <id>' blocks with one indented attribute per line.
    """
    assert command.startswith("info configure trap") and not command.endswith(" flat"), command
    prefix = "configure " + command[len("info configure "):]
    hits = [line for line in lines if line == prefix or line.startswith(prefix + " ")]
    if not hits:
        return None
    blocks = {}
    for line in hits:
        tokens = line.split()
        blocks.setdefault(" ".join(tokens[2:4]), []).append(" ".join(tokens[4:]))
    out = ["configure trap", "#" + "-" * 40, 'echo "trap"', "#" + "-" * 40]
    for resource, attributes in blocks.items():
        out.append("    " + resource)
        out.extend("      " + attribute for attribute in attributes if attribute)
        out.append("    exit")
    out.append("#" + "-" * 40)
    return "\n".join(out) + "\n"


def trap_case(section, field, target, sibling, attributes):
    def make_lines(key):
        return ["configure trap %s %s %s" % (section.rstrip("s"), key, attribute) for attribute in attributes]
    return case("isam_traps", {section: [{field: target}]}, make_lines(target),
                {section: [{field: sibling}]}, make_lines(sibling), target, sibling, trap_answer)


def voice_case(section, cli, target, sibling, attributes):
    return case("isam_voice_sip", {section: [{"name": target}]},
                ["configure voice sip %s %s %s" % (cli, target, attributes)],
                {section: [{"name": sibling}]},
                ["configure voice sip %s %s %s" % (cli, sibling, attributes)], target, sibling)


CASES = {
    "alarm:entries": case("isam_alarm", {"entries": [{"index": "xdsl-ne-los"}]},
                          ["configure alarm entry xdsl-ne-los severity major", "configure alarm entry xdsl-ne-los no reporting"],
                          {"entries": [{"index": "xdsl-fe-lof"}]},
                          ["configure alarm entry xdsl-fe-lof severity minor"], "xdsl-ne-los", "xdsl-fe-lof"),
    # Composite identity: the neighbour has the same filterid but the other type.
    "alarm:filters": case("isam_alarm", {"filters": [{"fltr_type": "temporal", "filterid": 3}]},
                          ["configure alarm filter temporal filterid 3 alarmid xtca-ne-es",
                           "configure alarm filter temporal filterid 3 threshold 7",
                           "configure alarm suppression filterid 3 interface 1/1/1/1 alarmid xdsl-ne-los status 1"],
                          {"filters": [{"fltr_type": "spatial", "filterid": 3}]},
                          ["configure alarm filter spatial filterid 3 alarmid xtca-fe-uas"], "xtca-ne-es", "xtca-fe-uas"),
    "alarm:custom_profiles": case("isam_alarm", {"custom_profiles": [{"name": "cabinet-a"}]},
                                  ['configure alarm custom-profile cabinet-a mnemonic1 DOOR description1 "door open" visible1 enable'],
                                  {"custom_profiles": [{"name": "basement-b"}]},
                                  ["configure alarm custom-profile basement-b mnemonic1 WATER severity1 critical"],
                                  "cabinet-a", "basement-b"),
    "alarm:hgutr069_custs": case("isam_alarm", {"hgutr069_custs": [{"alarm_id": "cust-alm1"}]},
                                 ['configure alarm hgutr069-cust cust-alm1 description "wan down"'],
                                 {"hgutr069_custs": [{"alarm_id": "cust-alm2"}]},
                                 ['configure alarm hgutr069-cust cust-alm2 description "voip down"'], "wan down", "voip down"),
    "isam_traps:definitions": trap_case("definitions", "name", "cold-start", "link-down", ["priority high"]),
    "isam_traps:managers": trap_case("managers", "address", "10.0.0.1:162", "10.0.0.2:162",
                                     ["priority low", "cold-start-trap", "max-per-window 5"]),
    "isam_traps:v6managers": trap_case("v6managers", "ipv6address", "2001:db8::a/162", "2001:db8::b/162",
                                       ["priority medium", "link-up-trap"]),
    "system:sntp.servers": case("isam_system", {"sntp": {"servers": [{"ip_address": "198.51.100.7"}]}},
                                ["configure system sntp server-table ip-address 198.51.100.7 priority 1"],
                                {"sntp": {"servers": [{"ip_address": "203.0.113.9"}]}},
                                ["configure system sntp server-table ip-address 203.0.113.9 priority 2"],
                                "198.51.100.7", "203.0.113.9"),
    "system:syslog.destinations": case("isam_system", {"syslog": {"destinations": [{"name": "ams-collector"}]}},
                                       ["configure system syslog destination ams-collector type udp:192.0.2.10:514:unlimited"],
                                       {"syslog": {"destinations": [{"name": "ntb-archive"}]}},
                                       ["configure system syslog destination ntb-archive type file:archive.log:2000"],
                                       "ams-collector", "ntb-archive"),
    "system:syslog.routes": case("isam_system", {"syslog": {"routes": [{"destination": "ams-collector"}]}},
                                 ["configure system syslog route ams-collector msg-type all facility local4 emergency alert"],
                                 {"syslog": {"routes": [{"destination": "ntb-archive"}]}},
                                 ["configure system syslog route ntb-archive msg-type eqpt facility local0 notice"],
                                 "ams-collector", "ntb-archive"),
    "isam_vlan_global:priority_regen": case(
        "isam_vlan_global", {"priority_regen": [{"dot1p": 3}]},
        ["configure vlan priority-regen 3 profile-name ControlledLoad3 pbit0 3 pbit1 3 pbit2 3 pbit3 3 pbit4 3 pbit5 3 pbit6 3 pbit7 3"],
        {"priority_regen": [{"dot1p": 30}]},
        ["configure vlan priority-regen 30 profile-name BestEffortThirty pbit0 0 pbit1 0 pbit2 0 pbit3 0 pbit4 0 pbit5 0 pbit6 0 pbit7 0"],
        "ControlledLoad3", "BestEffortThirty"),
    "software_mngt:oswp": case("isam_software_mngt", {"oswp": [{"id": "1"}]},
                               ["configure software-mngt oswp 1 primary-file-server-id 192.0.2.11 second-file-server-id 0.0.0.0"],
                               {"oswp": [{"id": "2"}]},
                               ["configure software-mngt oswp 2 primary-file-server-id 192.0.2.22 second-file-server-id 0.0.0.0"],
                               "192.0.2.11", "192.0.2.22"),
    "voice_sip:vsp": voice_case("vsp", "vsp", "vspalpha", "vspbeta", "domain-name sip.example timer-b 32000 no admin-status"),
    "voice_sip:register": voice_case("register", "register", "vspalpha", "vspbeta", "no register-intv no init-reg-delay"),
    "voice_sip:redundancy": voice_case("redundancy", "redundancy", "vspalpha", "vspbeta", "no support-redun no dns-purge-timer"),
    "voice_sip:redundancy_cmd": voice_case("redundancy_cmd", "redundancy-cmd", "vspalpha", "vspbeta", "fail-x-type geo-fail-over"),
    "voice_sip:lineid_syn_prof": voice_case("lineid_syn_prof", "lineid-syn-prof", "profalpha", "profbeta", 'isdn-syntax ""'),
    "voice_sip:cas_nsm_prof": voice_case("cas_nsm_prof", "cas-nsm-prof", "casalpha", "casbeta",
                                         'international-prefix "00" country-code "49" outg-cpn-length 0'),
}
