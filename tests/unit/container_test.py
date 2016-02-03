from __future__ import absolute_import, unicode_literals

import docker
import time

from tests import unittest, mock
from tests.factories.docker_client_factory   import DockerClientFactory

from freight_forwarder.container.config      import Config
from freight_forwarder.container.container   import Container
from freight_forwarder.container.host_config import HostConfig


class ContainerTest(unittest.TestCase):

    def setUp(self):
        """
        Setup Testing Environment for ContainerTest
        """
        self.docker_client = DockerClientFactory()

    def tearDown(self):
        del self.docker_client

    def test_config(self):
        with mock.patch.object(Container, '_create_container'):
            self.assertIsInstance(Container(self.docker_client, name='foo', image='bar').config, Config)

    def test_config_failure(self):
        with self.assertRaises(TypeError):
            with mock.patch.object(Container, '_create_container'):
                Container(DockerClientFactory(), name='foo', image='bar').config = 0

    def test_host_config(self):
        with mock.patch.object(Container, '_create_container'):
            test_container = Container(self.docker_client, name='foo', image='bar')
            test_container.host_config = HostConfig({'log_config': {"config": {}, "type": "syslog"}})
            self.assertIsInstance(test_container.host_config, HostConfig)

    def test_host_config_failure(self):
        with self.assertRaises(TypeError):
            with mock.patch.object(Container, '_create_container'):
                Container(self.docker_client, name='foo', image='bar').host_config = 0

    @mock.patch.object(docker.api.ContainerApiMixin, 'attach')
    def test_attach(self, mock_docker_container_mixin):
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            attach_data = container.attach()
            self.assertIsInstance(attach_data, list)

    @mock.patch.object(docker.api.ContainerApiMixin, 'commit')
    def test_commit(self, mock_docker_container_mixin):
        mock_docker_container_mixin.return_value = {'Id': '123'}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.name = 'foo'
            attach_data = container.commit(config=dict(), image_name='', tag='')
            self.assertEqual(attach_data, container.id)

    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    @mock.patch.object(docker.api.ContainerApiMixin, 'remove_container')
    def test_delete(self, mock_docker_container_remove, mock_docker_container_inspect):
        mock_docker_container_inspect.return_value = {'state': {'running': False}}
        mock_docker_container_remove.return_value = {}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.name = 'foo'
            self.assertEqual(container.delete(), {})

    def test_delete_failure(self):
        pass

    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    def test_inspect(self, mock_docker_container_inspect):
        mock_docker_container_inspect.return_value = {'state': {'running': True}}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.name = 'foo'
            self.assertEqual(container.inspect(), {'state': {'running': True}})

    def test_output(self):
        pass

    @mock.patch.object(Container, '_wait_for_exit_code')
    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    @mock.patch.object(docker.api.ContainerApiMixin, 'start')
    def test_start(self, mock_docker_container_start, mock_docker_container_inspect, mock_container_wait):
        mock_docker_container_inspect.return_value = {'state': {'running': True}}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.name = 'foo'
            self.assertTrue(container.start())

        mock_docker_container_inspect.return_value = {'state': {'running': False, 'exit_code': 0}}
        mock_docker_container_start.return_value = None
        mock_container_wait.return_value = 0
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.name = 'foo'
            self.assertTrue(container.start())

    def test_start_failure(self):
        pass

    @mock.patch.object(Container, '_start_recording')
    def test_start_transcribing(self, mock_container_start_recording):
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.start_transcribing()
            self.assertTrue(container._transcribe)
            self.assertIsNotNone(container._transcribe_queue)
            self.assertIsNotNone(container._transcribe_proc)
            self.assertTrue(container._transcribe_proc.daemon)

    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    def test_state(self, mock_docker_container_inspect):
        mock_docker_container_inspect.return_value = {'state': {'running': True}}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            self.assertEqual(container.state(), {'running': True})

    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    def test_running(self, mock_docker_container_inspect):
        mock_docker_container_inspect.return_value = {'state': {'running': True}}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            self.assertTrue(container.running())

        mock_docker_container_inspect.return_value = {'state': {'running': False}}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            self.assertFalse(container.running())

    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    @mock.patch.object(docker.api.ContainerApiMixin, 'stop')
    def test_stop(self, mock_docker_container_stop, mock_docker_container_inspect):
        mock_docker_container_inspect.return_value = {'state': {'running': False}}
        mock_docker_container_stop.return_value = True
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            container.name = 'foo'
            self.assertTrue(container.stop())

    @mock.patch.object(docker.api.ContainerApiMixin, 'wait')
    def test_wait(self, mock_docker_container_wait):
        mock_docker_container_wait.return_value = 0
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(self.docker_client, name='foo', image='bar', id='123')
            container.id = '123'
            self.assertEqual(container.wait(), 0)

    def test_dump_logs(self):
        pass

    @mock.patch.object(docker.api.ContainerApiMixin, 'containers')
    def test_find_by_name(self, mock_docker_container_containers):
        mock_docker_container_containers.return_value = [{
            'Id': '123',
            'Names': ['/foobar']
        }]
        with mock.patch.object(Container, '_find_by_id'):
            containers = Container.find_by_name(DockerClientFactory(), 'foobar')
            self.assertIsInstance(containers['foobar'], Container)

    @mock.patch.object(docker.api.ContainerApiMixin, 'containers')
    def test_find_by_name_failure(self, mock_docker_container_containers):
        with self.assertRaises(TypeError):
            Container.find_by_name(False, 'foobar')

        mock_docker_container_containers.side_effect = Exception
        with self.assertRaises(Exception):
            Container.find_by_name(DockerClientFactory(), 'foobar')

    @mock.patch.object(docker.api.ContainerApiMixin, 'create_container')
    @mock.patch.object(docker.api.ContainerApiMixin, 'create_host_config')
    def test_create_container(self, mock_docker_container_create_host_config, mock_docker_container_create_container):
        mock_docker_container_create_container.return_value = {'Id': '123', 'Warnings': ['foobar']}
        container = Container(DockerClientFactory(), name='foo', image='bar')
        self.assertEqual(container.id, '123')

    @mock.patch.object(docker.api.ContainerApiMixin, 'create_container')
    @mock.patch.object(docker.api.ContainerApiMixin, 'create_host_config')
    def test_create_container_failure(self, mock_docker_container_create_host_config, mock_docker_container_create_container):
        with self.assertRaises(TypeError):
            Container(DockerClientFactory(), name='foo', image='bar', container_config=[])
        with self.assertRaises(TypeError):
            Container(DockerClientFactory(), name='foo', image='bar', host_config=[])
        with self.assertRaises(TypeError):
            Container(None)
        with self.assertRaises(AttributeError):
            Container(DockerClientFactory(), name='foo')
        with self.assertRaises(TypeError):
            Container(DockerClientFactory(), name=1, image='bar')
        with self.assertRaises(TypeError):
            Container(DockerClientFactory(), name='foo', image=1)
        mock_docker_container_create_container.side_effect = Exception
        with self.assertRaises(Exception):
            Container(DockerClientFactory(), name='foo', image='bar')

    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    def test_find_by_id(self, mock_docker_container_inspect):
        mock_docker_container_inspect.return_value = {
            'Id': '123',
            'Name': 'foo',
            'Image': 'bar',
            'Created': '2016-01-20T23:05:25.351058124Z',
            'Config': {},
            'HostConfig': {}
        }
        container = Container(DockerClientFactory(), id='123')
        self.assertEqual(container.id, '123')

    def test_find_by_id_failure(self):
        with self.assertRaises(TypeError):
            Container(DockerClientFactory(), id=7)

    def test_start_recording(self):
        pass

    @mock.patch.object(time, 'sleep')
    @mock.patch.object(docker.api.ContainerApiMixin, 'inspect_container')
    def test_wait_for_exit_code(self, mock_docker_container_inspect, mock_time_sleep):
        mock_docker_container_inspect.return_value = {'state': {'running': False, 'exit_code': 0}}
        with mock.patch.object(Container, '_find_by_id'):
            container = Container(DockerClientFactory(), id='123')
            container.id = '123'
            exit_code = container._wait_for_exit_code()
            self.assertEqual(exit_code, 0)

if __name__ == '__main__':
    unittest.main()
