from __future__ import absolute_import, division, print_function

import re

from ansible_collections.nokia.isam.plugins.module_utils.network.isam.common import parse_cli_fields


class L2cpTemplate(object):
    def parse(self, config):
        result = []
        pattern = re.compile(r"^(?:configure\s+)?l2cp(?:\s+(.+))?$")
        for raw in (config or "").splitlines():
            match = pattern.match(raw.strip())
            if not match:
                continue
            tokens = (match.group(1) or "").split()
            if tokens[:1] == ["partition-type"] and len(tokens) > 1:
                result.append({"name": "l2cp", "partition_type": tokens[1]})
            elif tokens[:2] == ["no", "partition-type"]:
                result.append({"name": "l2cp", "partition_type": "no-partition"})
        return result

    def render(self, config):
        commands = []
        for item in config or []:
            value = item.get("partition_type")
            if value is None or value == "no-partition":
                commands.append("configure l2cp no partition-type")
            else:
                commands.append("configure l2cp partition-type %s" % value)
        return commands


class L2cpSessionTemplate(object):
    fields = (
        "gsmp_version", "gsmp_sub_version", "encap_type", "topo_discovery",
        "layer2_oam", "alive_timer", "port_reprt_shaper", "aggr_reprt_shaper",
        "tcp_retry_time", "gsmp_retry_time", "dslam_name", "partition_id",
        "window_size", "tcp_port", "router_instance",
    )

    def parse(self, config):
        result = []
        pattern = re.compile(r"^(?:configure\s+)?l2cp\s+(no\s+)?session\s+(\S+)(.*)$")
        for raw in (config or "").splitlines():
            match = pattern.match(raw.strip())
            if not match:
                continue
            if match.group(1):
                result.append({"name": match.group(2)})
                continue
            tokens = match.group(3).split()
            item = {"name": match.group(2)}
            value_fields = {field.replace("_", "-"): "str" for field in self.fields}
            value_fields["bras-ip-address"] = "str"
            item.update(
                parse_cli_fields(
                    tokens,
                    bool_fields=("sig-partition-id",),
                    value_fields=value_fields,
                    none_for_negated_values=True,
                )
            )
            result.append(item)
        return result

    def render(self, config):
        commands = []
        cli_fields = [(field, field.replace("_", "-")) for field in self.fields]
        for item in config or []:
            name = str(item["name"])
            if item.get("bras_ip_address") is None:
                commands.append("configure l2cp no session %s" % name)
                continue
            command = ["configure", "l2cp", "session", name, "bras-ip-address", str(item["bras_ip_address"])]
            for field, cli_name in cli_fields:
                if field in item and item[field] is not None:
                    command.extend((cli_name, str(item[field])))
                elif field in item:
                    command.extend(("no", cli_name))
            if item.get("sig_partition_id") is not None:
                command.extend((["sig-partition-id"] if item["sig_partition_id"] else ["no", "sig-partition-id"]))
            commands.append(" ".join(command))
        return commands


class L2cpUserPortTemplate(object):
    def parse(self, config):
        result = []
        pattern = re.compile(r"^(?:configure\s+)?l2cp\s+(no\s+)?user-port\s+(\S+)\s+partition-id(?:\s+(\S+))?$")
        for raw in (config or "").splitlines():
            match = pattern.match(raw.strip())
            if match:
                result.append({"name": match.group(2), "partition_id": match.group(3)})
        return result

    def render(self, config):
        commands = []
        for item in config or []:
            prefix = "configure l2cp user-port %s" % item["name"]
            if item.get("partition_id") is None:
                commands.append("configure l2cp no user-port %s partition-id" % item["name"])
            else:
                commands.append(prefix + " partition-id " + str(item["partition_id"]))
        return commands
