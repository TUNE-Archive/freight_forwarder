# -*- coding: utf-8; -*-
from __future__ import unicode_literals


import six


from freight_forwarder.utils import capitalize_keys, is_valid_hostname, is_valid_ip

# documentation http://linux.die.net/man/7/capabilities
VALID_CAPABILITIES = (
    'ALL',
    'SETPCAP',          # Modify process capabilities
    'SYS_MODULE',       # Load and unload kernel modules.
    'SYS_RAWIO',        # Perform I/O port operations (iopl(2) and ioperm(2)).
    'SYS_PACCT',        # Use acct(2), switch process accounting on or off.
    'SYS_ADMIN',        # Perform a range of system administration operations.
    'SYS_NICE',         # Raise process nice value (nice(2), setpriority(2)) and change the nice value for arbitrary processes.
    'SYS_RESOURCE',     # Override resource Limits.
    'SYS_TIME',         # Set system clock (settimeofday(2), stime(2), adjtimex(2)); set real-time (hardware) clock.
    'SYS_TTY_CONFIG',   # Use vhangup(2); employ various privileged ioctl(2) operations on virtual terminals.
    'MKNOD'             # Create special files using mknod(2).
    'AUDIT_WRITE',      # Write records to kernel auditing log.
    'AUDIT_CONTROL',    # Enable and disable kernel auditing; change auditing filter rules; retrieve auditing status and filtering rules.
    'MAC_OVERRIDE',     # Allow MAC configuration or state changes. Implemented for the Smack LSM.
    'MAC_ADMIN',        # Override Mandatory Access Control (MAC). Implemented for the Smack Linux Security Module (LSM).
    'NET_ADMIN',        # Perform various network-related operations.
    'SYSLOG'            # Perform privileged syslog(2) operations.
    'CHOWN',            # Make arbitrary changes to file UIDs and GIDs (see chown(2)).
    'NET_RAW',          # Use RAW and PACKET sockets.
    'DAC_OVERRIDE',     # Bypass file read, write, and execute permission checks.
    'FOWNER',           # Bypass permission checks on operations that normally require the file system UID of the process to match the UID of the file.
    'DAC_READ_SEARCH',  # Bypass file read permission checks and directory read and execute permission checks.
    'FSETID'            # Don’t clear set-user-ID and set-group-ID permission bits when a file is modified.
    'KILL',             # Bypass permission checks for sending signals.
    'SETGID',           # Make arbitrary manipulations of process GIDs and supplementary GID list.
    'SETUID',           # Make arbitrary manipulations of process UIDs.
    'LINUX_IMMUTABLE'   # Set the FS_APPEND_FL and FS_IMMUTABLE_FL i-node flags.
    'NET_BIND_SERVICE'  # Bind a socket to internet domain privileged ports (port numbers less than 1024).
    'NET_BROADCAST',    # Make socket broadcasts, and listen to multicasts.
    'IPC_LOCK',         # Lock memory (mlock(2), mlockall(2), mmap(2), shmctl(2)).
    'IPC_OWNER',        # Bypass permission checks for operations on System V IPC objects.
    'SYS_CHROOT',       # Use chroot(2), change root directory.
    'SYS_PTRACE',       # Trace arbitrary processes using ptrace(2).
    'SYS_BOOT',         # Use reboot(2) and kexec_load(2), reboot and load a new kernel for later execution.
    'LEASE',            # Establish leases on arbitrary files (see fcntl(2)).
    'SETFCAP',          # Set file capabilities.
    'WAKE_ALARM',       # Trigger something that will wake up the system.
    'BLOCK_SUSPEND'     # Employ features that can block system suspend.
)

# valid container network modes
VALID_NETWORK_MODES = (
    'bridge',
    'container',
    'host',
    "default",
    '',
    None
)

# valid docker log driver types
VALID_LOG_DRIVER_TYPES = (
    'journald',
    'json-file',
    'syslog',
    'none'
)


