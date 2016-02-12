# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

from tests import unittest, mock
from tests.factories.injector_factory import InjectorFactory

from freight_forwarder.container.config import Config
from freight_forwarder.container_ship import ContainerShip
from freight_forwarder.container_ship import Injector
from freight_forwarder.commercial_invoice.service import Service


class ContainerShipTest(unittest.TestCase):

    def setUp(self):
        self.patch_host_config = mock.patch('freight_forwarder.container.host_config')
        self.patch_logger = mock.patch('freight_forwarder.container_ship.logger')
        self.patch_urlparse = mock.patch('freight_forwarder.container_ship.urlparse')
        self.patch_utils = mock.patch('freight_forwarder.container_ship.utils')
        self.patch_urllib = mock.patch('freight_forwarder.container_ship.urllib3')
        self.patch_docker_client = mock.patch('freight_forwarder.container_ship.docker.Client')
        self.patch_container = mock.patch('freight_forwarder.container_ship.Container')
        self.patch_image = mock.patch('freight_forwarder.container_ship.Image')

        self.mock_host_config = self.patch_host_config.start()
        self.mock_logger = self.patch_logger.start()
        self.mock_urlparse = self.patch_urlparse.start()
        self.mock_utils = self.patch_utils.start()
        self.mock_urllib = self.patch_urllib.start()
        self.mock_docker_client = self.patch_docker_client.start()
        self.mock_container = self.patch_container.start()
        self.mock_image = self.patch_image.start()

        self.mock_service = mock.Mock(spec=Service)

        self.injector = InjectorFactory()

    def tearDown(self):
        self.patch_host_config.stop()
        self.patch_logger.stop()
        self.patch_urlparse.stop()
        self.patch_utils.stop()
        self.patch_urllib.stop()
        self.patch_docker_client.stop()
        self.patch_container.stop()
        self.patch_image.stop()

        del self.mock_service
        del self.injector

    @mock.patch('freight_forwarder.container_ship.docker.tls.TLSConfig')
    def test_create_container_ship(self, mock_docker_tlsconfig):
        self.mock_utils.validate_path.return_value = '/'
        self.mock_urlparse.return_value.scheme = 'https'
        kwargs = {'ssl_cert_path': '/', 'services': None, 'verify': False}
        container_ship = ContainerShip(address='https://127.0.0.1:2376', **kwargs)
        self.assertIsInstance(container_ship, ContainerShip)

    def test_injector(self):
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship.injector = self.injector
        self.assertIsInstance(container_ship.injector, Injector)

    def test_injector_failure(self):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.injector = False

    def test_report(self):
        pass

    def test_healthy(self):
        pass

    def test_inspect(self):
        pass

    def test_manifest(self):
        pass

    # @mock.patch.object(ContainerShip, '_service_map')
    # def test_recall_service(self, mock_service_map):
    #     self.mock_urlparse.return_value.scheme = 'http'
    #     self.mock_service.alias = 'api'
    #     container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
    #     container_ship.url.geturl.return_value = 'foobar'
    #     container_ship.recall_service(service=self.mock_service)

    def test_recall_service_failure(self):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.recall_service(service=False)

    def test_containers(self):
        pass

    @mock.patch.object(ContainerShip, 'healthy')
    @mock.patch.object(ContainerShip, '_load_service_containers')
    def test_load_containers(self, mock_container_ship_healthy, mock_container_ship_load_service_containers):
        mock_container_ship_healthy.return_value = True
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship.load_containers(service=self.mock_service, configs={}, use_cache=False)
        self.assertIsInstance(container_ship, ContainerShip)

    @mock.patch.object(ContainerShip, 'healthy')
    def test_load_containers_failure(self, mock_container_ship_healthy):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='127.0.0.1:2376', **{})
            container_ship.load_containers(service=None, configs={}, use_cache=False)
        mock_container_ship_healthy.return_value = False
        with self.assertRaises(Exception):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.load_containers(service=self.mock_service, configs={}, use_cache=False)

    def test_cargoes(self):
        pass

    def test_clean_up_dangling_images(self):
        pass

    def test_export(self):
        self.mock_urlparse.return_value.scheme = 'http'
        self.mock_service.cargo = self.mock_image
        self.mock_service.cargo.return_value.push.return_value = None
        self.mock_service.alias = 'foo-bar'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        self.assertTrue(container_ship.export(service=self.mock_service))

    def test_export_failure(self):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.export(service=False)
        with self.assertRaises(ValueError):
            self.mock_service.cargo = None
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.export(service=self.mock_service)

    @mock.patch('freight_forwarder.container_ship.re')
    def test_find_service_containers(self, mock_re):
        self.mock_container.name = 'foo-bar'
        self.mock_container.find_by_name.return_value = {'foo-bar': self.mock_container}
        self.mock_service.alias = 'foo-bar'
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        self.assertTrue('foo-bar' in container_ship.find_service_containers(service=self.mock_service))

    @mock.patch.object(ContainerShip, 'find_service_containers')
    def test_find_previous_service_containers(self, mock_find_service_containers):
        self.mock_container.name = 'foo-bar'
        mock_find_service_containers.return_value = {'foo-bar': self.mock_container}
        self.mock_service.containers = []
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        self.assertTrue('foo-bar' in container_ship.find_previous_service_containers(service=self.mock_service))

    @mock.patch.object(ContainerShip, '_load_service_cargo')
    @mock.patch.object(ContainerShip, 'healthy')
    def test_load_cargo(self, mock_healthy, mock_load_service_cargo):
        mock_healthy.return_value = True
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship.load_cargo(service=self.mock_service)
        self.assertIsInstance(container_ship, ContainerShip)

    @mock.patch.object(ContainerShip, 'healthy')
    def test_load_cargo_failure(self, mock_healthy):
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.load_cargo(service=False)
        with self.assertRaises(Exception):
            mock_healthy.return_value = False
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.load_cargo(service=self.mock_service)

    def test_offload_project(self):
        self.mock_container.find_by_name.return_value = {'foo-bar': self.mock_container}
        self.mock_container.delete.return_value = True
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship.offload_project(team='foo', project='bar')
        self.assertIsInstance(container_ship, ContainerShip)

    def test_offload_service_cargo(self):
        pass

    def test_offload_all_service_cargo(self):
        pass

    def test_offload_expired_service_cargo(self):
        pass

    def test_offload_service_containers(self):
        pass

    def test_offload_all_service_containers(self):
        pass

    def test_offload_previous_containers(self):
        pass

    @mock.patch.object(ContainerShip, 'find_service_containers')
    def test_start_service_containers(self, mock_find_service_containers):
        mock_find_service_containers.return_value = {'foo-bar': self.mock_container}
        self.mock_container.state.return_value = {}
        self.mock_container.stop.return_value = True
        self.mock_container.start.return_value = True
        self.mock_service.containers = {'foo-bar': self.mock_container}
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        self.assertTrue(container_ship.start_service_containers(service=self.mock_service, attach=False))

    @mock.patch('freight_forwarder.container_ship.copy')
    @mock.patch.object(ContainerShip, '_update_container_host_config')
    def test_service(self, mock_update_container_host_config, mock_copy):
        self.mock_container.find_by_name.return_value = {'foo-bar': self.mock_container}
        self.mock_service.repository = 'http://127.0.0.1'
        self.mock_service.name = 'appexample'
        self.mock_service.namespace = 'appexample-api'
        self.mock_service.alias = 'appexample'
        self.mock_service.docker_file = 'foobar'
        self.mock_service.dependencies = {}
        self.mock_service.container_config = ''
        self.mock_image.find_by_name.return_value = True
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship.test_service(service=self.mock_service, configs='')
        self.mock_logger.info.assert_called_once_with('Testing Service: {0}'.format(
            self.mock_service.name
        ))
        self.assertIsInstance(container_ship, ContainerShip)

    def test_service_map(self):
        pass

    def test_service_map_failure(self):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='https://127.0.0.1:2376', **{})
            container_ship._service_map(service=False, callback=False)

    def test_offload_cargo(self):
        self.mock_service.repository = 'http://127.0.0.1'
        self.mock_service.namespace = 'appexample-api'
        self.mock_image.find_all_by_name.return_value = {
            'foo-bar01': self.mock_image,
            'foo-bar02': self.mock_image,
            'foo-bar03': self.mock_image,
        }
        self.mock_image.identifier = 'http://127.0.0.1/appexample-api-test01'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._offload_cargo(service=self.mock_service)
        self.mock_logger.info.assert_called_once_with(
            'Done offloading Cargo for {0}/{1}.'.format(
                self.mock_service.repository,
                self.mock_service.namespace
            )
        )

    def test_container_registration(self):
        self.mock_container.find_by_name.return_value = {'foo-bar': self.mock_container}
        container_alias = 'foobar'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_name = container_ship._container_registration(alias=container_alias)
        self.assertEqual(container_name, '{0}-01'.format(container_alias))

    @mock.patch.object(ContainerShip, 'find_service_containers')
    def test_load_dependency_containers(self, mock_find_service_containers):
        self.mock_service.dependencies = {'foobar-dependency': self.mock_container}
        self.mock_service.host_config.links = ['foobar-dependency']
        self.mock_container.name = 'foobar-dependency'
        self.mock_container.containers = {}
        self.mock_container.state.return_value = {'running': True}
        mock_find_service_containers.return_value = {'foobar-dependency': self.mock_container}  # part of return
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._load_dependency_containers(service=self.mock_service)
        self.assertEqual(
            self.mock_service.dependencies['foobar-dependency'].containers['foobar-dependency'],
            self.mock_container
        )

    def test_private_offload_service_containers(self):
        self.mock_service.containers = {'foobar': self.mock_container}
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._offload_service_containers(service=self.mock_service)
        self.assertEquals(self.mock_service.containers, {})

    @mock.patch('freight_forwarder.registry.registry.V2')
    @mock.patch.object(ContainerShip, '_request_auth')
    def test_load_service_cargo(self, mock_request_auth, mock_v2_registry):
        self.mock_service.repository = 'http://127.0.0.1'
        self.mock_service.namespace = 'appexample-api'
        self.mock_service.source_registry = mock_v2_registry
        self.mock_service.source_tag = 'latest'
        self.mock_service.cargo = self.mock_image
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._load_service_cargo(service=self.mock_service, inject_configs=False)
        self.mock_image.pull.assert_called_once(
            self.mock_docker_client,
            mock_v2_registry,
            '{0}/{1}:{2}'.format(self.mock_service.repository, self.mock_service.namespace, self.mock_service.source_tag)
        )

    @mock.patch.object(ContainerShip, '_update_container_host_config')
    @mock.patch.object(ContainerShip, '_container_registration')
    @mock.patch.object(ContainerShip, '_load_dependency_containers')
    @mock.patch.object(ContainerShip, '_load_service_cargo')
    @mock.patch.object(Config, 'to_dict')
    def test_load_service_containers(self,
                                     mock_config_to_dict,
                                     mock_load_service_cargo,
                                     mock_load_dependency_containers,
                                     mock_container_registration,
                                     mock_update_container_host_config):
        mock_container_registration.return_value = 'appexample-api-01'
        self.mock_service.containers = {}
        self.mock_service.cargo = self.mock_image
        self.mock_service.alias = 'appexample-api'
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._load_service_containers(service=self.mock_service, configs='', use_cache=False)
        self.assertIn('appexample-api-01', self.mock_service.containers)

    @mock.patch.object(ContainerShip, '_update_volumes_from')
    @mock.patch.object(ContainerShip, '_update_links')
    @mock.patch.object(ContainerShip, '_load_dependency_containers')
    def test_update_container_host_config(self, mock_load_dependency_containers, mock_update_links, mock_update_volumes_from):
        self.mock_service.dependencies = {'appexample-api': self.mock_container}
        self.mock_service.host_config = self.mock_host_config
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._update_container_host_config(service=self.mock_service)
        mock_load_dependency_containers.assert_called_once_with(self.mock_service)
        mock_update_links.assert_called_once_with(self.mock_service)
        mock_update_volumes_from.asseert_called_once_with(self.mock_service)

    def test_update_links(self):
        foo_service = mock.Mock(spec=Service)
        self.mock_container.id = 'bar'
        foo_service.containers = {'foo': self.mock_container}
        self.mock_host_config.links = ['foo']
        self.mock_service.name = 'api'
        self.mock_service.alias = 'appexample-api'
        self.mock_service.host_config = self.mock_host_config
        self.mock_service.dependencies = {'foo': foo_service}
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._update_links(service=self.mock_service)
        self.assertEquals(self.mock_service.host_config.links[0], 'bar:foo')

    def test_update_volumes_from(self):
        api_service = mock.Mock(spec=Service)
        self.mock_container.id = 'bar'
        api_service.containers = {'api': self.mock_container}
        self.mock_service.host_config.volumes_from = ['api:rw']
        self.mock_service.dependencies = {'api': api_service}
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship._update_volumes_from(service=self.mock_service)
        self.assertEquals(self.mock_service.host_config.volumes_from[0], 'bar')

    def test_request_auth(self):
        pass

    @mock.patch('freight_forwarder.registry.registry.V2')
    def test_request_auth_failure(self, mock_v2_registry):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(Exception):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship._request_auth(registry=False)
        with self.assertRaises(Exception):
            self.mock_docker_client.return_value.login.side_effect = Exception
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship._request_auth(registry=mock_v2_registry)

if __name__ == '__main__':
    unittest.main()
