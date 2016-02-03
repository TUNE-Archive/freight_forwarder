# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import abc
import os
from weakref import WeakValueDictionary

import requests
from requests.packages import urllib3
from six               import add_metaclass

from freight_forwarder import utils
from .auth             import Auth
from .exceptions       import RegistryException


@add_metaclass(abc.ABCMeta)
class RegistryBase(object):
    _instances = WeakValueDictionary()

    ##
    # abstract methods
    ##
    @abc.abstractmethod
    def ping(self):
        pass

    @abc.abstractmethod
    def search(self, term):
        pass

    @abc.abstractmethod
    def tags(self, image_name):
        pass

    ##
    # magic methods
    ##
    def __init__(self, version, address='https://index.docker.io', **kwargs):
        urllib3.disable_warnings()
        self._instances[id(self)] = self
        self.scheme       = utils.parse_http_scheme(address)
        self.location     = utils.parse_hostname(address)
        self._api_version = version
        self._tls         = {}

        if kwargs.get('ssl_cert_path'):
            self.tls = kwargs['ssl_cert_path']

        # prepare session
        self.session = requests.Session()

        # set up certs.
        self.session.verify = self.tls.get('ca_path', kwargs.get('verify', True))
        self.session.cert = (self.tls['ssl_cert_path'], self.tls['ssl_key_path']) if self.tls else None
        self.auth = kwargs.get('authentication', kwargs.get('auth', None))
        if self.auth:
            self.session.auth = (self.auth.user, self.auth.passwd)

    def __str__(self):
        return "{0}{1}".format(self.scheme, self.location)

    def __del__(self):
        """
        :return:
        """
        if id(self) in self._instances:
            if hasattr(self, 'session'):
                self.session.close()

            if hasattr(self, '_auth'):
                if self._auth:
                    self._auth.clean_up()

    ##
    # Properties
    ##
    @property
    def auth(self):
        return self._auth

    @auth.setter
    def auth(self, value):
        if value is None:
            self._auth = None
            return

        elif not isinstance(value, dict):
            raise TypeError("auth must be a dict or None. {0} was passed.".format(value))

        self._auth = Auth("{0}{1}".format(self.scheme, self.location), self.api_version, **value)

    @property
    def api_version(self):
        return self._api_version

    @property
    def tls(self):
        return self._tls

    @tls.setter
    def tls(self, path):
        if not os.path.exists(path):
            raise OSError("ssl_cert_path '{0}' don't exist".format(path))

        for file_name in ('key', 'cert', 'ca'):
            path_to_file = os.path.join(path, '{0}.pem'.format(file_name))
            if not os.path.isfile(path_to_file):
                raise OSError("ssl_cert_path: was unable to find {0}.".format(path_to_file))

        self._tls = {
            "ssl_cert_path": os.path.join(path, 'cert.pem'),
            "ssl_key_path": os.path.join(path, 'key.pem'),
            "ca_path": os.path.join(path, 'ca.pem')
        }

    ##
    # protected methods
    ##
    def _validate_certs(self, ssl_cert_path, ssl_key_path):
        if ssl_cert_path is None:
            raise Exception("When validating ssl cert it can't be None.")
        else:
            if not os.path.exists(ssl_cert_path):
                raise LookupError("ssl_cert_path '{0}' don't exist".format(ssl_cert_path))

            self.auth['ssl_cert_path'] = ssl_cert_path

        if ssl_key_path is None:
            raise Exception("When validating ssl key it can't be None.")
        else:
            if not os.path.exists(ssl_key_path):
                raise LookupError("ssl_key_path '{0}' don't exist".format(ssl_key_path))

        return ssl_cert_path, ssl_key_path

    @utils.retry
    def _request_builder(self, verb, path, body={}, headers={}, params={}):
        url = "{0}{1}/{2}/{3}".format(self.scheme, self.location, self.api_version, path)

        headers_values = headers if headers else {'Accept': 'application/json', 'Content-Type': 'application/json'}
        verb = verb.upper()

        try:
            if verb in ('PUT', 'PATCH', 'POST'):
                response = self.session.request(verb, url, data=body, headers=headers_values, params=params)
            else:
                response = self.session.request(verb, url, headers=headers_values, params=params)
        except requests.ConnectionError:
            # TODO: need up raise more Registry specific exceptions
            raise

        return response

    def _validate_response(self, response):
        if not isinstance(response, requests.Response):
            raise TypeError("validate response requires the response argument to be a requests.Response object.")

        if hasattr(response, 'status_code') and not (response.status_code >= 200 and response.status_code < 300):
            raise RegistryException(response)

        return response.ok
