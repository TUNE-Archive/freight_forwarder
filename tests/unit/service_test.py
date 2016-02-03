# -*- coding: utf-8; -*-
from __future__ import absolute_import, unicode_literals
import os

import six
from tests import unittest, mock

from freight_forwarder.registry.registry import V1
from freight_forwarder.container.host_config import HostConfig
from freight_forwarder.container.config import Config as ContainerConfig
from tests.factories.service_factory import ServiceFactory


class ServiceTest(unittest.TestCase):
    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def setUp(self, mock_registry_class):
        self.mock_registry = mock_registry_class
        self.mock_registry_type = mock.Mock(spec=V1(address="https://v1.com"))
        self.mock_registry.return_value = self.mock_registry_type

        self.service_factory = ServiceFactory()

    def tearDown(self):
        del self.mock_registry_type
        del self.mock_registry
        del self.service_factory

    def test_init_bad_value_namespace(self):
        with self.assertRaises(TypeError):
            ServiceFactory(namespace=1)

    def test_init_bad_value_repository(self):
        with self.assertRaises(TypeError):
            ServiceFactory(repository=1)

    def test_init_bad_value_alias(self):
        with self.assertRaises(TypeError):
            ServiceFactory(alias=1)

    def test_init_bad_value_name(self):
        with self.assertRaises(TypeError):
            ServiceFactory(name=1)

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_init_of_source_registry(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type

        # Instance check
        self.assertIsInstance(self.service_factory.source_registry, V1)

        # Default values defined
        self.assertEquals(self.service_factory.source_registry, self.mock_registry_type)

        # Test initialization with wrong type
        with self.assertRaises(TypeError):
            self.service_factory.source_registry = int

        with self.assertRaises(TypeError):
            self.service_factory.source_registry = {}

        with self.assertRaises(TypeError):
            self.service_factory.source_registry = []

        self.service_factory.source_registry = None
        self.assertEqual(self.service_factory.source_registry, None)

        registry = mock_registry_class()
        self.service_factory.source_registry = registry
        mock_registry_class.assert_called_once()

        self.assertEqual(self.service_factory.source_registry, registry)

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_source_registry_property(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type
        # Test with None
        self.assertNotEquals(ServiceFactory(source_registry=None).source_registry, None)

        self.assertEquals(ServiceFactory(source_registry=self.mock_registry_type).source_registry, self.mock_registry_type)
        self.assertIsInstance(ServiceFactory(source_registry=self.mock_registry_type).source_registry, V1)

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_init_docker_file(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type

        test_path = os.getcwd()

        # with valid path
        self.assertIsInstance(ServiceFactory(docker_file=test_path).docker_file, six.string_types)

        # with None
        self.assertEquals(ServiceFactory(docker_file=None).docker_file, None)

        with self.assertRaises(Exception):
            ServiceFactory(docker_file=1)
        with self.assertRaises(Exception):
            ServiceFactory(docker_file=dict)
        with self.assertRaises(Exception):
            ServiceFactory(docker_file=list)
        with self.assertRaises(Exception):
            ServiceFactory(docker_file='/path/to/nowhere')

    def test_docker_file_property(self):
        self.assertEquals(self.service_factory.test_docker_file, None)

        with self.assertRaises(Exception):
            self.service_factory.docker_file = '/path/to/nowhere'

        with self.assertRaises(Exception):
            self.service_factory.docker_file = 1

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_init_with_test_docker_file(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type

        # with valid path
        self.assertIsInstance(ServiceFactory(test_docker_file=os.getcwd()).test_docker_file, six.string_types)

        # with None
        self.assertEquals(ServiceFactory(test_docker_file=None).test_docker_file, None)

    def test_test_docker_file_property(self):

        # TODO: update exception in property setter for test_docker_file
        with self.assertRaises(OSError, msg="OSError not raised when given in correct path"):
            self.service_factory.test_docker_file = '/path/to/nowhere'

        # TODO: update exception in property setter for test_docker_file
        with self.assertRaises(TypeError, msg="TypeError not raised in test_docker_file"):
            self.service_factory.test_docker_file = 1

    def test_init_with_docker_file_and_source_registry(self):
        docker_file_path = os.getcwd()
        service          = ServiceFactory(docker_file=docker_file_path, source_registry=self.mock_registry_type)

        self.assertEqual(service.docker_file, docker_file_path)
        self.assertEqual(service.source_registry, self.mock_registry_type)
        self.assertEqual(service.destination_registry, self.mock_registry_type)

    def test_name_property(self):
        self.assertIsInstance(self.service_factory.name, six.string_types)

        self.assertEquals(self.service_factory.name, 'api')

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_init_source_tag(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type

        self.assertEquals(ServiceFactory(namespace='appexample-api:xx90128123').source_tag, 'xx90128123')

        self.assertEquals(ServiceFactory(namespace='appexample-api:xx90128123').namespace, 'appexample-api')

        self.assertEquals(ServiceFactory(namespace='appexample-api').source_tag, 'latest')

        self.assertEquals(ServiceFactory(namespace='appexample-api').source_tag, 'latest')

        self.assertEquals(ServiceFactory(source_tag="a09f123x09").source_tag, 'a09f123x09')

        with self.assertRaises(TypeError):
            ServiceFactory(source_tag=1)

    def test_source_tag_property(self):
        self.assertEquals(self.service_factory.source_tag, 'asxkl8')

        with self.assertRaises(TypeError):
            self.service_factory.source_tag = int

        with self.assertRaises(TypeError):
            self.service_factory.source_tag = []

        with self.assertRaises(TypeError):
            self.service_factory.source_tag = {}

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_host_config(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type

        self.assertIsInstance(self.service_factory.host_config, HostConfig)

        mock_host_config = mock.Mock(spec=HostConfig, return_value=HostConfig(), create=True)
        self.assertEquals(ServiceFactory(host_config=mock_host_config).host_config, mock_host_config)

    def test_host_config_property(self):
        with self.assertRaises(TypeError):
            self.service_factory.host_config = int
        with self.assertRaises(TypeError):
            self.service_factory.host_config = []
        with self.assertRaises(TypeError):
            self.service_factory.host_config = {}

    def test_cargo_property(self):
        self.assertEquals(self.service_factory.cargo, None)

        with self.assertRaises(Exception):
            self.service_factory.cargo = int
        with self.assertRaises(Exception):
            self.service_factory.cargo = dict
        with self.assertRaises(Exception):
            self.service_factory.cargo = list

    def test_repository_property(self):
        self.assertEquals(self.service_factory.repository, 'teamexample')

    def test_alias_property(self):
        self.assertEquals(self.service_factory.alias, 'teamexample-appexample-api')

    def test_container_config_property(self):
        self.assertIsInstance(self.service_factory.container_config, ContainerConfig)

        mock_container_config = mock.Mock(spec=ContainerConfig, return_value=ContainerConfig(), create=True)
        with self.assertRaises(TypeError):
            self.service_factory.container_config = int
        with self.assertRaises(TypeError):
            self.service_factory.container_config = []
        with self.assertRaises(TypeError):
            self.service_factory.container_config = {}

        self.service_factory.container_config = mock_container_config()
        mock_container_config.assert_called_once_with()

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_destination_registry_property(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type
        # Instance check
        self.assertIsInstance(self.service_factory.destination_registry, V1)

        # Default values defined
        self.assertEquals(self.service_factory.destination_registry, self.mock_registry_type)

        # Test initialization with wrong type
        with self.assertRaises(TypeError):
            self.service_factory.destination_registry = int

        with self.assertRaises(TypeError):
            self.service_factory.destination_registry = list

        with self.assertRaises(TypeError):
            self.service_factory.destination_registry = dict

        self.service_factory.destination_registry = None
        self.assertEqual(self.service_factory.destination_registry, None)

        registry = mock_registry_class()
        self.service_factory.destination_registry = registry
        self.assertEqual(self.service_factory.destination_registry, registry)
        mock_registry_class.assert_called_once()

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def test_destination_registry_init(self, mock_registry_class):
        mock_registry_class.return_value = self.mock_registry_type
        # Test with None
        self.assertNotEquals(ServiceFactory(destination_registry=None).destination_registry, None)

    def test_configure_dependents_with_wrong_type(self):
        with self.assertRaises(TypeError):
            self.service_factory.configure_dependencies(int)
            self.service_factory.configure_dependencies([])
            self.service_factory.configure_dependencies('test')


class ServiceDependenciesTest(unittest.TestCase):

    @mock.patch('freight_forwarder.commercial_invoice.service.Registry')
    def setUp(self, mock_registry_class):
        self.mock_registry = mock_registry_class
        self.mock_registry_type = mock.create_autospec(spec=V1(address="https://v1.com"), spec_set=True)
        self.mock_registry.return_value = self.mock_registry_type
        self.api = ServiceFactory(name='api')
        self.build = ServiceFactory(name='build')
        self.database = ServiceFactory(name='database')
        self.cache = ServiceFactory(name='cache')
        self.nginx = ServiceFactory(name='nginx')

    def tearDown(self):
        del self.mock_registry
        del self.mock_registry_type
        del self.api
        del self.build
        del self.database
        del self.cache
        del self.nginx

    def test_configure_dependents_host_config_links_with_incorrect_formatted_link(self):
        # Link format is wrong and will ultimately fail due to being an incorrect format
        self.api.host_config.links = ['api']
        test_services = dict(api=self.api)
        with self.assertRaises(ReferenceError):
            self.api.configure_dependencies(test_services)

    def test_configure_dependents_host_config_volume_with_same_name(self):
        # Link format is wrong and will ultimately fail due to being an incorrect format
        self.api.host_config.volumes_from = ['api']
        test_services = dict(api=self.api)
        with self.assertRaises(ReferenceError):
            self.api.configure_dependencies(test_services)

    def test_configure_dependents_link(self):
        self.nginx.host_config.links = ['api']

        # Ensure the Service Object is named 'api'
        self.assertEquals(self.api.name, 'api')
        self.assertEquals(self.nginx.name, 'nginx')
        # Build the service dict
        test_services = dict(api=self.api,
                             nginx=self.nginx)

        self.nginx.configure_dependencies(test_services)
        self.assertEquals(self.nginx.dependencies, dict(api=self.api))

    def test_configure_dependency_link_with_good_link(self):
        self.api.host_config.links = ['database',
                                      'cache']
        self.nginx.host_config.links = ['api']

        # Ensure the Service Object is named 'api'
        self.assertEquals(self.api.name, 'api')
        # Build the service dict
        test_services = dict(api=self.api,
                             cache=self.cache,
                             database=self.database,
                             nginx=self.nginx)

        self.api.configure_dependencies(test_services)
        self.assertEquals(self.api.dependencies, dict(cache=self.cache,
                                                      database=self.database))
        self.assertEquals(self.api.dependents, dict(nginx=self.nginx))

    def test_configure_dependencies_host_config(self):
        self.api.host_config.volumes_from = ['build:ro']
        self.assertEquals(self.api.name, 'api')
        test_services = dict(api=self.api,
                             build=self.build)
        self.api.configure_dependencies(test_services)
        self.assertEquals(self.api.dependencies, dict(build=self.build))

    def test_configure_dependencies_host_config_with_same_name(self):
        self.build.host_config.volumes_from = ['build:ro']
        self.assertEquals(self.build.name, 'build')
        test_services = dict(build=self.build)
        with self.assertRaises(ReferenceError):
            self.build.configure_dependencies(test_services)

    def test_configure_dependencies_bad_dict(self):
        test_services = dict(build='build')
        with self.assertRaises(TypeError):
            self.build.configure_dependencies(test_services)

    def test_configure_dependencies_bad_services_type(self):
        test_services = [self.api, self.build]
        with self.assertRaises(TypeError):
            self.build.configure_dependencies(test_services)
