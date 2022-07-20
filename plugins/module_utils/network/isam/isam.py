from __future__ import absolute_import, division, print_function

__metaclass__ = type
import json

from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.connection import Connection, ConnectionError

_DEVICE_CONFIGS = {}

isam_provider_spec = {
    "host": dict(),
    "port": dict(type="int"),
    "username": dict(fallback=(env_fallback, ["ANSIBLE_NET_USERNAME"])),
    "password": dict(
        fallback=(env_fallback, ["ANSIBLE_NET_PASSWORD"]),
        no_log=True,
    ),
    "ssh_keyfile": dict(
        fallback=(env_fallback, ["ANSIBLE_NET_SSH_KEYFILE"]),
        type="path",
    ),
    "timeout": dict(type="int"),
}
isam_argument_spec = {
    "provider": dict(
        type="dict",
        options=isam_provider_spec,
        removed_at_date="2022-06-01",
        removed_from_collection="isam.isam",
    ),
}

def get_provider_argspec():
    return isam_provider_spec


def get_connection(module):
    if hasattr(module, "_isam_connection"):
        return module._isam_connection

    capabilities = get_capabilities(module)
    network_api = capabilities.get("network_api")
    if network_api == "cliconf":
        module._isam_connection = Connection(module._socket_path)
    else:
        module.fail_json(msg="Invalid connection type %s" % network_api)

    return module._isam_connection

def get_capabilities(module):
    if hasattr(module, "_isam_capabilities"):
        return module._isam_capabilities
    try:
        capabilities = Connection(module._socket_path).get_capabilities()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
    module._isam_capabilities = json.loads(capabilities)
    return module._isam_capabilities

def get_defaults_flag(module):
    connection = get_connection(module)
    try:
        out = connection.get_defaults_flag()
    except ConnectionError as exc:
        module.fail_json(msg=to_text(exc, errors="surrogate_then_replace"))
    return to_text(out, errors="surrogate_then_replace").strip()