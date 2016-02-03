# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
import json

import requests
import six
from tests import unittest, mock

from freight_forwarder.registry               import Registry, V1, V2
from freight_forwarder.registry.registry_base import RegistryBase, RegistryException
from ..factories.registry_factory import RegistryV1Factory, RegistryV2Factory


class RegistryTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(V1, '_validate_response', autospec=True, return_value=True)
    @mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
    def test_registry_v1_init(self, mock_requests, mock_v1_validate):
        test_registry = Registry()
        self.assertIsInstance(test_registry, RegistryBase)
        self.assertEquals(test_registry.ping(), True)

    @mock.patch.object(V1, '_validate_response', name="v1_validate")
    @mock.patch.object(V2, '_validate_response', name="v2_validate")
    @mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
    def test_registry_v2_init(self, mock_requests, mock_v2, mock_v1):
        mock_v1.side_effect = RegistryException("test")
        mock_v2.return_value = True
        test_v1_registry = RegistryV1Factory()
        test_v2_registry = RegistryV2Factory()
        # This is stated to ensure the test environment is setup correctly
        # validated v1.ping() returns an exception
        with self.assertRaises(RegistryException):
            test_v1_registry.ping()
        # validated v2.ping() returns an exception
        self.assertEquals(test_v2_registry.ping(), True)

        # Validate the logic of the registry class to return a V2 object
        test_registry = Registry(address="https://v2.dockertest.io")
        self.assertIsInstance(test_registry, RegistryBase)


class RegistryV1Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(V1, '_validate_response', return_value=True)
    @mock.patch.object(V1, '_request_builder')
    @mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
    def test_v1_search(self, mock_requests, mock_request_builder, mock_validate_response):
        # Defined Search Request a
        search_response_content = {
            "num_results": 3,
            "query": "test",
            "results": [
                {"description": "api test app", "name": "testproject/test-app"},
                {"description": "database test app", "name": "testproject/test-db"},
                {"description": "cache test app", "name": "testproject/test-cache"}
            ]
        }

        # Define Response Value for content once request has been validated
        mock_request_builder.return_value = create_response_object(
            url="https://search.registry.docker.com",
            status_code=200,
            content=json.dumps(search_response_content).encode('utf-8')
        )

        # Define Default value for utils _validate_reponse
        mock_validate_response.return_value = True

        # Build V1 Factory Registry
        test_registry = RegistryV1Factory(address='https://search.registry.docker.com')

        results = test_registry.search("test")
        self.assertIsInstance(results, dict)

    @mock.patch.object(V1, '_validate_response', return_value=True)
    @mock.patch.object(V1, '_request_builder')
    @mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
    def test_v1_tags(self, mock_requests, mock_request_builder, mock_validate_response):
        tag_response_content = {
            "0.1": "3fad19bfa2",
            "latest": "xxxxxxxxxx",
            "localtest": "xxxxxxxxxxxxxxae13",
            "redis123123": "xxxxxxxxxxxxxxae132",
            "jira1268": "xxxxxxxxxxxxxxae1324987"
        }

        formatted_output = [
            'appexample/test-app:0.1',
            'appexample/test-app:latest',
            'appexample/test-app:us-east-01-dev',
            'appexample/test-app:localtest',
            'appexample/test-app:redis123123',
            'appexample/test-app:jira1268'
        ]

        mock_request_builder.return_value = create_response_object(
            url="https://tag.registry.docker.com",
            status_code=200,
            content=json.dumps(tag_response_content).encode('utf-8')
        )

        mock_validate_response.return_value = True

        test_registry = RegistryV1Factory(address='https://tag.registry.docker.com')

        for tag in test_registry.tags("appexample/test-app"):
            tag_output = "".join(tag)
            self.assertIsInstance(tag_output, six.string_types)
            self.assertIn(tag_output, formatted_output)

    def test_delete_tag(self):
        self.skipTest("Implemented but not used")

    def test_delete(self):
        self.skipTest("Implemented but not used")

    def test_get_image_by_id(self):
        self.skipTest("Implemented but not used")

    def test_get_image_id_by_tag(self):
        self.skipTest("Implemented but not used")

    def set_image_tag(self):
        self.skipTest("Implemented but not used")


