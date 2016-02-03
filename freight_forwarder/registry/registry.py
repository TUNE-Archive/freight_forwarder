# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import json

import six

from freight_forwarder.utils import logger
from .registry_base          import RegistryBase
from .exceptions             import RegistryException


def Registry(address='https://index.docker.io', **kwargs):
    """
    :return:
    """
    registry = None
    try:
        try:
            registry = V1(address, **kwargs)
            registry.ping()
        except RegistryException:
            registry = V2(address, **kwargs)
            registry.ping()
    except OSError:
        logger.warning(
            'Was unable to verify certs for a registry @ {0}. '
            'Will not be able to interact with it for any operations until the certs can be validated.'.format(address)
        )

    return registry


class V1(RegistryBase):

    def __init__(self, address='https://index.docker.io', **kwargs):
        super(V1, self).__init__('v1', address, **kwargs)

    def ping(self):
        return self._validate_response(self._request_builder('GET', '_ping'))

    def search(self, terms):
        """
        returns a dict {"name":  "image_dict"}
        """
        images   = {}
        response = self._request_builder('GET', 'search', params={'q': terms})

        if self._validate_response(response):
            body = json.loads(response.content.decode('utf-8'))['results']
            for image in body:
                images[image['name']] = image

        return images

    def tags(self, image_name):
        if not isinstance(image_name, six.string_types):
            raise TypeError('image_name must be a str. {0} was passed.'.format(type(image_name).__name__))

        if '/' not in image_name:
            raise AttributeError(
                'image_name must be in the following format: \"namespace/repository\". {0} was passed.'.format(image_name)
            )

        tags = {}
        response = self._request_builder('GET', 'repositories/{0}/tags'.format(image_name))

        if self._validate_response(response):
            tags = json.loads(response.content.decode('utf-8'))

        for tag in tags:
            if isinstance(tag, dict):
                tag = tag.get('name')

            yield '{0}:{1}'.format(image_name, tag)

    def delete_tag(self, name_space, repository, tag):
        verb = 'DELETE'
        path = 'repositories/{0}/{1}/tags/{2}'.format(name_space, repository, tag)
        response = self._request_builder(verb, path)

        return self._validate_response(response)

    def delete(self, name_space, repository):
        verb = 'DELETE'
        path = 'repositories/%s/%s' % (name_space, repository)

        response = self._request_builder(verb, path)

        return self._validate_response(response)

    def get_image_by_id(self, id):
        if not isinstance(id, six.string_types):
            # add regex to check for uuid
            raise Exception("id has to be a string")

        verb = 'GET'
        path = 'images/{0}/json'.format(id)
        response = self._request_builder(verb, path)

        if self._validate_response(response):
            image = json.loads(response.content)
        # TODO: create image object.

        return image

    def get_image_id_by_tag(self, name_space, repository, tag):
        verb = 'GET'
        path = 'repositories/{0}/{1}/tags/{2}'.format(name_space, repository, tag)
        id = None

        response = self._request_builder(verb, path)
        if self._validate_response(response):
            id = response.content

        return id

    def set_image_tag(self, name_space, repository, tag, id):
        verb = 'PUT'
        path = 'repositories/{0}/{1}/tags/{2}'.format(name_space, repository, tag)
        response = self._request_builder(verb, path, body=json.dumps(id))

        return self._validate_response(response)


class V2(RegistryBase):

    def __init__(self, address='https://index.docker.io', **kwargs):
        super(V2, self).__init__('v2', address, **kwargs)

    def blobs(self):
        pass

    def catalog(self, count=None, last=None):
        pass

    def manifests(self):
        pass

    def ping(self):
        return self._validate_response(response=self._request_builder('GET', ''))

    def search(self, terms):
        """

        :param namespace:
        :param repository:
        :return:
        """
        verb            = 'GET'
        path            = '_catalog'

        response = self._request_builder(verb, path)
        if self._validate_response(response):
            body = json.loads(response.content.decode('utf-8'))
            if 'repositories' in body:

                for repository_name in body['repositories']:
                    if terms is None:
                        break

                    elif terms in repository_name:
                        yield repository_name

    def tags(self, image_name):
        if not isinstance(image_name, six.string_types):
            raise TypeError('image_name must be a str. {0} was passed.'.format(type(image_name).__name__))

        if '/' not in image_name:
            raise AttributeError(
                'image_name must be in the following format: \"namespace/repository\". {0} was passed.'.format(image_name)
            )

        response = self._request_builder('GET', '{0}/tags/list'.format(image_name))
        if self._validate_response(response):
            response = json.loads(response.content.decode('utf-8'))

        for tag in response.get('tags'):
            yield '{0}:{1}'.format(image_name, tag)
