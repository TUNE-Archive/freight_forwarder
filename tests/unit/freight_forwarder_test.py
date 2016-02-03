from __future__ import absolute_import, unicode_literals

from tests import unittest

from freight_forwarder import FreightForwarder


class FreightForwarderTest(unittest.TestCase):
    def setup(self):
        """Some Mock
        """

    def test_valid_repository(self):
        self.assertRaises(TypeError, lambda: FreightForwarder(1, "cia"))
        self.assertRaises(TypeError, lambda: FreightForwarder([], "cia"))
        self.assertRaises(TypeError, lambda: FreightForwarder({}, "cia"))
        self.assertRaises(TypeError, lambda: FreightForwarder(None, "cia"))
        self.assertRaises(TypeError, lambda: FreightForwarder(type, "cia"))

    def test_valid_name(self):
        """
        """
        pass
