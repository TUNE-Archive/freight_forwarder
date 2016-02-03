# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
import string
import random
import os

from tests import unittest

from freight_forwarder.utils import *


class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.docker_https_host = 'https://docker-host.example.com:2376'
        self.docker_http_host  = 'http://docker-host.example.com:2375'
        self.localhost         = 'https://127.0.0.1:2376'
        self.bad_host          = 'http://docker-test'
        self.test_path         = os.getcwd()

    def tearDown(self):
        del self.docker_https_host
        del self.docker_http_host
        del self.localhost
        del self.bad_host
        del self.test_path

    def test_validate_uri_good_uri(self):
        uri = 'https://hub.docker.com'
        self.assertEquals(validate_uri(uri), 'https://hub.docker.com')

    def test_validate_uri_with_bad_uri(self):
        with self.assertRaises(TypeError):
            validate_uri('https:/hub.docker.com')

    def test_validate_path_good_path(self):
        self.assertEquals(validate_path(self.test_path), self.test_path)

    def test_validate_path_bad_path(self):
        with self.assertRaises(SystemError):
            validate_path('/path/to/null')

    def test_valid_domain(self):
        self.assertTrue(is_valid_domain_name(random_string(63)))

    def test_valid_domain_with_long_domain(self):
        self.assertFalse(is_valid_domain_name(random_string(64)))

    def test_valid_hostname_bad_with_hyphen(self):
        self.assertFalse(is_valid_hostname(''.join('-' + random_string(10))))

    def test_valid_hostname_bad_with_hyphen_at_end(self):
        self.assertFalse(is_valid_hostname(''.join(random_string(10) + '-')))

    def test_valid_hostname_with_good_hostname(self):
        self.assertTrue(is_valid_hostname(''.join(random_string(10) + '.' + 'example.com')))

    def test_valid_hostname_with_bad_hostname_length(self):
        self.assertFalse(is_valid_hostname(''.join(random_string(256) + '.' + 'example.com')))

    def test_valid_ip_with_valid_ip_address(self):
        ip = "127.0.0.1"
        self.assertTrue(is_valid_ip(ip))

    def test_valid_ip_with_valid_bad_ip_address(self):
        ip = "192.256.0.1"
        self.assertFalse(is_valid_ip(ip), msg="invalid ipv4 address passes")

    def test_valid_ip_with_valid_bad_ip_address_2(self):
        ip = "999.999.999.999"
        self.assertFalse(is_valid_ip(ip), msg="invalid ipv4 address passes")

    def test_http_scheme_with_http(self):
        self.assertEquals(parse_http_scheme(self.docker_http_host), 'http://')

    def test_http_scheme_with_no_scheme(self):
        self.assertEquals(parse_http_scheme('docker-host.example.com'), 'http://')

    def test_http_scheme_with_https(self):
        self.assertEquals(parse_http_scheme(self.docker_https_host), 'https://')

    def test_parse_hostname_with_good_hostname(self):
        self.assertEquals(parse_hostname(self.docker_http_host), 'docker-host.example.com')

    def test_parse_hostname_with_localhost(self):
        self.assertEquals(parse_hostname(self.localhost), '127.0.0.1')

    def test_parse_hostname_with_bad_hostname(self):
        with self.assertRaises(TypeError):
            parse_hostname(self.bad_host)

    def test_path_regex_bad(self):
        self.assertEquals(path_regex('/path/test&/nowhere'), None)

    def test_path_regex_good(self):
        test_path_object = path_regex(self.test_path)
        self.assertEquals(test_path_object.string, self.test_path)


def random_string(n):
    """
    :param n: designated number of digits to return

    :return: Random string with the defined number of digits
    """
    if isinstance(n, int):
        return ''.join(random.choice((string.ascii_letters + string.digits)) for x in range(n))
    else:
        raise(TypeError("n has to be of type int"))
