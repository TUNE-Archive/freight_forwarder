# -*- coding: utf-8; -*-
from __future__ import absolute_import, unicode_literals

from tests import unittest, mock
from tests.factories.docker_client_factory import DockerClientFactory

from freight_forwarder.container.config import Config
from freight_forwarder.image import Image
from freight_forwarder.registry.registry import V2

import docker
import requests


class ImageTest(unittest.TestCase):

    def setUp(self):
        self.docker_client = DockerClientFactory()

    def tearDown(self):
        del self.docker_client

    @mock.patch.object(Image, '_inspect_and_map')
    def test_create_image(self, mock_image_inspect):
        image = Image(client=self.docker_client, identifier='123')
        self.assertEqual(image.identifier, '123')
        self.assertIsInstance(image, Image)

    def test_create_image_failure(self):
        with self.assertRaises(Exception):
            Image(client=False, identifier='123')
        with self.assertRaises(TypeError):
            Image(client=self.docker_client, identifier=False)

    @mock.patch.object(docker.api.ImageApiMixin, 'push')
    @mock.patch.object(V2, 'ping')
    @mock.patch.object(Image, 'tag')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_push(self, mock_image_inspect, mock_image_tag, mock_v2_registry_ping, mock_docker_image_push):
        mock_v2_registry = mock.Mock(spec=V2(address='https://v2.com'))
        mock_v2_registry_ping.return_value = True
        mock_docker_image_push.return_value = {}
        image = Image(client=self.docker_client, identifier='123')
        image.push(registry=mock_v2_registry, repository_tag='foo', tag='bar')
        self.assertTrue(True)  # TODO: ...

    @mock.patch.object(Image, '_inspect_and_map')
    def test_push_failure_invalid_registry(self, mock_image_inspect):
        with self.assertRaises(Exception):
            image = Image(client=self.docker_client, identifier='123')
            image.push(registry=False, repository_tag='foo')

    @mock.patch.object(Image, '_inspect_and_map')
    def test_push_failure_invalid_tag(self, mock_image_inspect):
        mock_v2_registry = mock.Mock(spec=V2(address='https://v2.com'))
        mock_v2_registry.return_value.ping.return_value = True
        with self.assertRaises(TypeError):
            image = Image(client=self.docker_client, identifier='123')
            image.push(registry=mock_v2_registry, repository_tag=False)

    @mock.patch.object(docker.api.ImageApiMixin, 'tag')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_tag(self, mock_image_inspect, mock_docker_image_tag):
        image = Image(client=self.docker_client, identifier='123')
        image.id = '123'
        image.tag(repository_tag='foo:bar', tags=['abc'])
        self.assertEqual(image.repo_tags, ('foo:abc', 'foo:bar'))

    @mock.patch.object(docker.api.ImageApiMixin, 'tag')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_tag_no_tags(self, mock_image_inspect, mock_docker_image_tag):
        image = Image(client=self.docker_client, identifier='123')
        image.id = '123'
        image.tag(repository_tag='foo')
        self.assertEqual(image.repo_tags, ('foo:latest',))

    @mock.patch.object(docker.api.ImageApiMixin, 'tag')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_tag_failure(self, mock_image_inspect, mock_docker_image_tag):
        with self.assertRaises(TypeError):
            image = Image(client=self.docker_client, identifier='123')
            image.tag(repository_tag=False, tags=[])
        with self.assertRaises(TypeError):
            image = Image(client=self.docker_client, identifier='123')
            image.tag(repository_tag='foo', tags=False)
        mock_docker_image_tag.side_effect = Exception
        with self.assertRaises(Exception):
            image = Image(client=self.docker_client, identifier='123')
            image.id = '123'
            image.tag(repository_tag='foo:bar', tags=['abc'])
            self.assertEqual(image.repo_tags, ('foo:abc', 'foo:bar'))

    @mock.patch.object(docker.api.ImageApiMixin, 'remove_image')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_delete(self, mock_image_inspect, mock_docker_image_remove):
        mock_docker_image_remove.return_value = None
        image = Image(client=self.docker_client, identifier='123')
        image.id = '123'
        self.assertTrue(image.delete())

    @mock.patch.object(docker.api.ImageApiMixin, 'remove_image')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_delete_failure(self, mock_image_inspect, mock_docker_image_remove):
        mock_docker_image_remove.return_value = True
        image = Image(client=self.docker_client, identifier='123')
        image.id = '123'
        self.assertFalse(image.delete())

        mock_docker_image_remove.side_effect = Exception
        mock_docker_image_remove.return_value = True
        image = Image(client=self.docker_client, identifier='123')
        image.id = '123'
        self.assertFalse(image.delete())

    @mock.patch.object(docker.api.ImageApiMixin, 'inspect_image')
    @mock.patch('freight_forwarder.image.ContainerConfig')
    def test_inspect_and_map(self, mock_container_config, mock_docker_image_inspect):
        mock_container_config.return_value = mock.Mock(spec=Config())
        mock_docker_image_inspect.return_value = {
            'Comment': '',
            'Id': '123',
            'VirtualSize': 491552314,
            'Container': '123',
            'Os': 'linux',
            'Parent': '456',
            'Created': '2015-11-23T23:11:31.282086214Z',
            'Architecture': 'amd64',
            'DockerVersion': '1.8.2',
            'Size': 0,
        }
        image = Image(client=self.docker_client, identifier='123')
        self.assertEqual(image.parent, '456')

    @mock.patch.object(docker.api.ImageApiMixin, 'inspect_image')
    def test_inspect_and_map_failure(self, mock_docker_image_inspect):
        mock_docker_image_inspect.side_effect = Exception
        with self.assertRaises(Exception):
            Image(client=self.docker_client, identifier='123')

    @mock.patch.object(docker.api.ImageApiMixin, 'images')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_all(self, mock_image_inspect, mock_docker_image_images):
        mock_docker_image_images.return_value = [{
            'VirtualSize': 817117650,
            'RepoTags': [],
            'Labels': {},
            'Size': 0,
            'Created': 1453314552,
            'Id': '123',
            'ParentId': '456',
            'RepoDigests': []
        }]
        images = Image.all(client=self.docker_client)
        self.assertIsInstance(images['123'], Image)

    def test_all_failure(self):
        with self.assertRaises(TypeError):
            Image.all(client=False)

    @mock.patch.object(docker.api.ImageApiMixin, 'images')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_find_by_name(self, mock_image_inspect, mock_docker_image_images):
        mock_docker_image_images.return_value = [{
            'VirtualSize': 817117650,
            'RepoTags': ['foo'],
            'Labels': {},
            'Size': 0,
            'Created': 1453314552,
            'Id': '123',
            'ParentId': '456',
            'RepoDigests': []
        }]
        image = Image.find_by_name(client=self.docker_client, name='foo')
        self.assertIsInstance(image, Image)
        self.assertEqual(image.identifier, 'foo')

    def test_find_by_name_failure(self):
        with self.assertRaises(TypeError):
            Image.find_by_name(client=False, name='foo')

    @mock.patch.object(docker.api.ImageApiMixin, 'images')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_find_all_by_name(self, mock_image_inspect, mock_docker_image_images):
        mock_docker_image_images.return_value = [{
            'VirtualSize': 817117650,
            'RepoTags': ['foo'],
            'Labels': {},
            'Size': 0,
            'Created': 1453314552,
            'Id': '123',
            'ParentId': '456',
            'RepoDigests': []
        }]
        images = Image.find_all_by_name(client=self.docker_client, name='foo')
        self.assertIsInstance(images['123'], Image)
        self.assertEqual(images['123'].identifier, 'foo')

    @mock.patch.object(docker.api.ImageApiMixin, 'pull')
    @mock.patch.object(requests.Session, 'close')
    @mock.patch.object(Image, '_inspect_and_map')
    def test_pull(self, mock_image_inspect, mock_request_session_close, mock_docker_image_pull):
        mock_registry = mock.Mock(spec=V2(address='https://v2.com'))
        mock_registry.ping.return_value = True
        mock_registry.location = ''
        mock_docker_image_pull.return_value = []
        image = Image.pull(client=self.docker_client, registry=mock_registry, repository_tag='foo:bar')
        self.assertIsInstance(image, Image)
        self.assertEqual(image.identifier, '/foo:bar')

    def test_pull_failure(self):
        mock_registry = mock.Mock(spec=V2(address='https://v2.com'))
        mock_registry.ping.return_value = False
        with self.assertRaises(TypeError):
            Image.pull(client=False, registry=mock_registry, repository_tag='foo')
        with self.assertRaises(Exception):
            Image.pull(client=self.docker_client, registry=False, repository_tag='foo')
        with self.assertRaises(TypeError):
            Image.pull(client=self.docker_client, registry=mock_registry, repository_tag=False)
        with self.assertRaises(AttributeError):
            Image.pull(client=self.docker_client, registry=mock_registry, repository_tag='foo:bar', tag='abc')
        with self.assertRaises(ValueError):
            Image.pull(client=self.docker_client, registry=mock_registry, repository_tag='foo:bar:abc')
        with self.assertRaises(Exception):
            Image.pull(client=self.docker_client, registry=mock_registry, repository_tag='foo:bar')

    @mock.patch.object(docker.api.BuildApiMixin, 'build')
    @mock.patch.object(requests.Session, 'close')
    @mock.patch.object(Image, '_inspect_and_map')
    @mock.patch('freight_forwarder.image.os')
    def test_build(self, mock_os, mock_image_inspect, mock_request_session_close, mock_docker_build):
        mock_os.path.exists.return_value = True
        mock_os.path.isfile.return_value = True
        mock_os.getcwd.return_value = '/'
        mock_os.path.realpath.return_value = '/'
        mock_docker_build.return_value = []
        image = Image.build(client=self.docker_client, repository_tag='foo', docker_file='abc')
        self.assertIsInstance(image, Image)
        self.assertEqual(image.identifier, 'foo:latest')

    @mock.patch('freight_forwarder.image.os')
    def test_build_failure(self, mock_os):
        mock_os.path.exists.return_value = True
        with self.assertRaises(TypeError):
            Image.build(client=False, repository_tag='foo', docker_file='abc')
        with self.assertRaises(Exception):
            Image.build(client=self.docker_client, repository_tag='foo', docker_file=False)
        with self.assertRaises(TypeError):
            Image.build(client=self.docker_client, repository_tag=False, docker_file='abc')
        with self.assertRaises(TypeError):
            Image.build(client=self.docker_client, repository_tag='foo', docker_file='abc', use_cache='yes')