class HostConfig(object):
    def __init__(self, properties={}):
        """
          "HostConfig": {
            "Binds": ["/tmp:/tmp"],
            "Links": ["redis3:redis"],
            "LxcConf": {"lxc.utsname":"docker"},
            "Memory": 0,
            "MemorySwap": 0,
            "CpuShares": 512,
            "CpuPeriod": 100000,
            "CpusetCpus": "0,1",
            "CpusetMems": "0,1",
            "BlkioWeight": 300,
            "OomKillDisable": false,
            "PortBindings": { "22/tcp": [{ "HostPort": "11022" }] },
            "PublishAllPorts": false,
            "Privileged": false,
            "ReadonlyRootfs": false,
            "Dns": ["8.8.8.8"],
            "DnsSearch": [""],
            "ExtraHosts": null,
            "VolumesFrom": ["parent", "other:ro"],
            "CapAdd": ["NET_ADMIN"],
            "CapDrop": ["MKNOD"],
            "RestartPolicy": { "Name": "", "MaximumRetryCount": 0 },
            "NetworkMode": "bridge",
            "Devices": [],
            "Ulimits": [{}],
            "LogConfig": { "Type": "json-file", "Config": {} },
            "SecurityOpt": [""],
            "CgroupParent": ""
          }
        """
        # TODO: consider adding external links
        self.binds             = properties.get('binds', ['/dev/log:/dev/log:rw'])
        self.cap_add           = properties.get('cap_add', None)
        self.cap_drop          = properties.get('cap_drop', None)
        self.devices           = properties.get('devices', None)
        self.links             = properties.get('links', [])
        self.lxc_conf          = properties.get('lxc_conf', [])
        self.readonly_root_fs  = properties.get('readonly_root_fs') or properties.get('readonly_rootfs', False)
        self.security_opt      = properties.get('security_opt', None)
        self.memory            = properties.get('memory', 0)
        self.memory_swap       = properties.get('memory_swap', 0)
        self.cpu_shares        = properties.get('cpu_shares', 0)
        self.port_bindings     = properties.get('port_bindings') or properties.get('ports', {})
        self.publish_all_ports = properties.get('publish_all_ports', False)
        self.privileged        = properties.get('privileged', False)
        self.dns               = properties.get('dns', None)
        self.dns_search        = properties.get('dns_search', None)
        self.extra_hosts       = properties.get('extra_hosts', [])
        self.network_mode      = properties.get('network_mode', 'bridge')
        self.volumes_from      = properties.get('volumes_from', [])
        self.cgroup_parent     = properties.get('cgroup_parent', '')
        self.log_config        = properties.get(
            'log_config',
            {"config": {'max-size': '100m', 'max-file': '2'}, "type": "json-file"}
        )
        self.ulimits           = properties.get('ulimits', [])
        self.restart_policy    = properties.get('restart_policy', {})

        # add later if required self._ipc_mode = None

    def to_dict(self):
        return dict([(name, getattr(self, name)) for name in dir(self) if not name.startswith('_') and not callable(getattr(self, name))])

    def docker_py_dict(self):
        """
        """
        return {
            'binds': self._binds,
            'port_bindings': capitalize_keys(self._port_bindings) if self._port_bindings else self._port_bindings,
            'lxc_conf': self._lxc_conf,
            'publish_all_ports': self._publish_all_ports,
            'links': [link.split(':') for link in self._links] if self._links else self._links,
            'privileged': self._privileged,
            'dns': self._dns,
            'dns_search': self._dns_search,
            'volumes_from': self._volumes_from,
            'network_mode': self._network_mode,
            'restart_policy': self._restart_policy,
            'cap_add': self._cap_add,
            'cap_drop': self._cap_drop,
            'devices': self._devices,
            'extra_hosts': self._extra_hosts,
            'read_only': self._readonly_root_fs,
            'security_opt': self._security_opt,
            'ulimits': self._ulimits,
            'log_config': self._log_config,
            'mem_limit': self._memory,
            'memswap_limit': self._memory_swap
        }

    @property
    def binds(self):
        return self._binds

    @binds.setter
    def binds(self, value):
        self._binds = self._convert_binds(value)

    @property
    def cap_add(self):
        return self._cap_add

    @cap_add.setter
    def cap_add(self, value):
        """
        """
        if value is None:
            self._cap_add = value
        else:
            self._cap_add = self._create_capabilities_list(value)

            for capability in self._cap_add:
                if hasattr(self, '_cap_drop'):
                    if capability in self._cap_drop:
                        raise ValueError(
                            "circular reference in cap_add. please remove {0} from either cap_add or cap_drop".format(capability)
                        )

    @property
    def cap_drop(self):
        return self._cap_drop

    @cap_drop.setter
    def cap_drop(self, value):
        if value is None:
            self._cap_drop = value
        else:
            self._cap_drop = self._create_capabilities_list(value)

            for capability in self._cap_drop:
                if hasattr(self, '_cap_add'):
                    if capability in self._cap_add:
                        raise ValueError(
                            "circular reference in cap_add. please remove {0} from either cap_add or cap_drop".format(capability)
                        )

    @property
    def cgroup_parent(self):
        return self._cgroup_parent

    @cgroup_parent.setter
    def cgroup_parent(self, value):
        if not isinstance(value, six.string_types):
            raise TypeError("cgroup parent must be a string. {0} was passed".format(value))

        self._cgroup_parent = value

    @property
    def cpu_shares(self):
        return self._cpu_shares

    @cpu_shares.setter
    def cpu_shares(self, value):
        if not isinstance(value, int):
            raise TypeError("cpu shares must be an int. {0} was passed".format(value))

        self._cpu_shares = value

    @property
    def devices(self):
        return self._devices

    @devices.setter
    def devices(self, value):
        """
        { "PathOnHost": "/dev/deviceName", "PathInContainer": "/dev/deviceName", "CgroupPermissions": "mrw"}
        """

        if value is None:
            self._devices = None

        elif isinstance(value, list):
            results = []
            delimiter = ':'

            for device in value:
                if not isinstance(device, six.string_types):
                    raise TypeError("each device must be a str. {0} was passed".format(device))

                occurrences = device.count(delimiter)
                permissions = 'rwm'

                if occurrences is 0:
                    path_on_host = device
                    path_in_container = device

                elif occurrences is 1:
                    path_on_host, path_in_container = device.split(delimiter)

                elif occurrences is 2:
                    path_on_host, path_in_container, permissions = device.split(delimiter)

                    if permissions not in 'rwm':
                        raise ValueError("only permissions supported for devices are any combination of  'r' 'w' 'm'.")
                else:
                    raise ValueError(
                        """When passing devices they must be in one of the
                        following formats: path_on_host, path_on_host:path_in_container,
                        or path_on_host:path_in_container:permissions"""
                    )

                results.append("{0}:{1}:{2}".format(path_on_host, path_in_container, permissions))

            self._devices = results
        else:
            raise TypeError("devices must be a list or None.")

    @property
    def dns(self):
        return self._dns

    @dns.setter
    def dns(self, value):
        self._dns = self._create_dns_list(value)

    @property
    def dns_search(self):
        return self._dns_search

    @dns_search.setter
    def dns_search(self, value):
        self._dns_search = self._create_dns_list(value)

    @property
    def log_config(self):
        return self._log_config

    @log_config.setter
    def log_config(self, value):
        """
        { "Type": "<driver_name>", "Config": {"key1": "val1"}}
        """
        if not isinstance(value, dict):
            raise TypeError("log_config must be a dict. {0} was passed".format(value))

        config      = value.get('config')
        driver_type = value.get('type')

        if driver_type not in VALID_LOG_DRIVER_TYPES:
            raise ValueError("type must be one of the support drivers {0}".format(", ".join(VALID_LOG_DRIVER_TYPES)))

        if config and not isinstance(config, dict):
            raise ValueError("log_config.config must be a dict.")

        if driver_type == 'syslog':
            config = {
                'syslog-facility': config.get('syslog_facility', config.get('syslog-facility')),
                'syslog-tag': config.get('syslog_tag', config.get('syslog-tag'))
            }

        self._log_config = {'type': driver_type, 'config': config or {}}

    @property
    def links(self):
        return self._links

    @links.setter
    def links(self, value):
        """
        """
        if value is None:
            self._links = value
        elif isinstance(value, list):
            self._links = []

            # TODO: better validation please.
            for link in value:
                if not isinstance(link, six.string_types):
                    raise TypeError("links must be a string.")

                if ':' not in link:
                    self._links.append(link)
                    continue

                if link.count(':') is 1:
                    self._links.append(link)
                else:
                    raise AttributeError(
                        "links must be in one of the following formats: dependency or container_name:alias"
                    )
        else:
            raise TypeError("links must be a list or None.")

    @property
    def lxc_conf(self):
        return self._lxc_conf

    @lxc_conf.setter
    def lxc_conf(self, value):
        self._lxc_conf = []
        if value is None:
            return

        elif isinstance(value, (list, dict)):
            self._lxc_conf = value

        else:
            raise TypeError("lxc conf must be a dict, list, or None")

    @property
    def memory(self):
        return self._memory

    @memory.setter
    def memory(self, value):
        self._memory = value

    @property
    def memory_swap(self):
        return self._memory_swap

    @memory_swap.setter
    def memory_swap(self, value):
        self._memory_swap = value

    @property
    def network_mode(self):
        return self._network_mode

    @network_mode.setter
    def network_mode(self, value):
        """
        """
        # TODO: docker returns bridged for network more in the inspect response
        if value == 'bridged':
            value = 'bridge'

        if value is None:
            pass
        elif value not in VALID_NETWORK_MODES:
            raise ValueError(
                "network mode must be one of the following values: {0}".format(VALID_NETWORK_MODES)
            )

            # TODO: validate container network mode later

        self._network_mode = value

    @property
    def port_bindings(self):
        return self._port_bindings

    @port_bindings.setter
    def port_bindings(self, value):
        """
            {
                u'8080/tcp': [
                    {
                        u'host_port': u'8080',
                        u'host_ip': u''
                    }
                ]
            }
        """
        if isinstance(value, (list, dict)):
                self._port_bindings = self._convert_port_bindings(value)
        elif value is None:
            self._port_bindings = None
        else:
            raise TypeError('port bindings must be a dict, list, or None. {0} was passed.'.format(type(value)))

    @property
    def ports(self):
        return self.port_bindings

    @ports.setter
    def ports(self, value):
        # TODO: Validation
        self.port_bindings = value

    @property
    def privileged(self):
        return self._privileged

    @privileged.setter
    def privileged(self, value):
        if not isinstance(value, bool):
            raise TypeError("privileged must be a bool: {0} was passed".format(value))

        self._privileged = value

    @property
    def publish_all_ports(self):
        return self._publish_all_ports

    @publish_all_ports.setter
    def publish_all_ports(self, value):
        if not isinstance(value, bool):
            raise TypeError("publish all ports must be a bool: {0} was passed".format(value))

        self._publish_all_ports = value

    @property
    def readonly_root_fs(self):
        return self._readonly_root_fs

    @readonly_root_fs.setter
    def readonly_root_fs(self, value):
        if not isinstance(value, bool):
            raise TypeError("readonly_root_fs is required to be a bool.")

        self._readonly_root_fs = value

    @property
    def restart_policy(self):
        return self._restart_policy

    @restart_policy.setter
    def restart_policy(self, value):
        # TODO: Validation
        self._restart_policy = value

    @property
    def ulimits(self):
        return self._ulimits

    @ulimits.setter
    def ulimits(self, value):
        """
        """
        if value is None:
            pass
        elif isinstance(value, list):
            if value:
                for ulimit in value:
                    if not isinstance(ulimit, dict):
                        raise TypeError('each ulimit must be a dict: { "name": "nofile", "soft": 1024, "hard", 2048 }}')

                    name = ulimit.get('name')
                    hard = ulimit.get('hard')
                    soft = ulimit.get('soft')

                    if not isinstance(name, six.string_types):
                        raise ValueError("ulimit.name must be a string: {0}".format(ulimit))

                    if soft and not isinstance(soft, int):
                        raise ValueError("ulimit.soft must be an integer: {0}")

                    if hard and not isinstance(hard, int):
                        raise ValueError("ulimit.hard must be an integer: {0}".format(ulimit))
        else:
            raise TypeError('ulimits most be a list or None.')

        self._ulimits = value

    @property
    def extra_hosts(self):
        return self._extra_hosts

    @extra_hosts.setter
    def extra_hosts(self, value):
        """
        :param value:
        :return None:
        """
        if value is None:
            self._extra_hosts = value
        elif isinstance(value, list):
            # TODO: better validation
            self._extra_hosts = value
        elif isinstance(value, dict):
            converted_extra_hosts = []
            for k, v in sorted(six.iteritems(value)):
                if not is_valid_hostname(k):
                    raise ValueError("each key in extra hosts is required to be a valid hostname. {0} was passed".format(k))

                if not is_valid_ip(v):
                    raise ValueError("each value in extra hosts is required to be a valid ip address. {0} was passed".format(v))

                converted_extra_hosts.append('{0}:{1}'.format(k, v))

            self._extra_hosts = converted_extra_hosts
        else:
            raise TypeError("extra hosts must be a dict, list, or None. {0} was passed".format(value))

    @property
    def security_opt(self):
        return self._security_opt

    @security_opt.setter
    def security_opt(self, value):
        if value is None:
            self._security_opt = value
        elif not isinstance(value, list):
            raise TypeError('security_opt must be a list')

        self._security_opt = value

    @property
    def volumes_from(self):
        return self._volumes_from

    @volumes_from.setter
    def volumes_from(self, value):
        """
        :param value:
        :return:
        """
        volumes_from = []

        if isinstance(value, list):
            for volume_from in value:
                if not isinstance(volume_from, six.string_types):
                    raise TypeError("each bind must be a str. {0} was passed".format(volume_from))

                volumes_from.append(self._convert_volume_from(volume_from))
        elif isinstance(value, six.string_types):
            volumes_from.append(self._convert_volume_from(value))
        elif value is None:
            pass
        else:
            raise ValueError(
                """When passing binds they must be in one of the
                following formats: container_path, host_path:container_path,
                or host_path:container_path:permissions"""
            )

        self._volumes_from = volumes_from

    ##
    # static methods
    ##
    @classmethod
    def allowed_config_attributes(cls):

        return tuple(six.text_type(name) for name in dir(cls) if not name.startswith('_') and not callable(getattr(cls, name)))

    ##
    # private methods
    ##
    def _convert_volume_from(self, volume_from):
        """
        :param volume_from:
        :return:
        """
        if ':' in volume_from:
            container, permissions = volume_from.split(':')
        else:
            container = volume_from
            permissions = 'rw'

        if permissions not in ('ro', 'rw'):
            raise ValueError("only permissions supported for volumes_from are rw and ro.")

        return "{0}:{1}".format(container, permissions)

    def _create_dns_list(self, dns):
        """
        :param dns:
        :return:
        """
        if not dns:
            return None

        dns_list = []

        if isinstance(dns, six.string_types):
            if is_valid_ip(dns):
                dns_list.append(dns)
            else:
                raise ValueError("dns is required to be a valid ip adress. {0} was passed.".format(dns))
        elif isinstance(dns, list):
            for dns_entry in dns:
                if is_valid_ip(dns_entry):
                    dns_list.append(dns_entry)
            else:
                raise ValueError("dns is required to be a valid ip adress. {0} was passed.".format(dns))

        else:
            raise ValueError("dns and dns search must be a list or string. {0} was passed.".format(dns))

        return dns_list

    def _create_capabilities_list(self, capabilities):
        """

        :param capabilities:
        :return capabilities_list:
        """
        capabilities_list = []

        if isinstance(capabilities, six.string_types):
            if capabilities.upper() in VALID_CAPABILITIES:
                capabilities_list.append(capabilities)
            else:
                raise ValueError(
                    "cap add must be one of the following VALID_CAPABILITIES: {0}".format(", ".join(VALID_CAPABILITIES))
                )

        elif isinstance(capabilities, list):
            for capability in capabilities:
                if capability.upper() in VALID_CAPABILITIES:
                    capabilities_list.append(capability)
                else:
                    raise ValueError(
                        "cap add must be one of the following VALID_CAPABILITIES: {0}".format(
                            ", ".join(VALID_CAPABILITIES)
                        )
                    )
        else:
            raise ValueError("cap add must be a string, list")

        return capabilities_list

    def _convert_binds(self, binds):
        """
        """
        results = []
        if binds is None:
            return None
        elif isinstance(binds, list):
            delimiter = ':'
            for bind in binds:
                if not isinstance(bind, six.string_types):
                    raise TypeError("each bind must be a str. {0} was passed".format(bind))

                occurrences = bind.count(delimiter)
                if occurrences is 0:
                    results.append(bind)
                elif occurrences is 1:
                    host, container = bind.split(delimiter)
                    results.append("{0}:{1}:rw".format(host, container))
                elif occurrences is 2:
                    host, container, permissions = bind.split(delimiter)

                    if permissions not in ('ro', 'rw'):
                        raise ValueError("only permissions supported for binds are rw and ro.")

                    results.append("{0}:{1}:{2}".format(host, container, permissions))
                else:
                    raise ValueError(
                        """When passing binds they must be in one of the following
                         formats: container_path, host_path:container_path, or
                         host_path:container_path:permissions"""
                    )
        else:
            raise TypeError("binds must be a list or None.")

        return binds

    def _convert_port_bindings(self, value):
        """
        "PortBindings": {
            "6379/tcp": [
                {
                    "HostIp": "",
                    "HostPort": "6379"
                }
            ]
        }
        """
        converted = {}

        if not value:
            return converted

        if isinstance(value, list):
            value = self._convert_port_bindings_from_list(value)

        if isinstance(value, dict):
            for port_protocol, host_bindings in six.iteritems(value):
                if '/' in port_protocol:
                    port, protocol = port_protocol.split('/')

                    if protocol not in ('tcp', 'udp'):
                        raise ValueError('only supported protocols are tcp and udp. {0} was passed.'.format(protocol))
                else:
                    port_protocol = "{0}/tcp".format(port_protocol)

                converted[port_protocol] = []

                if isinstance(host_bindings, list):
                    for host_binding in host_bindings:
                        if isinstance(host_binding, dict):
                            if "host_port" not in host_binding:
                                raise ValueError("host_port must be provided.")

                            if 'host_ip' not in host_binding:
                                host_binding['host_ip'] = ''

                            converted[port_protocol].append(host_binding)
                        else:
                            raise TypeError("The host binding information must be a dict.")
                else:
                    raise TypeError("The host binding information in port bindings must be in a list.")

        return converted

    def _convert_port_bindings_from_list(self, value):
        """
        """
        converted = {}
        for port_binding in value:
            if not isinstance(port_binding, six.string_types):
                raise TypeError("port bindings must be a string.")

            delimiter   = ':'
            occurrences = port_binding.count(delimiter)
            host_ip     = ''

            if occurrences is 2:
                host_ip, host_port, container_port = port_binding.split(delimiter)
            elif occurrences is 1:
                host_port, container_port = port_binding.split(delimiter)
            else:
                raise AttributeError(
                    """when passing port bindings as we list it must be in the follow format:
                    container_port:host_port or container_port:host_ip:host_port
                    protocol is optional if required use the following format:
                    container_port/protocol:host_ip:host_port"""
                )

            if host_ip in converted:
                # TODO : better error message
                # File "/Users/alexb/Development/tune/freight_forwarder/freight_forwarder/container/host_config.py",
                # line 771, in _convert_port_bindings_from_list
                # "conflict with port binding: {0}".format(host_ip)
                #  ValueError: conflict with port binding: 8000
                raise ValueError(
                    "conflict with port binding: {0}".format(host_ip)
                )

            converted[container_port] = [{"host_port": host_port, "host_ip": host_ip}]

        return converted
