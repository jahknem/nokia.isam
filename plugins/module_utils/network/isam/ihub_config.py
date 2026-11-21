"""Read-only IHUB configuration families from evidenced hierarchical CLI output.

Do not send configure/context-changing commands to obtain these configurations.
The access parser abbreviates `info configure port` to port-protection, and the
flat root source omits IHUB. Ports/LAGs therefore require explicit consent for
the hierarchical device-root source; services have a verified family source.
"""

import re
import shlex
from datetime import datetime, timezone


READS = {
    "ihub_ports": {"command": "info configure", "read_scope": "device", "section": "Port Configuration"},
    "ihub_lags": {"command": "info configure", "read_scope": "device", "section": "LAG Configuration"},
    "ihub_services": {"command": "info configure service", "read_scope": "family", "section": "Service Configuration"},
}


def _section(text, resource):
    if not isinstance(text, str) or not text.strip():
        raise ValueError("IHUB configuration response is blank; absence is not confirmed")
    lines = text.splitlines()
    nonempty = [line.strip() for line in lines if line.strip()]
    if not re.fullmatch(r"-{10,}", nonempty[-1]):
        raise ValueError("IHUB configuration has no terminal delimiter")
    marker = 'echo "%s"' % READS[resource]["section"]
    indices = [i for i, line in enumerate(lines) if line.strip() == marker]
    if len(indices) == 1:
        start = indices[0] + 1
        end = next((i for i in range(start, len(lines)) if lines[i].lstrip().startswith("echo ")), len(lines))
        return lines[start:end], True
    # The standalone service read returns a framed body, without a service
    # wrapper or echo marker. No other unlabelled body is an evidenced source.
    if (resource == "ihub_services" and not indices
            and re.fullmatch(r"-{10,}", nonempty[0])
            and not any(line.lstrip().startswith(("echo ", "configure")) for line in lines)):
        return lines, False
    raise ValueError("IHUB configuration has no unique expected family section")


def _nodes(lines):
    """Parse native indentation + matching exit delimiters, not guessed CLI paths.

Unknown commands remain native syntax nodes and are reported by the projection,
not promoted to modeled fields. A truncated or unbalanced node is an error.
"""
    records = []
    for number, line in enumerate(lines, 1):
        if not line.strip() or line.lstrip().startswith("#") or re.fullmatch(r"-{10,}", line.strip()):
            continue
        if "\t" in line:
            raise ValueError("IHUB configuration contains tab indentation")
        try:
            tokens = shlex.split(line.strip())
        except ValueError as exc:
            raise ValueError("IHUB configuration has malformed quoting") from exc
        records.append((len(line) - len(line.lstrip()), tokens, number))

    def sequence(index, closing=None):
        result = []
        level = records[index][0] if index < len(records) else None
        while index < len(records):
            indent, tokens, number = records[index]
            if tokens == ["exit"]:
                if closing is None or indent != closing:
                    raise ValueError("IHUB configuration has an unexpected exit")
                return result, index + 1
            if (closing is not None and indent <= closing) or indent != level:
                raise ValueError("IHUB configuration has unbalanced indentation")
            block = (index + 1 < len(records) and
                     (records[index + 1][0] > indent or records[index + 1][:2] == (indent, ["exit"])))
            if block:
                # Empty blocks have their matching exit immediately after the
                # opening line; nonempty blocks recurse at the next indentation.
                if records[index + 1][:2] == (indent, ["exit"]):
                    children, index = [], index + 2
                else:
                    children, index = sequence(index + 1, indent)
            else:
                children, index = None, index + 1
            result.append({"tokens": tokens, "children": children, "line": number})
        if closing is not None:
            raise ValueError("IHUB configuration has an unterminated node")
        return result, index

    return sequence(0)[0] if records else []


