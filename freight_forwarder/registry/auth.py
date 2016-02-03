from __future__ import unicode_literals, absolute_import
import os
import six
import base64
import json
import time
import uuid

import requests

from ..utils import utils


AUTH_TYPES = ('registry_rubber', 'basic')


# TODO: update to support new docker configuration file path.
class Auth(object):
    def __init__(self, registry, registry_version, **kwargs):
        """

        :param auth_type:
        :param registry:
        :param kwargs:
        :return:
        """
        self._registry         = utils.validate_uri(registry)
        self._registry_version = registry_version
        self._ssl_cert_path    = kwargs.get('ssl_cert_path', None)
        self._config_path      = os.path.join(os.environ.get('HOME'), '.dockercfg')
        self.user              = None
        self.passwd            = None
        self.auth_type         = kwargs.get('type')
        self.address           = kwargs.get('address', None)
        self.verify            = kwargs.get('verify', False)

    def clean_up(self):
        """
        :return:
        """
        if self.auth_type == 'registry_rubber' and self.user:
            self._registry_rubber_uonce('delete')

        # clean up old docker configs.
        user_home = os.environ.get('HOME')
        for file_name in os.listdir(user_home):
            if 'dockercfg' in file_name:
                if file_name.count('.') is 2:
                    try:
                        parts = file_name.split('.')
                        delta = int(time.time()) - int(parts[1])

                        # default to 30 seconds?
                        if delta > 30:
                            os.remove(os.path.realpath(os.path.join(user_home, file_name)))
                    except Exception:
                        pass

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, value):
        if value is None:
            self._address = None
        else:
            self._address = utils.validate_uri(value)

    @property
    def auth_type(self):
        return self._auth_type

    @auth_type.setter
    def auth_type(self, value):
        if isinstance(value, six.string_types):
            if value not in AUTH_TYPES and value is not None:
                raise ValueError("auth_type must be one of the following values: {0}, None.".format(', '.join(AUTH_TYPES)))
        else:
            raise LookupError("auth_type must be a string. {0} was passed.".format(value))

        self._auth_type = value

    @property
    def config_path(self):
        return self._config_path

    @property
    def registry(self):
        return self._registry

    @property
    def registry_version(self):
        return self._registry_version

    @property
    def ssl_cert_path(self):
        return self._ssl_cert_path

    @property
    def verify(self):
        return self._verify

    @verify.setter
    def verify(self, value):
        if not isinstance(value, bool):
            raise TypeError("verify must be bool. {0} was passed.".format(value))

        self._verify = value

    ##
    # public methods
    ##
    def load_dockercfg(self):
        """
        :return:
        """
        if self.ssl_cert_path:
            self._validate_ssl_certs()

        if self.auth_type == 'registry_rubber':
            self.user, self.passwd = self._registry_rubber_uonce('add')
            self._config_path = self._create_dockercfg(
                self.user,
                self.passwd,
                os.path.join(os.environ.get('HOME'), '.{0}.dockercfg'.format(self.user))
            )
        else:
            if not os.path.isfile(self.config_path):
                raise ValueError("Couldn't find dockercfg file: {0}".format(self.config_path))

            with open(self.config_path, 'r') as f:
                try:
                    config = json.loads(f.read())
                except Exception:
                    raise SyntaxError("{0} doesn't container valid json.".format(self.config_path))

            if self.registry not in config:
                raise LookupError("Was unable to find {0} in {1}".format(self.registry, self.config_path))

            registry_config = config[self.registry]
            if 'auth' not in registry_config:
                raise LookupError("Was unable to find 'auth' obj for {0} in {1}".format(self.registry, self.config_path))

            credentials = base64.decodestring(registry_config['auth'])

            self.user = credentials.get('user')
            self.user = credentials.get('password')

    ##
    # private methods
    ##
    @utils.retry
    def _registry_rubber_uonce(self, action):
        if not isinstance(action, six.string_types):
            raise TypeError("action must be a string. {0} was passed.".format(action))

        user   = "{0}".format(int(time.time()))
        passwd = six.text_type(uuid.uuid4()).replace('-', '')

        params = {"user": user, "passwd": passwd}

        url = "{0}/dregister_users/{1}".format(self.address, action)

        if self.ssl_cert_path:
            certs = (os.path.join(self.ssl_cert_path, 'cert.pem'), os.path.join(self.ssl_cert_path, 'key.pem'))
            response = requests.get(url, params=params, cert=certs, verify=self.verify)
        else:
            response = requests.get(url, params=params)

        if response.ok:
            return user, passwd
        else:
            raise LookupError("Was unable to create new user with registry rubber: {0}".format(url))

    # TODO: need to make this python three compatible.
    def _create_dockercfg(self, user, passwd, config_path, email=""):
        registry     = "{0}/{1}/".format(self.registry, self.registry_version)
        encoded_data = base64.encodestring("{0}:{1}".format(user, passwd).encode()).decode().strip()
        config       = {}

        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                try:
                    config = json.loads(f.read())
                except Exception:
                    raise SyntaxError("{0} doesn't container valid json.".format(self.config_path))

        config[registry] = {
            "auth": encoded_data,
            "email": email
        }

        with open(config_path, 'w') as f:
            f.write(json.dumps(config))

        return config_path

    def _validate_ssl_certs(self):
        """

        :return:
        """
        if not os.path.exists(self.ssl_cert_path):
            raise LookupError("ssl_cert_path '{0}' don't exist".format(self.ssl_cert_path))

        for file_name in ('key', 'cert', 'ca'):
            path_to_file = os.path.join(self.ssl_cert_path, '{0}.pem'.format(file_name))
            if not os.path.isfile(path_to_file):
                raise LookupError("ssl_cert_path: was unable to find {0}.".format(path_to_file))
