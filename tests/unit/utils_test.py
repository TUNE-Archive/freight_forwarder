# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
import string
import random
import os
import json

from tests import unittest, mock

from freight_forwarder.utils import *

import requests


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

    def test_normalize_keys(self):
        test_data = {
            "progressDetail": {
                "current": 655337,
                "start": 1413994898,
                "total": 20412416
            }
        }

        test_normalize_keys = normalize_keys(test_data)

        self.assertIn('progress_detail', test_normalize_keys)

    def test_normalize_value(self):
        test_string = "TestValue"

        test_normalize_value = normalize_value(test_string)

        self.assertEqual(test_normalize_value, "test_value")


class UtilsParseStreamTest(unittest.TestCase):
    def setUp(self):
        # Patch sys.stdout for stream
        self.patch_utils_stdout = mock.patch("freight_forwarder.utils.utils.stdout", name="utils_sys")
        self.mock_utils_stdout = self.patch_utils_stdout.start()

        # Patch normalized_values
        self.patch_utils_normalize_keys = mock.patch("freight_forwarder.utils.utils.normalize_keys",
                                                     name="utils_normalize_keys")
        self.mock_utils_normalize_keys = self.patch_utils_normalize_keys.start()

        # Patch Display Error
        self.patch_display_error = mock.patch("freight_forwarder.utils.utils._display_error",
                                              name="mock_display_error")
        self.mock_display_error = self.patch_display_error.start()

        # Patch Display Progress
        self.patch_display_progress = mock.patch("freight_forwarder.utils.utils._display_progress",
                                                 name="mock_display_error")
        self.mock_display_progress = self.patch_display_progress.start()

        # Patch Display Status
        self.patch_display_status = mock.patch("freight_forwarder.utils.utils._display_status",
                                               name="mock_display_status")
        self.mock_display_status = self.patch_display_status.start()

        # Patch Display Stream
        self.patch_display_stream = mock.patch("freight_forwarder.utils.utils._display_stream",
                                               name="mock_display_stream")
        self.mock_display_stream = self.patch_display_stream.start()

        # Mock Response Object
        self.mock_object_request = mock.MagicMock(spec=requests.PreparedRequest, url="https://docker-host.test.io:2376")
        self.mock_object_response = mock.MagicMock(spec=requests.Response, request=self.mock_object_request)

        self.mock_object_response.status_code = 404

    def tearDown(self):
        self.patch_utils_stdout.stop()
        self.patch_utils_normalize_keys.stop()
        self.patch_display_error.stop()
        self.patch_display_progress.stop()
        self.patch_display_status.stop()
        self.patch_display_stream.stop()
        del self.mock_object_request
        del self.mock_object_response

    def test_parse_stream_string(self):
        # Configure Mock response object with string
        test_values_list = ["test".encode('utf-8')]
        attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**attributes)

        parse_stream(self.mock_object_response)

        self.mock_utils_stdout.flush.assert_called_once_with()
        self.mock_utils_stdout.write.called_once_with('test')
        self.mock_utils_stdout.assert_has_calls([mock.call.write('test'), mock.call.flush()])

    def test_parse_stream_int(self):
        # Configure Mock response with int
        test_int = "{0}".format(123)
        test_int.encode('utf-8')
        test_values_list = [test_int]
        attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**attributes)

        test_parse_stream = parse_stream(self.mock_object_response)

        self.mock_utils_stdout.flush.assert_has_calls([mock.call.flush()])
        self.mock_utils_stdout.write.called_once_with('123')
        self.mock_utils_stdout.assert_has_calls([mock.call.write('123'), mock.call.flush()])
        self.assertEqual(test_parse_stream, [])

    def test_parse_stream_error(self):
        # Configure Mock response with error
        test_docker_response_error = {
            "error": "Test Error",
            "error_detail": {
                "code": "2",
                "message": "Test Error Message"
            }
        }
        test_docker_response_encoded = json.dumps(test_docker_response_error).encode('utf-8')
        test_values_list = [test_docker_response_encoded]

        # Configure Response object as iter
        iter_attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**iter_attributes)

        # Configure Normalized keys with return value
        mock_attributes_normalize_keys = {"return_value": test_docker_response_error}
        self.mock_utils_normalize_keys.configure_mock(**mock_attributes_normalize_keys)

        # Configure Mock for Display Error
        test_exception = {"side_effect": DockerStreamException(test_docker_response_error)}
        self.mock_display_error.configure_mock(**test_exception)

        with self.assertRaises(DockerStreamException):
            parse_stream(self.mock_object_response)

        self.mock_display_error.assert_called_with(test_docker_response_error, self.mock_utils_stdout)

    def test_parse_stream_progress(self):
        # Configure Mock response with progress
        test_docker_response_progress = {
            "status": "Pushing",
            "progress_detail": {
                "current": 655337,
                "start": 1413994898,
                "total": 20412416
            },
            "id": "51783549ce98",
            "progress": "[=>                                                 ] 790.1 kB/19.99 MB 30s"
        }
        test_docker_response_encoded = json.dumps(test_docker_response_progress).encode('utf-8')
        test_values_list = [test_docker_response_encoded]

        mock_response_attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**mock_response_attributes)

        # Configure Normalized keys with return value
        mock_attributes_normalize_keys = {"return_value": test_docker_response_progress}
        self.mock_utils_normalize_keys.configure_mock(**mock_attributes_normalize_keys)

        # Configure Mock for Display Progress
        attributes_display_progress = {"return_value": test_docker_response_progress}
        self.mock_display_progress.configure_mock(**attributes_display_progress)

        parse_stream(self.mock_object_response)

        self.mock_display_progress.assert_has_call(mock.call(test_docker_response_progress))

    def test_parse_stream_status(self):
        # Configure Mock response with status
        test_docker_response_status = {
            "status": "Download complete",
            "progress_detail": {},
            "id": "12340981vas"
        }
        test_docker_response_encoded = json.dumps(test_docker_response_status).encode('utf-8')
        test_values_list = [test_docker_response_encoded]

        mock_response_attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**mock_response_attributes)

        # Configure Normalized keys with return value
        mock_attributes_normalize_keys = {"return_value": test_docker_response_status}
        self.mock_utils_normalize_keys.configure_mock(**mock_attributes_normalize_keys)

        parse_stream(self.mock_object_response)

        self.mock_display_progress.assert_has_call(mock.call(test_docker_response_status))

    def test_parse_stream_stream(self):
        # Configure Mock response with stream
        test_docker_response_stream = {
            "stream": "test stream"
        }
        test_docker_response_encoded = json.dumps(test_docker_response_stream).encode('utf-8')
        test_values_list = [test_docker_response_encoded]

        mock_response_attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**mock_response_attributes)

        # Configure Normalized keys with return value
        mock_attributes_normalize_keys = {"return_value": test_docker_response_stream}
        self.mock_utils_normalize_keys.configure_mock(**mock_attributes_normalize_keys)

        parse_stream(self.mock_object_response)

        self.mock_display_stream.assert_has_call(mock.call(test_docker_response_stream))

    def test_parse_stream_json(self):
        # Defined json response for testing
        test_response_json = {"test": "test messsage", "foo": "bar"}
        test_response_json_encoded = json.dumps(test_response_json).encode('utf-8')
        test_values_list = [test_response_json_encoded]

        mock_response_attributes = {"__iter__.return_value": iter(test_values_list)}
        self.mock_object_response.configure_mock(**mock_response_attributes)

        # Configure normalize keys with dict
        mock_attributes_normalize_keys = {"return_value": test_response_json}
        self.mock_utils_normalize_keys.configure_mock(**mock_attributes_normalize_keys)

        parse_stream(self.mock_object_response)

        self.mock_utils_stdout.write.called_once_with(mock.call(test_response_json))
        self.mock_utils_stdout.flush.called_once_with(mock.call())


def random_string(n):
    """
    :param n: designated number of digits to return

    :return: Random string with the defined number of digits
    """
    if isinstance(n, int):
        return ''.join(random.choice((string.ascii_letters + string.digits)) for x in range(n))
    else:
        raise(TypeError("n has to be of type int"))