def parse_ihub_config(text, resource):
    """Typed, read-only projection; unknown syntax has explicit coverage gaps.

    Gap records contain modeled paths and keywords, never unknown values (which
    could contain credentials). They are not a configuration replay format.
    """
    if resource not in READS:
        raise ValueError("Unknown IHUB resource")
    lines, labelled = _section(text, resource)
    roots = _nodes(lines)
    gaps = []

    def gap(node, path):
        gaps.append({"path": list(path), "keyword": node["tokens"][0], "line": node["line"]})

    def leaf(node, row, path, allowed=("shutdown", "description")):
        tokens = node["tokens"]
        if node["children"] is not None:
            return False
        if "shutdown" in allowed and (tokens == ["shutdown"] or tokens == ["no", "shutdown"]):
            if "shutdown" in row:
                raise ValueError("Duplicate IHUB shutdown setting")
            row["shutdown"] = tokens == ["shutdown"]
        elif "description" in allowed and len(tokens) == 2 and tokens[0] == "description":
            if "description" in row:
                raise ValueError("Duplicate IHUB description setting")
            row["description"] = tokens[1]
        else:
            return False
        return True

    def saps(nodes, path):
        values, seen = [], set()
        for node in nodes:
            t = node["tokens"]
            if len(t) not in (2, 3) or t[0] != "sap" or (len(t) == 3 and t[2] != "create") or node["children"] is None:
                gap(node, path)
                continue
            if t[1] in seen:
                raise ValueError("Duplicate IHUB SAP identity")
            seen.add(t[1])
            row = {"id": t[1]}
            for child in node["children"]:
                if not leaf(child, row, path):
                    gap(child, path + [t[1]])
            values.append(row)
        return values

    if resource == "ihub_services":
        if labelled:
            if len(roots) != 1 or roots[0]["tokens"] != ["service"] or roots[0]["children"] is None:
                raise ValueError("IHUB service section does not contain a complete service node")
            roots = roots[0]["children"]
        config = {"customers": [], "services": []}
        seen = set()
        for node in roots:
            t = node["tokens"]
            if t[0] == "customer" and len(t) in (2, 3) and (len(t) == 2 or t[2] == "create") and t[1].isdigit():
                section, row = "customers", {"id": t[1]}
            elif (t[0] in ("vpls", "ies") and len(t) in (4, 5) and t[1].isdigit()
                  and t[2] == "customer" and t[3].isdigit() and (len(t) == 4 or t[4] == "create")):
                section, row = "services", {"service_type": t[0], "id": t[1], "customer_id": t[3]}
            elif (len(t) == 8 and t[0] == "vpls" and t[1].isdigit() and t[2] == "customer" and t[3].isdigit()
                  and t[4:6] == ["v-vpls", "vlan"] and t[6].isdigit() and 1 <= int(t[6]) <= 4094 and t[7] == "create"):
                section, row = "services", {"service_type": "vpls", "id": t[1], "customer_id": t[3],
                                             "vpls_type": "v-vpls", "vlan_id": int(t[6])}
            else:
                gap(node, [])
                continue
            key = (t[0], t[1])
            if key in seen or node["children"] is None:
                raise ValueError("Duplicate or incomplete IHUB service/customer node")
            seen.add(key)
            path = [t[0], t[1]]
            for child in node["children"]:
                c = child["tokens"]
                if leaf(child, row, path, ("description",) if section == "customers" else ("shutdown", "description")):
                    continue
                if section == "services" and c == ["stp"] and child["children"] is not None:
                    row["stp"] = {}
                    for setting in child["children"]:
                        if not leaf(setting, row["stp"], path, ("shutdown",)):
                            gap(setting, path + ["stp"])
                elif section == "services" and c[0] == "sap":
                    row.setdefault("saps", []).extend(saps([child], path))
                elif (section == "services" and c[0] == "interface" and len(c) in (2, 3)
                      and (len(c) == 2 or c[2] == "create") and child["children"] is not None):
                    interface = {"name": c[1]}
                    for setting in child["children"]:
                        st = setting["tokens"]
                        if leaf(setting, interface, path):
                            continue
                        if st[0] == "address" and len(st) == 2 and setting["children"] is None:
                            interface["address"] = st[1]
                        elif st[0] == "sap":
                            interface.setdefault("saps", []).extend(saps([setting], path + ["interface", c[1]]))
                        else:
                            gap(setting, path + ["interface", c[1]])
                    row.setdefault("interfaces", []).append(interface)
                else:
                    gap(child, path)
            config[section].append(row)
    else:
        config, seen = [], set()
        keyword = "port" if resource == "ihub_ports" else "lag"
        for node in roots:
            t = node["tokens"]
            if len(t) != 2 or t[0] != keyword or node["children"] is None:
                raise ValueError("IHUB family section contains an unexpected or incomplete node")
            if t[1] in seen or (keyword == "lag" and not t[1].isdigit()):
                raise ValueError("Duplicate or invalid IHUB identity")
            seen.add(t[1])
            row, path = {"id": t[1]}, [keyword, t[1]]
            for child in node["children"]:
                c = child["tokens"]
                if leaf(child, row, path):
                    continue
                if keyword == "lag" and len(c) == 2 and c[0] == "port" and child["children"] is None:
                    row.setdefault("ports", []).append(c[1])
                elif (keyword == "lag" and len(c) == 4 and c[0] == "lacp" and c[1] in ("active", "passive")
                      and c[2] == "administrative-key" and c[3].isdigit() and child["children"] is None):
                    row["lacp"] = {"mode": c[1], "administrative_key": int(c[3])}
                elif keyword == "port" and c == ["ethernet"] and child["children"] is not None:
                    ethernet = row.setdefault("ethernet", {})
                    for setting in child["children"]:
                        st = setting["tokens"]
                        if len(st) == 2 and st[0] == "speed" and st[1].isdigit() and setting["children"] is None:
                            ethernet["speed"] = int(st[1])
                        elif st == ["lldp"] and setting["children"] is not None:
                            # LLDP destination is itself a CLI node, not a leaf.
                            for dest in setting["children"]:
                                dt = dest["tokens"]
                                if len(dt) != 2 or dt[0] != "dest-mac" or dest["children"] is None:
                                    gap(dest, path + ["ethernet", "lldp"])
                                    continue
                                lldp = {"destination": dt[1]}
                                for option in dest["children"]:
                                    ot = option["tokens"]
                                    if len(ot) == 2 and ot[0] == "admin-status" and option["children"] is None:
                                        lldp["admin_status"] = ot[1]
                                    elif len(ot) >= 2 and ot[0] == "tx-tlvs" and option["children"] is None:
                                        lldp["tx_tlvs"] = ot[1:]
                                    else:
                                        gap(option, path + ["ethernet", "lldp", dt[1]])
                                ethernet.setdefault("lldp", []).append(lldp)
                        else:
                            gap(setting, path + ["ethernet"])
                else:
                    gap(child, path)
            config.append(row)

    def unique(values, field):
        ids = [value[field] for value in values]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate IHUB child identity")

    if resource == "ihub_services":
        for service in config["services"]:
            unique(service.get("saps", []), "id")
            unique(service.get("interfaces", []), "name")
            for interface in service.get("interfaces", []):
                unique(interface.get("saps", []), "id")
    elif resource == "ihub_lags":
        for lag in config:
            if len(set(lag.get("ports", []))) != len(lag.get("ports", [])):
                raise ValueError("Duplicate IHUB LAG member")
    return {"config": config, "coverage": {"complete": not gaps, "unparsed": gaps,
                                           "meaning": "observed_syntax_projection_not_device_completeness"}}


