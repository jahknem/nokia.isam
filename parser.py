from more_itertools import pairwise
import re


def flatten_config(config):
    parsers = [
        re.compile(
            r"""
           (?P<rest>^configure\sbridge\s(no\sageing-time)|(ageing-time\s?))
            """, re.VERBOSE),
        re.compile(
            r"""
            configure\sbridge\sport\s(?P<id>\S+)\s((vlan-id\s(?P<vlan_id>\d+)\s)|(vlan-tpid(?P<vlan_tpid>\d+)\s(?P<tpid>\d+)))?(?P<rest>.*)
            """, re.VERBOSE),
        re.compile(
            r"""
            configure\sbridge\sport\s(?P<id>\S+)\s
            ((?P<negate_pvid>no pvid))|(pvid\s(?P<pvid>\S+)s?)
            $""", re.VERBOSE),
        ]
    flattened_config = []
    vlan_id = None
    bridge_id = None
    rest = None
    vlan_tpid = None
    for line in config.splitlines():
        # if line contains bridge port id, store it in bridge_id
        line2 = line
        for regex in parsers:
            match = regex.match(line)
            if match:
                regDict = match.groupdict()
                for key in regDict.keys():
                    if key == 'ageing_time':
                        flattened_config.append(regDict[key])
                        break
                    if key == 'id':
                        bridge_id = match.group(key)
                    if key == 'vlan_id':
                        vlan_id = match.group(key)
                    if key == 'vlan_tpid':
                        vlan_tpid = match.group(key)
                    if key == 'rest':
                        rest = match.group(key)
                # for each group matched, add it to the flattened config and prepend the bridge_id. Also prepend vlan_id if it exists

                if bridge_id:
                    values = match.group("rest").split()
                    for item,item2 in divide_chunks(values,2):
                        if vlan_id:
                            flattened_config.append('configure bridge port ' + bridge_id + ' ' +'vlan-id' + ' ' + vlan_id + ' ' + ' '.join([item, item2]))
                        elif vlan_tpid:
                            flattened_config.append('configure bridge port ' + bridge_id + ' ' + 'vlan_tpid'+ vlan_tpid + ' ' + match.group('tpid')+ ' ' + ' '.join([item, item2]))
                        else:
                            flattened_config.append('configure bridge port ' + bridge_id + ' ' + ' '.join([item, item2]))
                    bridge_id = None
                    vlan_id = None
                    vlan_tpid = None
                    rest = None
                elif rest:
                    flattened_config.append(match.group('rest'))
                bridge_id = None
                vlan_id = None
                rest = None
                break
    return flattened_config

def divide_chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]
                
teststring = """configure bridge no ageing-time
configure bridge port 1/1/5/1/1/1/1 no default-priority no mac-learn-off max-unicast-mac 5 no qos-profile no prio-regen-prof no prio-regen-name no max-committed-mac no mirror-mode no mirror-vlan no outervlancapture no direction no pvid-tagging-flag no ds-pbit-mode no default-tpid
configure bridge port 1/1/5/1/1/1/1 vlan-tpid0 0 no tpid
configure bridge port 1/1/5/1/1/1/1 vlan-tpid1 1 no tpid
configure bridge port 1/1/5/1/1/1/1 vlan-id 10 tag single-tagged l2fwder-vlan 110 vlan-scope local no qos no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl no min-cvlan-id no max-cvlan-id no ds-dedicated-q no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile
configure bridge port 1/1/5/1/1/1/1 vlan-id 20 tag single-tagged l2fwder-vlan 120 vlan-scope local qos priority:5 no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl no min-cvlan-id no max-cvlan-id no ds-dedicated-q no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile
configure bridge port 1/1/5/1/1/1/1 vlan-id 30 tag single-tagged l2fwder-vlan 130 vlan-scope local qos priority:4 no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl no min-cvlan-id no max-cvlan-id no ds-dedicated-q no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile
configure bridge port 1/1/5/1/1/1/1 vlan-id 99 no tag no l2fwder-vlan no vlan-scope no qos no qos-profile no prior-best-effort no prior-background no prior-spare no prior-exc-effort no prior-ctrl-load no prior-less-100ms no prior-less-10ms no prior-nw-ctrl no in-qos-prof-name no max-up-qos-policy no max-ip-antispoof no max-unicast-mac no max-ipv6-antispf no mac-learn-ctrl no min-cvlan-id no max-cvlan-id no ds-dedicated-q no tpid no inner-pbit-remark no groupid no usacceptframetype no oltregenprofile
configure bridge port 1/1/5/1/1/1/1 pvid 99"""

for line in flatten_config(teststring):
    print(line)