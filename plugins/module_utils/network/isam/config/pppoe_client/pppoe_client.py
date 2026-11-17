# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function

from ansible.module_utils.common.text.converters import to_text
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module import ResourceModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.rm_base.resource_module_base import get_resource_connection
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.facts.facts_base import get_targeted_config
from ansible_collections.nokia.isam.plugins.module_utils.network.isam.rm_templates.pppoe_client import PppoeClientTemplate


# kind -> (targeted gathering resource, CLI node): whole read "info configure pppoe-client <node> flat",
# single instance "info configure pppoe-client <node> <name> flat".
READS = {
    "interface": ("pppoe_client_interface", "interface"),
    "profile": ("pppoe_client_ppp_profile", "ppp-profile"),
}


class PppoeClient(ResourceModule):
    def __init__(self, module, kind):
        self.template = PppoeClientTemplate(kind)
        self.kind = kind
        super(PppoeClient, self).__init__(
            empty_fact_val=[], facts_module=_LocalFacts(self.template, module, kind), module=module,
            resource="pppoe_client_%s" % kind, tmplt=_TemplateAdapter(self.template),
        )

    def execute_module(self):
        config = self._module.params.get("config") or []
        if self.state in ("parsed", "gathered"):
            # no commands: the result is the parsed / gathered facts
            return self.result
        elif self.state == "rendered":
            self.commands = self.template.render(config)
        else:
            # Instances are keyed by name (ppp-profile) or (name, client_id) (interface: the CLI
            # identity is "(ifindex) client-id <id>", several client ids can share one port).
            current = {}
            for item in self.have or []:
                item = dict((key, value) for key, value in item.items() if value is not None and key != "password")
                if self.kind == "interface" and item.get("client_id") is None:
                    continue  # not addressable: every interface command needs the client id
                current[self._key(item)] = item
            desired = [dict((key, value) for key, value in item.items() if value is not None) for item in config]
            self.commands = []
            if self.state == "deleted":
                targets = [key for key in current if not desired or any(self._matches(item, key) for item in desired)]
                self.commands = [self._delete_command(key) for key in targets]
            else:
                resolved = [(item, self._resolve(item, current)) for item in desired]
                if self.state == "overridden":
                    kept = set(key for item, key in resolved)
                    self.commands.extend(self._delete_command(key) for key in current if key not in kept)
                for item, key in resolved:
                    self.commands.extend(self._update(item, key, current.get(key)))
            if self.commands:
                self.run_commands()
        return self.result

    def _key(self, item):
        if self.kind == "interface":
            return (item["name"], item.get("client_id"))
        return item["name"]

    def _matches(self, want, key):
        """deleted: a config entry names a profile, a port (all its client ids) or one client id."""
        if self.kind != "interface":
            return want["name"] == key
        return want["name"] == key[0] and want.get("client_id") in (None, key[1])

    def _resolve(self, want, current):
        """The instance a config entry addresses (interface without client_id: the port's only one)."""
        if self.kind != "interface" or want.get("client_id") is not None:
            return self._key(want)
        candidates = [key for key in current if key[0] == want["name"]]
        if len(candidates) > 1:
            self._module.fail_json(
                msg="pppoe-client interface %s has several client ids (%s); set client_id"
                % (want["name"], ", ".join(str(key[1]) for key in candidates))
            )
        return candidates[0] if candidates else (want["name"], None)

    def _update(self, want, key, have):
        """The command bringing one instance to want, or nothing when it already matches."""
        fields = PppoeClientTemplate.PROFILE_FIELDS if self.kind == "profile" else self.OPTIONAL_INTERFACE_FIELDS
        defaults = self.DEFAULTS[self.kind]
        if self.state == "merged":
            target = dict(have or {}, **want)
        else:
            # replaced/overridden: optional attributes not in want go back to their default
            # ("no <attribute>"); the mandatory interface attributes have no removal form, keep have's.
            target = dict(want)
            if self.kind == "interface":
                for field in self.MANDATORY_INTERFACE_FIELDS:
                    if field not in target and field in (have or {}):
                        target[field] = have[field]
        if self.kind == "interface":
            target["client_id"] = key[1]
        compared = fields + (("client_id",) + self.MANDATORY_INTERFACE_FIELDS if self.kind == "interface" else ())
        if have is not None and self._normalized(target, have, compared, defaults):
            return []
        command = []
        if self.kind == "interface":
            # Creating or changing a client interface takes all mandatory parameters.
            missing = [field for field in ("client_id",) + self.MANDATORY_INTERFACE_FIELDS + ("password",) if target.get(field) is None]
            if missing:
                message = "pppoe-client interface %s: %s required to %s it" % (
                    want["name"], ", ".join(missing), "change" if have is not None else "create")
                if have is not None and missing == ["password"]:
                    # The device hides the password: it can never come from the device.
                    self._module.fail_json(msg=message)
                self._module.warn(message + "; skipped")
                return []
            command = ["configure pppoe-client interface", str(want["name"]), "client-id", str(target["client_id"])]
            for field in self.MANDATORY_INTERFACE_FIELDS + ("password",):
                command.extend((field.replace("_", "-"), str(target[field])))
        else:
            command = ["configure pppoe-client ppp-profile", str(want["name"])]
        for field in fields:
            if target.get(field) is not None:
                command.extend((field, str(target[field])))
            elif have is not None and have.get(field) is not None and have.get(field) != defaults[field]:
                command.extend(("no", field))
        return [" ".join(command)]

    @staticmethod
    def _normalized(target, have, fields, defaults):
        """target equals have, attributes at their device default ("info ... flat" omits them) included.

        The password is not compared: the device hides it.
        """
        def value(item, field):
            result = item.get(field, defaults.get(field))
            return result.lower() if field == "mac" and isinstance(result, str) else result
        return all(value(target, field) == value(have, field) for field in fields)

    def _delete_command(self, key):
        if self.kind == "interface":
            return "configure pppoe-client no interface %s client-id %s" % key
        return "configure pppoe-client no ppp-profile %s" % key

    MANDATORY_INTERFACE_FIELDS = ("profile_name", "username")
    OPTIONAL_INTERFACE_FIELDS = ("mac", "pbit")
    # Defaults from the CLI help ("configure pppoe-client ppp-profile" / "interface").
    DEFAULTS = {
        "profile": {"ipversion": "ipv4", "authproto": "auto", "mru": 1500},
        "interface": {"mac": "00:00:00:00:00:00", "pbit": 0},
    }


class _LocalFacts(object):
    def __init__(self, template, module=None, kind=None):
        self.template = template
        self._module = module
        self._kind = kind

    def get_config(self, connection):
        """The whole node, or only the instances named in config with state gathered (targeted gathering)."""
        resource, node = READS[self._kind]
        return get_targeted_config(self._module, connection, resource, "info configure pppoe-client %s flat" % node,
                                   {"config": "info configure pppoe-client %s %%s flat" % node})

    def get_facts(self, resource_facts_type=None, data=None, **kwargs):
        resource = resource_facts_type[0]
        if data is None:
            # Every state reads the device: gathered (targeted when config names instances) and the
            # write states (the whole resource, so merged/replaced/overridden/deleted compare against it).
            try:
                data = self.get_config(get_resource_connection(self._module))
            except Exception as exc:  # like netcommon's facts: a clear failure, no traceback
                self._module.fail_json(msg=to_text(exc))
        return {"ansible_network_resources": {resource: self.template.parse(data)}}, []


class _TemplateAdapter(object):
    def __init__(self, template):
        self.template = template

    def get_parser(self, name):
        return {"compval": name}