def run_module(resource, argument_spec):
    """Shared implementation of the three read-only resource module entry points."""
    from ansible.module_utils.basic import AnsibleModule
    from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import get_resource_connection

    module = AnsibleModule(argument_spec=argument_spec, required_if=[["state", "parsed", ["running_config"]]],
                           mutually_exclusive=[["config", "running_config"]],
                           supports_check_mode=True)
    source: dict = dict(READS[resource])
    if module.params["state"] == "parsed":
        text = module.params["running_config"]
        source = {"command": None, "read_scope": "offline"}
    else:
        if module.params.get("running_config") is not None:
            module.fail_json(msg="running_config is only valid with state=parsed", changed=False)
        if (source["read_scope"] == "device" or module.params.get("config") is not None) and not module.params["allow_broad_read"]:
            module.fail_json(msg="This request requires a whole-source read (%s); set allow_broad_read=true" % source["read_scope"], changed=False)
        if module.check_mode:
            module.exit_json(changed=False, skipped=True, source=source, msg="check_mode_does_not_read_ihub_configuration")
        try:
            text = get_resource_connection(module).get(source["command"])
            source["collected_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception as exc:
            # Transport exceptions may contain echoed configuration. Do not
            # copy a partial sensitive source into the module's error message.
            module.fail_json(msg="IHUB configuration read failed (%s)" % type(exc).__name__, changed=False)
    try:
        parsed = parse_ihub_config(text, resource)
    except ValueError as exc:
        module.fail_json(msg=str(exc), changed=False)
    selection = module.params.get("config")
    if selection is not None:
        def select(rows, wanted, fields):
            ids = {tuple(row[field] for field in fields) for row in wanted}
            return [row for row in rows if tuple(row[field] for field in fields) in ids]

        if resource == "ihub_services":
            parsed["config"] = {section: select(parsed["config"][section], selection.get(section) or [],
                                                ("id", "service_type") if section == "services" else ("id",))
                                for section in ("customers", "services")}
        else:
            parsed["config"] = select(parsed["config"], selection, ("id",))
    key = "parsed" if module.params["state"] == "parsed" else "gathered"
    module.exit_json(changed=False, source=source, coverage=parsed["coverage"], **{key: parsed["config"]},
                     ansible_facts={"ansible_network_resources": {resource: parsed["config"]}})
