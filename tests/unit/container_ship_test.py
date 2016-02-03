# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

from tests import unittest, mock
from tests.factories.injector_factory import InjectorFactory

from freight_forwarder.container_ship import ContainerShip
from freight_forwarder.container_ship import Injector
from freight_forwarder.commercial_invoice.service import Service


class ContainerShipTest(unittest.TestCase):

    def setUp(self):
        self.patch_urlparse = mock.patch('freight_forwarder.container_ship.urlparse')
        self.patch_utils = mock.patch('freight_forwarder.container_ship.utils')
        self.patch_urllib = mock.patch('freight_forwarder.container_ship.urllib3')
        self.patch_docker_client = mock.patch('freight_forwarder.container_ship.docker.Client')
        self.patch_image = mock.patch('freight_forwarder.container_ship.Image')
        self.injector = InjectorFactory()

        self.mock_urlparse = self.patch_urlparse.start()
        self.mock_utils = self.patch_utils.start()
        self.mock_urllib = self.patch_urllib.start()
        self.mock_docker_client = self.patch_docker_client.start()
        self.mock_image = self.patch_image.start()

    def tearDown(self):
        self.patch_urlparse.stop()
        self.patch_utils.stop()
        self.patch_urllib.stop()
        self.patch_docker_client.stop()
        self.patch_image.stop()
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

    def test_recall_service(self):
        pass

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
        mock_service = mock.Mock(spec=Service)
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        container_ship.load_containers(service=mock_service, configs={}, use_cache=False)
        self.assertIsInstance(container_ship, ContainerShip)

    @mock.patch.object(ContainerShip, 'healthy')
    def test_load_containers_failure(self, mock_container_ship_healthy):
        self.mock_urlparse.return_value.scheme = 'http'
        mock_service = mock.Mock(spec=Service)
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='127.0.0.1:2376', **{})
            container_ship.load_containers(service=None, configs={}, use_cache=False)
        mock_container_ship_healthy.return_value = False
        with self.assertRaises(Exception):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.load_containers(service=mock_service, configs={}, use_cache=False)

    def test_cargoes(self):
        pass

    def test_clean_up_dangling_images(self):
        pass

    def test_export(self):
        mock_service = mock.Mock(spec=Service)
        self.mock_urlparse.return_value.scheme = 'http'
        mock_service.cargo = self.mock_image
        mock_service.cargo.return_value.push.return_value = None
        mock_service.alias = 'foo-bar'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        self.assertTrue(container_ship.export(service=mock_service))

    def test_export_failure(self):
        mock_service = mock.Mock(spec=Service)
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.export(service=False)
        with self.assertRaises(ValueError):
            mock_service.cargo = None
            container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
            container_ship.export(service=mock_service)

    @mock.patch('freight_forwarder.container_ship.Container')
    @mock.patch('freight_forwarder.container_ship.re')
    def test_find_service_containers(self, mock_re, mock_container):
        mock_container.name = 'foo-bar'
        mock_container.find_by_name.return_value = {'foo-bar': mock_container}
        mock_service = mock.Mock(spec=Service)
        mock_service.alias = 'foo-bar'
        self.mock_urlparse.return_value.scheme = 'http'
        container_ship = ContainerShip(address='http://127.0.0.1:2376', **{})
        self.assertTrue('foo-bar' in container_ship.find_service_containers(service=mock_service))

    def test_find_previous_service_containers(self):
        pass

    def test_load_cargo(self):
        pass

    def test_offload_project(self):
        pass

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

    def test_start_service_containers(self):
        pass

    def test_service(self):
        pass

    def test_service_map(self):
        pass

    def test_service_map_failure(self):
        self.mock_urlparse.return_value.scheme = 'http'
        with self.assertRaises(TypeError):
            container_ship = ContainerShip(address='https://127.0.0.1:2376', **{})
            container_ship._service_map(service=False, callback=False)

    def test_offload_cargo(self):
        pass

    def test_container_registration(self):
        pass

    def test_load_dependency_containers(self):
        pass

    def test_load_service_containers(self):
        pass

    def test_load_service_cargo(self):
        pass

    def test_update_container_host_config(self):
        pass

    def test_update_links(self):
        pass

    def test_update_volumes_from(self):
        pass

    def test_request_auth(self):
        pass

if __name__ == '__main__':
    unittest.main()