class RegistryV2Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(V2, '_validate_response', name='mock_v2_validate_response', return_value=True)
    @mock.patch.object(V2, '_request_builder', name='mock_v2_request_builder')
    @mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
    def test_v2_search(self, mock_requests, mock_request_builder, mock_validate_response):
        # Defined Search Request
        search_response_content = json.dumps({"repositories": ["appexample/test-app",
                                                               "appexample/test-db",
                                                               "appexample/test-cache"]}).encode('utf-8')

        response = create_response_object(url="https://v2search.registry.docker.com",
                                          status_code=200,
                                          content=search_response_content)

        # Define Response Value for content once request has been validated
        mock_request_builder.return_value = response
        # Define Default value for utils _validate_response
        mock_validate_response.return_value = True

        # Build V1 Factory Registry
        test_registry = RegistryV2Factory(address='https://v2search.registry.docker.com')
        test_registry.search("test")

        for search in test_registry.search("test"):
            search_output = "".join(search)
            self.assertIsInstance(search_output, six.string_types)

    @mock.patch.object(V2, '_validate_response', name='mock_v2_validate_response', return_value=True)
    @mock.patch.object(V2, '_request_builder', name='mock_v2_request_builder')
    @mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
    def test_v2_tags(self, mock_requests, mock_request_builder, mock_validate_response):
        tag_response_content = json.dumps({"name": "appexample/test-app",
                                           "tags": [
                                               "latest",
                                               "0.0.15",
                                               "asdfasb81"]
                                           }
                                          ).encode('utf-8')

        formatted_output = ['appexample/test-app:latest',
                            'appexample/test-app:0.0.15',
                            'appexample/test-app:asdfasb81']

        response = create_response_object(url="https://v2tags.registry.docker.com",
                                          status_code=200,
                                          content=tag_response_content)

        mock_request_builder.return_value = response
        mock_validate_response.return_value = True

        test_registry = RegistryV2Factory(address='https://v2tags.registry.docker.com')

        for tags in test_registry.tags("appexample/test-app"):
            tag_output = "".join(tags)
            self.assertIsInstance(tag_output, six.string_types)
            self.assertIn(tag_output, formatted_output)

    def test_blobs(self):
        self.skipTest("Not implemented")

    def test_catalog(self, count=None, last=None):
        self.skipTest("Not implemented")

    def test_manifests(self):
        self.skipTest("Not implemented")


class RegistryBaseTests(unittest.TestCase):
    def setUp(self):
        self.patch_requests = mock.patch('freight_forwarder.registry.registry_base.requests', autospec=True)
        self.patch_requests.start()
        self.test_registry = RegistryV1Factory(address="https://registrybasetest.docker.com")

    def tearDown(self):
        self.patch_requests.stop()
        del self.test_registry

    def test_ping(self):
        self.skipTest("Defined as abc method. Override in class")

    def test_tags(self):
        self.skipTest("Defined as abc method. Override in class")

    def test_init(self):
        self.assertEquals(self.test_registry.scheme, 'https://')
        self.assertEquals(self.test_registry.location, 'registrybasetest.docker.com')
        self.assertEquals(self.test_registry.auth, None)
        self.assertEquals(self.test_registry.__str__(), "https://registrybasetest.docker.com")
        self.assertIsInstance(self.test_registry, RegistryBase)

    def test_registry_base_auth_base_functionality(self):
        self.assertEquals(self.test_registry.auth, None)

        with self.assertRaises(TypeError):
            self.test_registry.auth = ["user=test_user", "passwd=password"]

    def test_registry_base_auth_with_auth(self):
        pass


class RegistryExceptionTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_exception_with_status_code_and_url(self):
        response = create_response_object(url="https://bad.docker.io",
                                          status_code=503,
                                          content={"test": "data"})
        registry_exception = RegistryException(response)
        self.assertIsInstance(registry_exception, RegistryException)
        self.assertEquals(registry_exception.response.status_code, 503)

    def test_exception_with_no_content(self):
        response = create_response_object(url="https://nocontent.docker.io",
                                          status_code=503)
        registry_exception = RegistryException(response)
        self.assertIsInstance(registry_exception, RegistryException)
        self.assertEquals(registry_exception.message, 'There was an issue with the request to the docker registry.')

    def test_exception_with_error_content(self):
        # TODO - grab a properly formatted error for testing
        response = create_response_object(url="https://errorcontent.docker.io",
                                          status_code=500,
                                          content=json.dumps({'error': 'Docker Registry Error Example'}))
        registry_exception = RegistryException(response)
        self.assertIsInstance(registry_exception, RegistryException)
        self.assertEquals(registry_exception.message, 'Docker Registry Error Example')

        # Test the class.__str__ MagicMethod
        self.assertEquals("{0}".format(registry_exception), 'Docker Registry Error Example')


def create_response_object(url, status_code, content=None):
    """
    The function generates a mock object that is properly formatted for the RegistryException and validates the input

    :param url: url to pass through for the mock request object
    :param status_code: status code to append to the response object
    :param content: **required** if not provided, this attribute will be blocked
    :return: Parent Mock: request.Reponse Child Mock: request - requests.PreparedRequest
    """
    if not isinstance(url, six.string_types):
        raise(TypeError("incorrect type provided for url"))

    if not isinstance(status_code, six.integer_types):
        raise(TypeError("incorrect type provided for http status code"))

    mock_object_request = mock.MagicMock(spec=requests.PreparedRequest, url=url)
    mock_object_response = mock.MagicMock(spec=requests.Response, request=mock_object_request)
    mock_object_response.status_code = status_code

    if content:
        mock_object_response.content = content
    else:
        # this blocks the content attribute from being present
        del mock_object_response.content

    return mock_object_response


def format_image_results(registry_response_dict):
    """
    Response attribute content is formatted correctly for the Images

    :param response: response object with content attribute
    :return: dict of various images
    """
    if not isinstance(registry_response_dict, dict):
        raise TypeError('registry_response_dict must be a dict.')

    images = {}
    results = registry_response_dict.get('results')

    if results:
        for image in results:
            images[image.get('name')] = image

    return images
