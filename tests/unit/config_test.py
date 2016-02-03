# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
from hashlib import md5

import shutil
import tempfile
import os
import json
import six

from tests import unittest, mock

from freight_forwarder.config import Config, ConfigValidationException, ConfigDict, ConfigUnicode


class ConfigTest(unittest.TestCase):
    def setUp(self):
        """ Do somethings
        """
        self.temp_dir = tempfile.mkdtemp()
        with open(os.path.join(self.temp_dir, 'freight-forwarder.yml'), 'w') as config:
            config.write(
                """---
                team: itops
                project: "docker-example"
                repository: "git@github.com:TuneOSS/freight_forwarder.git"

                app:
                  build: "./"
                  test: "./test/"
                  links:
                    - redis
                  ports:
                      - "4567:4567"

                redis:
                  image: "docker_hub/library/redis:latest"
                  detach: true
                  ports:
                     - "5379:5379"

                registries:
                  default:
                    address: "https://docker-dev.registry.com"
                    verify: false

                environments:
                  jenkins: &jenkins
                    address: "https://your-jenkins-server03.sea1.office.priv:2376"
                    ssl_cert_path: "/etc/docker/certs/client/production/"
                    verify: false

                  vivek: &vivek
                    address: "https://192.168.99.100:2376"
                    ssl_cert_path: "/Users/vivek/.docker/machine/machines/vivek"
                    verify: false

                  development:
                    local:
                      hosts:
                        default:
                          - *vivek
                      deploy:
                        app:
                          image: "default/itops/docker-example-app:latest"
                    ci:
                      hosts:
                        export:
                          - *jenkins
                      deploy:
                        app:
                          image: "default/itops/docker-example-app:latest"

                  production:
                    ci:
                      hosts:
                        export:
                          - *jenkins

                      deploy:
                        app:
                          image: "default/itops/docker-example-app:local-production-latest"
                          log_config:
                            type: syslog
                            config:
                              syslog-tag: "cia-api"
                              syslog-facility: "local6"

                      export:
                        app:
                          image: "default/itops/docker-example-app:local-development-latest"
          """.format('utf-8')
            )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # TODO: come back and test loading of the config a more thoroughly. just bear minimum now,
    @mock.patch.object(Config, '_load', autospec=True)
    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    def test_config_path(self, mocked_os, mocked_load):
        mocked_os.return_value = self.temp_dir
        config = Config()

        self.assertEquals(config._path, self.temp_dir)
        mocked_load.assert_called_once_with(config)

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    def test_invalid_path(self, mock_cwd):
        mock_cwd.return_value = '/road/to/nowhere/'

        with self.assertRaises(LookupError):
            Config()

    @mock.patch.object(Config, '_load', autospec=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_path_override(self, mocked_load, mocked_logger):
        with self.assertRaises(TypeError):
            Config(path_override=121412)
            mocked_logger.assert_called_once_with("path_override must be a string.")
            mocked_load.assert_not_called()

        config = Config('/some/new/path/')
        self.assertEquals(config._path, '/some/new/path/')

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    def test_load(self, mock_cwd):
        mock_cwd.return_value = self.temp_dir
        config = Config()

        self.assertIsInstance(config._data, ConfigDict)

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    def test_original_config_mutation(self, mock_cwd):
        # self.skipTest('need to fix issues with config._data.  should be a ConfigDict not dict.')
        mock_cwd.return_value = self.temp_dir

        config = Config()
        original_md5 = md5(json.dumps(config._data).encode()).digest()
        config.validate()

        self.assertEquals(original_md5, md5(json.dumps(config._data).encode()).digest())

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_team(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()

        config.validate()
        self.assertEquals(config.team, config._data['team'])
        self.assertEquals(config.team, 'itops')
        self.assertEquals(config.team, config.get('team'))
        self.assertIsInstance(config.team, ConfigUnicode)

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_without_team(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()
        del config._data['team']
        with self.assertRaises(ConfigValidationException) as cve:
            config.validate()

        self.assertEquals('required', cve.exception.validation_type)
        self.assertIn('team', cve.exception.validation_value)
        mock_logger.assert_called_with('root failed validation: required. Potential fixes in root add/delete/update team.')

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_with_team_misspelled(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()
        config._data['tem'] = config._data['team']
        del config._data['team']
        with self.assertRaises(ConfigValidationException) as cve:
            config.validate()

        self.assertEquals('required', cve.exception.validation_type)
        self.assertEquals('root', cve.exception.property_name)
        mock_logger.assert_called_with('root failed validation: required. Potential fixes in root add/delete/update team.')

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_team_wrong_type(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()
        config._data['team'] = 3452345

        with self.assertRaises(ConfigValidationException) as cve:
            config.validate()

        self.assertEquals('type', cve.exception.validation_type)
        self.assertEquals('team', cve.exception.property_name)
        text_type = six.string_types[0].__name__
        mock_logger.assert_called_with(
            'team failed validation: type. '
            'Potential fixes in team add/delete/update {0}, {0}.'.format(text_type)
        )

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_project(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()

        config.validate()
        self.assertEquals(config.project, config._data['project'])
        self.assertEquals(config.project, 'docker-example')
        self.assertEquals(config.project, config.get('project'))
        self.assertIsInstance(config.project, ConfigUnicode)

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_without_project(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()
        del config._data['project']
        with self.assertRaises(ConfigValidationException) as cve:
            config.validate()

        self.assertEquals('required', cve.exception.validation_type)
        self.assertIn('project', cve.exception.validation_value)
        mock_logger.assert_called_with('root failed validation: required. Potential fixes in root add/delete/update project.')

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_with_project_misspelled(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()
        config._data['proect'] = config._data['project']
        del config._data['project']
        with self.assertRaises(ConfigValidationException) as cve:
            config.validate()

        self.assertEquals('required', cve.exception.validation_type)
        self.assertEquals('root', cve.exception.property_name)
        mock_logger.assert_called_with('root failed validation: required. Potential fixes in root add/delete/update project.')

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_project_wrong_type(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()
        config._data['project'] = 763463423

        with self.assertRaises(ConfigValidationException) as cve:
            config.validate()

        self.assertEquals('type', cve.exception.validation_type)
        self.assertEquals('project', cve.exception.property_name)
        text_type = six.string_types[0].__name__
        mock_logger.assert_called_with(
            'project failed validation: type. '
            'Potential fixes in project add/delete/update {0}, {0}.'.format(text_type)
        )

    @mock.patch('freight_forwarder.config.os.getcwd', create=True)
    @mock.patch('freight_forwarder.config.logger.error', create=True)
    def test_hosts(self, mock_logger, mocked_os):
        mocked_os.return_value = self.temp_dir
        config = Config()

        config.validate()
        self.assertEquals(config.project, config._data['project'])
        self.assertEquals(config.project, 'docker-example')
        self.assertEquals(config.project, config.get('project'))
        self.assertIsInstance(config.project, ConfigUnicode)
