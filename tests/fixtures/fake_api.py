# -*- coding: utf-8; -*-

def get_fake_inspect():
    status_code = 200
    response = {
        "AppArmorProfile": "",
        "Args": [
            "/elasticsearch/bin/elasticsearch"
        ],
        "Config": {
            "AttachStderr": false,
            "AttachStdin": false,
            "AttachStdout": false,
            "Cmd": [
                "/elasticsearch/bin/elasticsearch"
            ],
            "CpuShares": 0,
            "Cpuset": "",
            "Domainname": "",
            "Entrypoint": [
                "/bin/bash"
            ],
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
                "REFRESHED_AT=2015-05-29",
                "ES_PKG_NAME=elasticsearch-1.5.0"
            ],
            "ExposedPorts": {
                "9200/tcp": {},
                "9300/tcp": {}
            },
            "Hostname": "0c34a206f19d",
            "Image": "fb5b1c70d3ecb7618941ffa9209a185fe0c649ef4be45efd2431e4a90070f1d3",
            "Labels": {},
            "MacAddress": "",
            "Memory": 0,
            "MemorySwap": 0,
            "NetworkDisabled": false,
            "OnBuild": "null",
            "OpenStdin": false,
            "PortSpecs": "null",
            "StdinOnce": false,
            "Tty": false,
            "User": "",
            "Volumes": "null",
            "WorkingDir": "/data"
        },
        "Created": "2015-06-05T02:02:58.85825348Z",
        "Driver": "aufs",
        "ExecDriver": "native-0.2",
        "ExecIDs": "null",
        "HostConfig": {
            "Binds": [
                "/tmp:/tmp:rw"
            ],
            "CapAdd": "null",
            "CapDrop": "null",
            "CgroupParent": "",
            "ContainerIDFile": "",
            "CpuShares": 0,
            "CpusetCpus": "",
            "Devices": "null",
            "Dns": "null",
            "DnsSearch": "null",
            "ExtraHosts": "null",
            "IpcMode": "",
            "Links": "null",
            "LogConfig": {
                "Config": {},
                "Type": "json-file"
            },
            "LxcConf": "null",
            "Memory": 0,
            "MemorySwap": 0,
            "NetworkMode": "bridge",
            "PidMode": "",
            "PortBindings": {
                "9200/tcp": [
                    {
                        "HostIp": "",
                        "HostPort": "9200"
                    }
                ]
            },
            "Privileged": false,
            "PublishAllPorts": false,
            "ReadonlyRootfs": false,
            "RestartPolicy": {
                "MaximumRetryCount": 0,
                "Name": "always"
            },
            "SecurityOpt": "null",
            "Ulimits": "null",
            "VolumesFrom": []
        },
        "HostnamePath": "/mnt/sda1/var/lib/docker/containers/0c34a206f19dfe22b2957855db285d6a30259cab5f54e444554dd560f82d5dfc/hostname",
        "HostsPath": "/mnt/sda1/var/lib/docker/containers/0c34a206f19dfe22b2957855db285d6a30259cab5f54e444554dd560f82d5dfc/hosts",
        "Id": "0c34a206f19dfe22b2957855db285d6a30259cab5f54e444554dd560f82d5dfc",
        "Image": "fb5b1c70d3ecb7618941ffa9209a185fe0c649ef4be45efd2431e4a90070f1d3",
        "LogPath": "/mnt/sda1/var/lib/docker/containers/0c34a206f19dfe22b2957855db285d6a30259cab5f54e444554dd560f82d5dfc/0c34a206f19dfe22b2957855db285d6a30259cab5f54e444554dd560f82d5dfc-json.log",
        "MountLabel": "",
        "Name": "/tune_platform-elasticsearch-15",
        "NetworkSettings": {
            "Bridge": "docker0",
            "Gateway": "172.17.42.1",
            "GlobalIPv6Address": "",
            "GlobalIPv6PrefixLen": 0,
            "IPAddress": "172.17.0.77",
            "IPPrefixLen": 16,
            "IPv6Gateway": "",
            "LinkLocalIPv6Address": "fe80::42:acff:fe11:4d",
            "LinkLocalIPv6PrefixLen": 64,
            "MacAddress": "02:42:ac:11:00:4d",
            "PortMapping": "null",
            "Ports": {
                "9200/tcp": [
                    {
                        "HostIp": "0.0.0.0",
                        "HostPort": "9200"
                    }
                ],
                "9300/tcp": "null"
            }
        },
        "Path": "/bin/bash",
        "ProcessLabel": "",
        "ResolvConfPath": "/mnt/sda1/var/lib/docker/containers/0c34a206f19dfe22b2957855db285d6a30259cab5f54e444554dd560f82d5dfc/resolv.conf",
        "RestartCount": 0,
        "State": {
            "Dead": false,
            "Error": "",
            "ExitCode": 0,
            "FinishedAt": "0001-01-01T00:00:00Z",
            "OOMKilled": false,
            "Paused": false,
            "Pid": 5034,
            "Restarting": false,
            "Running": true,
            "StartedAt": "2015-06-05T02:03:00.57050272Z"
        },
        "Volumes": {
            "/tmp": "/tmp"
        },
        "VolumesRW": {
            "/tmp": true
        }
    }

    return status_code, response

