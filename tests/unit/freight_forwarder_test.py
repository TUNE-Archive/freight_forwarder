# -*- coding: utf-8; -*-
from __future__ import absolute_import, unicode_literals

import os


from tests import unittest, mock
from mock import call

from ..factories.registry_factory import RegistryV1Factory

from freight_forwarder        import FreightForwarder
from freight_forwarder.config import ConfigDict
from freight_forwarder.commercial_invoice.commercial_invoice import CommercialInvoice


class FreightForwarderTest(unittest.TestCase):
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

    @mock.patch('freight_forwarder.freight_forwarder.CommercialInvoice', create=True)
    def test_commercial_invoice_export_and_deploy_service(self, mock_commercial_invoice):
        commercial_invoice = self.freight_forwarder.commercial_invoice(
            action='export',
            data_center='local',
            environment='development',
            transport_service='tomcat-test'
        )
        commercial_invoice_services = mock_commercial_invoice.call_args[1].get('services')
        self.assertEqual(commercial_invoice_services['tomcat_test']['build'],
                          './Dockerfile')
        self.assertIsInstance(commercial_invoice_services['tomcat_test'], ConfigDict)

        self.assertNotIn('image', commercial_invoice_services['tomcat_test'].values())

    @mock.patch.object(FreightForwarder, '_FreightForwarder__complete_distribution')
    @mock.patch.object(FreightForwarder, '_FreightForwarder__dispatch')
    @mock.patch.object(FreightForwarder, '_FreightForwarder__wait_for_dispatch')
    @mock.patch.object(FreightForwarder, '_FreightForwarder__service_deployment_validation')
    @mock.patch.object(FreightForwarder, '_FreightForwarder__write_state_file', autospec=True)
    @mock.patch.object(FreightForwarder, '_FreightForwarder__validate_commercial_invoice')
    @mock.patch('freight_forwarder.commercial_invoice.commercial_invoice.ContainerShip', create=True)
    @mock.patch('freight_forwarder.freight_forwarder.logger', autospec=True)
    def test_assemble_fleet_with_yaml_variables_in_hosts(self,
                                                         mock_logger,
                                                         mock_container_ship,
                                                         mock_validate_commercial_invoice,
                                                         mock_write_state_file,
                                                         mock_service_deployment_validation,
                                                         mock_wait_for_dispatch,
                                                         mock_dispatch,
                                                         mock_complete_distribution
                                                         ):
        """
        Verify that feel is built correctly based on the provided configuration data
        :param mock_commercial_invoice:
        :return:
        """
        mock_registries = mock.patch.object(CommercialInvoice, '_create_registries', return_value={
            'tune_dev': RegistryV1Factory(),
            u'docker_hub': RegistryV1Factory()
        })
        mock_registries.start()
        mock_transport_service = mock.MagicMock(return_value='tomcat-test')

        self.freight_forwarder._bill_of_lading = {'failures': {}, 'successful': {}}
        commercial_invoice = self.freight_forwarder.commercial_invoice(
            action='deploy',
            data_center='local',
            environment='staging',
            transport_service=mock_transport_service()
        )
        mock_validate_commercial_invoice.return_value = commercial_invoice

        test_deployment = self.freight_forwarder.deploy_containers(
            commercial_invoice
        )

        # Ensure output of deployment is True based on no errors during the deployment process
        self.assertTrue(test_deployment)

        # Validate output of logging to ensure the correct host is output to the user
        calls = [call('Running deploy.'),
                 call('dispatching service: ffbug-example-tomcat-test on host: https://192.168.99.100:2376.')]
        mock_logger.info.assert_has_calls(calls)
