# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
import six
import os

from freight_forwarder.image                 import Image
from freight_forwarder.registry              import Registry, V1, V2
from freight_forwarder.container.host_config import HostConfig
from freight_forwarder.container.config      import Config as ContainerConfig
from freight_forwarder.utils                 import logger
from .container_dict                         import ContainerDict


class Service(object):
    def __init__(self, repository, namespace, name, alias, container_config=None, docker_file=None, host_config=None,
                 source_registry=None, destination_registry=None, source_tag=None, test_docker_file=None):
        """
         EXPLAIN ME!
        """
        if not isinstance(name, six.string_types):
            raise TypeError("name needs to be a string")

        if not isinstance(namespace, six.string_types):
            raise TypeError("namespace needs to be a string")

        if not isinstance(repository, six.string_types):
            raise TypeError("repository needs to be a string")

        if not isinstance(alias, six.string_types):
            raise TypeError("alias needs to be a string")

        self._alias = alias

        tag = None
        if ":" in namespace:
            namespace, tag = namespace.split(':')

        if source_tag:
            self.source_tag = source_tag
        elif tag:
            self.source_tag = tag
        else:
            self.source_tag = 'latest'

        self._name       = name
        self._namespace  = namespace
        self._repository = repository
        self._cargo      = None
        self._containers = ContainerDict()

        # TODO: update both dependencies and dependents with something similar to container dict
        self._dependencies = {}
        self._dependents   = {}

        self.docker_file      = docker_file
        self.test_docker_file = test_docker_file

        # Source registry will be the default registry is source registry is None and there isn't a Dockerfile
        if source_registry is None and not self.docker_file:
            self.source_registry = Registry()
        else:
            self.source_registry = source_registry

        # Destination Registry will be assigned to source_registry if value is None
        if destination_registry is None and self.source_registry:
            self.destination_registry = self.source_registry
        else:
            self.destination_registry = destination_registry

        self.container_config = container_config
        self.host_config      = host_config

    ##
    # properties
    ##
    @property
    def alias(self):
        return self._alias

    @property
    def cargo(self):
        return self._cargo

    @cargo.setter
    def cargo(self, value):
        if not isinstance(value, Image):
            raise Exception("Cargo must be an instance of an Image")

        self._cargo = value

    @property
    def containers(self):
        return self._containers

    @property
    def container_config(self):
        return self._container_config

    @container_config.setter
    def container_config(self, value):
        if value is None:
            self._container_config = ContainerConfig()
        else:
            if isinstance(value, ContainerConfig):
                self._container_config = value
            else:
                raise TypeError("container_config must be and instance of ContainerConfig.")

    @property
    def dependencies(self):
        return self._dependencies

    @property
    def dependents(self):
        return self._dependents

    @property
    def docker_file(self):
        return self._docker_file

    @docker_file.setter
    def docker_file(self, value):
        self._docker_file = self.__get_valid_docker_file_path(value)

    @property
    def destination_registry(self):
        return self._destination_registry

    @destination_registry.setter
    def destination_registry(self, value):
        if value is None:
            self._destination_registry = None
        else:
            if not isinstance(value, (V1, V2)):
                raise TypeError("destination_registry must of of type Registry")

            self._destination_registry = value

    @property
    def test_docker_file(self):
        return self._test_docker_file

    @test_docker_file.setter
    def test_docker_file(self, value):
        self._test_docker_file = self.__get_valid_docker_file_path(value)

    @property
    def host_config(self):
        return self._host_config

    @host_config.setter
    def host_config(self, value):
        if value is None:
            self._host_config = HostConfig()
        else:
            if isinstance(value, HostConfig):
                self._host_config = value
            else:
                raise TypeError("host_config must be and instance of HostConfig.")

    @property
    def name(self):
        return self._name

    @property
    def namespace(self):
        return self._namespace

    @property
    def repository(self):
        return self._repository

    @property
    def source_registry(self):
        return self._source_registry

    @source_registry.setter
    def source_registry(self, value):
        if value is None:
            self._source_registry = None
        else:
            if not isinstance(value, (V1, V2)):
                raise TypeError("source_registry must of of type Registry")

            self._source_registry = value

    @property
    def source_tag(self):
        return self._source_tag

    @source_tag.setter
    def source_tag(self, value):
        if not isinstance(value, six.string_types):
            raise TypeError(logger.error("source_tag must be a string."))

        self._source_tag = value

    ##
    # public methods
    ##
    def configure_dependencies(self, services):
        """
        """
        if not isinstance(services, dict):
            raise TypeError("services must be a dict.")

        # configure service dependents
        self.__configure_dependents(services)

        for volume in self.host_config.volumes_from:
            # TODO: need to look into adding permissions back?
            if ':' in volume:
                volume, permission = volume.split(':')

            if volume == self.name:
                raise ReferenceError("Can not use itself inside volumes_from.")

            if volume in services:
                self._dependencies[volume] = services[volume]

        # TODO: need to validate link here if its not part of a service.
        for link in self.host_config.links:
            if link == self.name:
                raise ReferenceError("Can not link to itself.")

            if link in services:
                self._dependencies[link] = services[link]
            else:
                if link.count(':') != 1:
                    raise ReferenceError("When adding links that aren't defined as Services in the configuration file "
                                         "they must be in the following format `name:alias`.  "
                                         "{0} is not valid.".format(link))

    ##
    # private methods
    ##
    def __configure_dependents(self, services):
        if not isinstance(services, dict):
            raise TypeError("services must be a dict.")

        if services:
            for name, service in six.iteritems(services):
                if not isinstance(service, Service):
                    raise TypeError("{0} must be a Dependency or Application not: {1}".format(name, type(service)))

                elif self.name in service.host_config.volumes_from and service.name in self._host_config.volumes_from:
                    raise ReferenceError("Circular volume_from reference between {0} and {1}".format(self.alias, name))

                elif self.name in service.host_config.links and service.name in self._host_config.links:
                    raise ReferenceError("Circular link reference between {0} and {1}".format(self.alias, name))

                if self.name in service.host_config.links:
                    self._dependents[service.name] = service

                if service.host_config.volumes_from:
                    for volume_from in service.host_config.volumes_from:
                        if self.name in volume_from:
                            self._dependents[service.name] = service

    def __get_valid_docker_file_path(self, file_path):
        if file_path is None:
            return None
        elif not isinstance(file_path, six.string_types):
            raise TypeError("Dockerfile path must be a str.")

        elif not os.path.exists(file_path):
            raise OSError("Dockerfile path doesn't exist: {0}".format(file_path))

        else:
            return os.path.abspath(file_path)
