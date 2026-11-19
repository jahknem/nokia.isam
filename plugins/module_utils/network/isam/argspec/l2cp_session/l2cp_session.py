from __future__ import absolute_import, division, print_function


class L2cpSessionArgs(object):
    argument_spec = {"config": {"type": "list", "elements": "dict", "options": {
        "name": {"type": "str", "required": True}, "bras_ip_address": {"type": "str"},
        "gsmp_version": {"type": "str"}, "gsmp_sub_version": {"type": "str"},
        "encap_type": {"type": "str", "choices": ["tcp"]},
        "topo_discovery": {"type": "str", "choices": ["disabled", "enabled"]},
        "layer2_oam": {"type": "str", "choices": ["disabled", "enabled"]},
        "alive_timer": {"type": "str"}, "port_reprt_shaper": {"type": "str"},
        "aggr_reprt_shaper": {"type": "str"}, "tcp_retry_time": {"type": "str"},
        "gsmp_retry_time": {"type": "str"}, "dslam_name": {"type": "str"},
        "partition_id": {"type": "str"}, "window_size": {"type": "str"},
        "tcp_port": {"type": "str"}, "router_instance": {"type": "str"},
        "sig_partition_id": {"type": "bool"},
    }}, "running_config": {"type": "str"},
        "state": {"type": "str", "choices": ["merged", "replaced", "overridden", "deleted", "gathered", "rendered", "parsed"], "default": "merged"}}
