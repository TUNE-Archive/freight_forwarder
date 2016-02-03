# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

import factory

from freight_forwarder.container.host_config import HostConfig


class HostConfigFactory(factory.Factory):
    class Meta:
        model = HostConfig

    binds             = ['/dev/log:/dev/log:rw']
    cap_add           = None
    cap_drop          = None
    devices           = None
    links             = []
    lxc_conf          = None
    readonly_root_fs  = False
    security_opt      = None
    memory            = 0
    memory_swap       = 0
    cpu_shares        = 0
    port_bindings     = {}
    publish_all_ports = False
    privileged        = False
    dns               = None
    dns_search        = None
    extra_hosts       = []
    network_mode      = 'bridge'
    volumes_from      = []
    cgroup_parent     = ''
    log_config        = {"config": {'max-size': '100m', 'max-file': '2'}, "type": "json-file"}
    ulimits           = []
    restart_policy    = {}
