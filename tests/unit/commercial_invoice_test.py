from __future__ import absolute_import, unicode_literals

import os

from tests import unittest, mock
from mock import call
from freight_forwarder.commercial_invoice import CommercialInvoice
from freight_forwarder.freight_forwarder  import FreightForwarder


class CommercialInvoiceConstructorTest(unittest.TestCase):

    def setUp(self):
        self.hosts = {
            'default': [
                {
                    'verify': False,
                    'ssl_cert_path': '/Users/alexb/.docker/machine/machines/ff02-dev',
                    'address': 'https://172.16.135.137:2376'
                }
            ]
        }

        self.registries = {
            'development':
                {
                    'verify': False,
                    'address': 'https://development-registry.com'
                }
        }

        self.services = {
            'app': {
                'test': './test/',
                'links': ['redis'],
                'build': './',
                'ports': ['4567:4567']
            },
            'redis': {
                'detach': True,
                'image': 'docker_hub/library/redis:latest',
                'ports': ['5379:5379']
            }
        }

    def tearDown(self):
        pass

    @mock.patch.object(CommercialInvoice, '_create_registries', autospec=True)
    @mock.patch.object(CommercialInvoice, '_create_container_ships', autospec=True)
    def test_tags_and_tagging_scheme_defaults(self, mocked_create_registries, mocked_create_container_ships):
        commercial_invoice = CommercialInvoice(
            'power_rangers',
            'mighty_morphing',
            self.services,
            self.hosts,
            'app',
            'quality_control',
            'development',
            'local',
            self.registries
        )

        self.assertEqual(commercial_invoice.tags, [])
        self.assertEqual(commercial_invoice._tagging_scheme, True)


class CommercialInvoiceInjectorTest(unittest.TestCase):

    def setUp(self):
        self.hosts = {
            'default': [
                {
                    'verify': False,
                    'ssl_cert_path': '/Users/alexb/.docker/machine/machines/ff02-dev',
                    'address': 'https://172.16.135.137:2376'
                }
            ]
        }

        self.services = {
            'app': {
                'test': './test/',
                'links': ['redis'],
                'build': './',
                'ports': ['4567:4567']
            },
            'redis': {
                'detach': True,
                'image': 'docker_hub/library/redis:latest',
                'ports': ['5379:5379']
            }
        }

    def tearDown(self):
        pass

    @mock.patch.object(CommercialInvoice, '_create_registries', autospec=True)
    @mock.patch('freight_forwarder.commercial_invoice.commercial_invoice.Injector', create=True)
    @mock.patch.object(CommercialInvoice, '_create_container_ships', autospec=True)
    def test_default_without_injector_registry(self, mocked_create_container_ships, mocked_injector, mocked_create_registries):
        mocked_injector.return_value = mock.Mock()
        mocked_create_registries.return_value = {
            'default': mocked_injector.return_value,
            'docker_hub': mock.Mock(),
            'development': mock.Mock()
        }

        registries = {
            'development': {
                'verify': False,
                'address': 'https://docker-dev.ops.tune.com'
            },
            'default': {
                'verify': False,
                'address': 'https://default-registry.com'
            }

        }

        commercial_invoice = CommercialInvoice(
            'power_rangers',
            'mighty_morphing',
            self.services,
            self.hosts,
            'app',
            'quality_control',
            'development',
            'local',
            registries
        )

        self.assertEqual(commercial_invoice.injector, mocked_injector.return_value)
        mocked_injector.assert_called_once_with(
            'development',
            'local',
            'mighty_morphing',
            mocked_injector.return_value
        )

    @mock.patch.object(CommercialInvoice, '_create_registries', autospec=True)
    @mock.patch('freight_forwarder.commercial_invoice.commercial_invoice.Injector', create=True)
    @mock.patch.object(CommercialInvoice, '_create_container_ships', autospec=True)
    def test_registry_with_injector_provided(self, mocked_create_container_ships, mocked_injector, mocked_create_registries):
        mocked_injector.return_value = mock.Mock()

        mocked_create_registries.return_value = {
            'default': mock.Mock(),
            'docker_hub': mock.Mock(),
            'development': mock.Mock(),
            'injector': mocked_injector.return_value
        }

        registries = {
            'development': {
                'verify': False,
                'address': 'https://docker-dev.ops.tune.com'
            },
            'default': {
                'verify': False,
                'address': 'https://default-registry.com'
            },
            'injector': {
                'verify': False,
                'address': 'https://injector-registry.com'
            }

        }

        commercial_invoice = CommercialInvoice(
            'power_rangers',
            'mighty_morphing',
            self.services,
            self.hosts,
            'app',
            'quality_control',
            'development',
            'local',
            registries
        )

        self.assertEqual(commercial_invoice.injector, mocked_injector.return_value)
        mocked_injector.assert_called_once_with(
            'development',
            'local',
            'mighty_morphing',
            mocked_injector.return_value
        )


class CommercialInvoiceCreateContainershipsTest(unittest.TestCase):
    def setUp(self):
        self.freight_forwarder = FreightForwarder(
            config_path_override=os.path.join(os.getcwd(),
                                              'tests',
                                              'fixtures',
                                              'test_freight_forwarder.yaml'),
            verbose=False
        )

    def tearDown(self):
        del self.freight_forwarder

    @mock.patch.object(CommercialInvoice, '_create_registries', autospec=True)
    @mock.patch('freight_forwarder.commercial_invoice.commercial_invoice.ContainerShip', create=True)
    def test_create_containerships_with_deploy(self, mock_container_ship, mocked_create_registries):
        """
        Validate the deployment host or hosts is available inside the commercial invoice
        :param mock_container_ship:
        :param mocked_create_registries:
        :return:
        """
        commercial_invoice = self.freight_forwarder.commercial_invoice(
            'deploy',
            'local',
            'development',
            'tomcat-test'
        )
        self.assertEqual(len(commercial_invoice.container_ships), 3)
        self.assertIn('tomcat-test', commercial_invoice.container_ships.keys())
        self.assertEqual(len(commercial_invoice.container_ships['tomcat-test']), 1)

    @mock.patch.object(CommercialInvoice, '_create_registries', autospec=True)
    @mock.patch('freight_forwarder.commercial_invoice.commercial_invoice.ContainerShip', create=True)
    @mock.patch('freight_forwarder.commercial_invoice.commercial_invoice.os')
    def test_create_containerships_with_no_default(self, mock_os, mock_container_ship, mocked_create_registries):
        """
        Validate the the container_ship creation with no default defined in the configuration
        :param mock_container_ship:
        :param mocked_create_registries:
        :return:
        """
        # Remove default hosts to ensure it is created
        hosts = self.freight_forwarder._config.get('hosts', 'environments', 'development', 'local')
        del hosts['default']

        commercial_invoice = self.freight_forwarder.commercial_invoice(
            'deploy',
            'local',
            'development',
            'tomcat-test'
        )
        self.assertEqual(mock_os.getenv.call_count, 3)
        calls =  [call('DOCKER_TLS_VERIFY'), call('DOCKER_CERT_PATH'), call('DOCKER_HOST')]
        mock_os.getenv.assert_has_call(calls, any_order=True)
