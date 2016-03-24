# -*- coding: utf-8; -*-
from __future__ import absolute_import, unicode_literals

import os

from tests import unittest, mock

from freight_forwarder        import FreightForwarder
from freight_forwarder.config import ConfigDict


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
