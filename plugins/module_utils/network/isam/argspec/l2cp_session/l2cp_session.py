from __future__ import absolute_import, division, print_function


class L2cpSessionArgs(object):
    argument_spec = {"config": {"type": "list", "elements": "dict", "options": {
        "name": {"type": "str", "required": True}, "bras_ip_address": {"type": "str"},
        "gsmp_version": {"type": "str", "default": "3"}, "gsmp_sub_version": {"type": "str", "default": "1"},
        "encap_type": {"type": "str", "default": "tcp", "choices": ["tcp"]},
        "topo_discovery": {"type": "str", "default": "enabled", "choices": ["disabled", "enabled"]},
        "layer2_oam": {"type": "str", "default": "enabled", "choices": ["disabled", "enabled"]},
        "alive_timer": {"type": "str", "default": "250"}, "port_reprt_shaper": {"type": "str", "default": "10"},
        "aggr_reprt_shaper": {"type": "str", "default": "10"}, "tcp_retry_time": {"type": "str", "default": "10"},
        "gsmp_retry_time": {"type": "str", "default": "10"}, "dslam_name": {"type": "str", "default": "00 : 00 : 00"},
        "partition_id": {"type": "str", "default": "0"}, "window_size": {"type": "str", "default": "10"},
        "tcp_port": {"type": "str", "default": "6068"}, "router_instance": {"type": "str", "default": "base"},
        "sig_partition_id": {"type": "bool"},
    }}, "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"}}
