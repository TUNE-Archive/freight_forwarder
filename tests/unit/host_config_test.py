# -*- coding: utf-8; -*-
from __future__ import absolute_import, unicode_literals

from tests import unittest

from freight_forwarder.container.host_config import HostConfig


class HostConfigTest(unittest.TestCase):

    def setup(self):
        pass

    def test_binds(self):
        self.assertEqual(HostConfig().binds, ['/dev/log:/dev/log:rw'])

    def test_cap_add(self):
        self.assertEqual(HostConfig().cap_add, None)

    def test_cap_add_failure(self):
        with self.assertRaises(ValueError):
            hst_cnfg = HostConfig(properties={'cap_add': [], 'cap_drop': []})
            hst_cnfg.cap_drop = ['ALL']
            hst_cnfg.cap_add = ['ALL']

    def test_cap_drop(self):
        self.assertEqual(HostConfig().cap_drop, None)

    def test_cap_drop_failure(self):
        with self.assertRaises(ValueError):
            hst_cnfg = HostConfig(properties={'cap_add': [], 'cap_drop': []})
            hst_cnfg.cap_add = ['ALL']
            hst_cnfg.cap_drop = ['ALL']

    def test_cgroup_parent(self):
        self.assertEqual(HostConfig().cgroup_parent, '')

    def test_cgroup_parent_failure(self):
        with self.assertRaises(TypeError):
            HostConfig().cgroup_parent = False

    def test_cpu_shares(self):
        self.assertEqual(HostConfig().cpu_shares, 0)

    def test_cpu_shares_failure(self):
        with self.assertRaises(TypeError):
            HostConfig().cpu_shares = ''

    def test_devices(self):
        self.assertEqual(HostConfig().devices, None)
        hst_cnfg = HostConfig()
        hst_cnfg.devices = ['/tmp:/tmp']
        self.assertEqual(hst_cnfg._devices, ['/tmp:/tmp:rwm'])
        hst_cnfg.devices = ['/tmp']
        self.assertEqual(hst_cnfg._devices, ['/tmp:/tmp:rwm'])

    def test_devices_failure(self):
        with self.assertRaises(TypeError):
            HostConfig().devices = 1
        with self.assertRaises(TypeError):
            HostConfig().devices = [False]
        with self.assertRaises(ValueError):
            HostConfig().devices = ['/:/:+']
        with self.assertRaises(ValueError):
            HostConfig().devices = ['::::']

    def test_dns(self):
        self.assertEqual(HostConfig().dns, None)

    def test_dns_search(self):
        self.assertEqual(HostConfig().dns_search, None)

    def test_extra_hosts(self):
        self.assertEqual(HostConfig().extra_hosts, [])
        self.assertEqual(
            HostConfig(properties={'extra_hosts': dict(foobar='127.0.0.1')}).extra_hosts,
            ['foobar:127.0.0.1']
        )

    def test_extra_hosts_failure(self):
        with self.assertRaises(ValueError):
            HostConfig(properties={'extra_hosts': dict(foo_bar='127.0.0.1')})
        with self.assertRaises(ValueError):
            HostConfig(properties={'extra_hosts': dict(foobar='a.b.c.d')})

    def test_log_config_with_no_value_defined(self):
        self.assertEqual(HostConfig().log_config, dict(config={'max-size': '100m', 'max-file': '2'}, type='json-file'))

    def test_log_config_with_string(self):
        test_log_config_string = "config={}, type=json-file"
        with self.assertRaises(TypeError):
            HostConfig().log_config(value=test_log_config_string)

    def test_log_config_with_list(self):
        test_log_config_list = ["config={}", "type=json-file"]
        with self.assertRaises(TypeError):
            HostConfig().log_config(value=test_log_config_list)

    def test_log_config_syslog(self):
        hst_cnfg = HostConfig()
        hst_cnfg.log_config = {"config": {}, "type": "syslog"}
        self.assertEqual(
            hst_cnfg.log_config,
            {'config': {'syslog-facility': None, 'syslog-tag': None}, 'type': 'syslog'}
        )

    def test_log_config_failure(self):
        with self.assertRaises(TypeError):
            HostConfig().log_config = []
        with self.assertRaises(ValueError):
            HostConfig().log_config = {"config": {}, "type": "xml"}
        with self.assertRaises(ValueError):
            HostConfig().log_config = {"config": True, "type": "json-file"}

    def test_links(self):
        self.assertEqual(HostConfig().links, [])
        self.assertEqual(HostConfig(properties={'links': None})._links, None)
        self.assertEqual(HostConfig(properties={'links': ['api']})._links, ['api'])
        self.assertEqual(HostConfig(properties={'links': ['foo:api']})._links, ['foo:api'])

    def test_links_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'links': [False]})
        with self.assertRaises(AttributeError):
            HostConfig(properties={'links': ['::']})
        with self.assertRaises(TypeError):
            HostConfig(properties={'links': False})

    def test_lxc_conf(self):
        self.assertEqual(HostConfig().lxc_conf, [])
        self.assertEqual(
            HostConfig(properties={'lxc_conf': {"lxc.utsname": "docker", "lxc.network.name": "eth0"}}).lxc_conf,
            {"lxc.utsname": "docker", "lxc.network.name": "eth0"}
        )

    def test_lxc_conf_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'lxc_conf': ''})
        with self.assertRaises(TypeError):
            HostConfig(properties={'lxc_conf': 123})
        with self.assertRaises(TypeError):
            HostConfig(properties={'lxc_conf': False})

    def test_network_mode(self):
        self.assertEqual(HostConfig().network_mode, 'bridge')
        self.assertEqual(HostConfig(properties={'network_mode': 'bridged'}).network_mode, 'bridge')
        self.assertEqual(HostConfig(properties={'network_mode': None}).network_mode, None)

    def test_network_mode_failure(self):
        with self.assertRaises(ValueError):
            HostConfig(properties={'network_mode': 'foobar'})

    def test_port_bindings(self):
        self.assertEqual(HostConfig().port_bindings, {})
        self.assertEqual(HostConfig(properties={'port_bindings': []}).port_bindings, {})
        self.assertEqual(HostConfig(properties={'ports': None}).port_bindings, None)

    def test_port_bindings_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'ports': 0}).port_bindings

    def test_privileged(self):
        self.assertEqual(HostConfig().privileged, False)
        self.assertEqual(HostConfig(properties={'privileged': True}).privileged, True)

    def test_privileged_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'privileged': 0})

    def test_publish_all_ports(self):
        self.assertEqual(HostConfig().publish_all_ports, False)

    def test_publish_all_ports_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'publish_all_ports': 0})

    def test_readonly_root_fs(self):
        self.assertEqual(HostConfig().readonly_root_fs, False)

    def test_readonly_root_fs_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'readonly_root_fs': 2})

    def test_restart_policy(self):
        self.assertEqual(HostConfig().restart_policy, dict())

    def test_ulimits(self):
        self.assertEqual(HostConfig().ulimits, [])
        self.assertEqual(HostConfig(properties={'ulimits': None}).ulimits, None)
        self.assertEqual(
            HostConfig(properties={'ulimits': [{'name': 'foo', 'hard': 2, 'soft': 1}]}).ulimits,
            [{'name': 'foo', 'hard': 2, 'soft': 1}]
        )

    def test_ulimits_failure(self):
        with self.assertRaises(TypeError):
            HostConfig(properties={'ulimits': 1})
        with self.assertRaises(TypeError):
            HostConfig(properties={'ulimits': [1]})
        with self.assertRaises(ValueError):
            HostConfig(properties={'ulimits': [{'name': 1, 'hard': 2, 'soft': 1}]})
        with self.assertRaises(ValueError):
            HostConfig(properties={'ulimits': [{'name': 'foo', 'hard': '2', 'soft': 1}]})
        with self.assertRaises(ValueError):
            HostConfig(properties={'ulimits': [{'name': 'foo', 'hard': 2, 'soft': '1'}]})

    def test_volumes_from(self):
        self.assertEqual(HostConfig().volumes_from, [])

    def test_to_dict(self):
        host_config = HostConfig().to_dict()
        host_dict = dict(
            binds=['/dev/log:/dev/log:rw'],
            cap_add=None,
            cap_drop=None,
            cgroup_parent='',
            cpu_shares=0,
            devices=None,
            dns=None,
            dns_search=None,
            extra_hosts=[],
            links=[],
            log_config={'config': {'max-size': '100m', 'max-file': '2'}, 'type': 'json-file'},
            lxc_conf=[],
            memory=0,
            memory_swap=0,
            network_mode='bridge',
            port_bindings={},
            ports={},
            privileged=False,
            publish_all_ports=False,
            readonly_root_fs=False,
            restart_policy={},
            security_opt=None,
            ulimits=[],
            volumes_from=[]
        )
        self.assertEqual(host_config, host_dict)

    def test_docker_py_dict(self):
        docker_py_dict = HostConfig().docker_py_dict()
        response_dict = dict(
            binds=['/dev/log:/dev/log:rw'],
            cap_add=None,
            cap_drop=None,
            devices=None,
            dns=None,
            dns_search=None,
            extra_hosts=[],
            links=[],
            log_config={'config': {'max-size': '100m', 'max-file': '2'}, 'type': 'json-file'},
            lxc_conf=[],
            mem_limit=0,
            memswap_limit=0,
            network_mode='bridge',
            port_bindings={},
            privileged=False,
            publish_all_ports=False,
            read_only=False,
            restart_policy={},
            security_opt=None,
            ulimits=[],
            volumes_from=[]
        )
        self.assertEqual(docker_py_dict, response_dict)

    def test_convert_binds_with_empty(self):
        self.assertEqual(HostConfig()._convert_binds(binds=[]), [])

    def test_convert_binds_with_value(self):
        test_bind_value = ['/test/directory:/test/directory']
        test_bind_result = ['/test/directory:/test/directory']
        self.assertEqual(HostConfig()._convert_binds(binds=test_bind_value),
                         test_bind_result)

    def test_convert_binds_with_bad_value(self):
        test_bind_bad_value = {'/test/directory=/test/directory'}
        with self.assertRaises(TypeError):
            HostConfig()._convert_binds(binds=test_bind_bad_value)

    def test_convert_port_bindings_with_empty(self):
        test_port_binding_empty = None
        self.assertEqual(HostConfig()._convert_port_bindings(value=test_port_binding_empty), {})

    def test_convert_port_bindings_with_good_data(self):
        test_port_binding_request = {'8080': []}
        test_port_binding_response = {'8080/tcp': []}
        self.assertEqual(HostConfig()._convert_port_bindings(value=test_port_binding_request),
                         test_port_binding_response)

    def test_convert_port_bindings_with_bad_data(self):
        test_port_binding_request = {'8080/8080'}
        with self.assertRaises(TypeError):
            HostConfig()._convert_port_bindings(binds=test_port_binding_request)

    def test_convert_port_bindings_with_formatted_response(self):
        test_port_binding_request = {'8080/tcp': [{'host_port': '8080', 'host_ip': ''}]}
        test_port_binding_response = {'8080/tcp': [{'host_port': '8080', 'host_ip': ''}]}
        self.assertEqual(HostConfig()._convert_port_bindings(value=test_port_binding_request),
                         test_port_binding_response)

    # def test_build_dict_with_string(self):
    #     test_string_value = '8080,8080'
    #     self.assertEqual(HostConfig()._build_dict(test_string_value, ','),
    #                      {"8080": "8080"})

    # def test_build_dict_with_dict(self):
    #     test_dict_value = {'8080':'8080'}
    #     with self.assertRaises(TypeError):
    #         HostConfig()._build_dict(test_dict_value, ':')

    # def test_build_dict_with_list(self):
    #     test_list_value = ['8080', '8080']
    #     with self.assertRaises(TypeError):
    #        HostConfig()._build_dict(test_list_value, ' ')
