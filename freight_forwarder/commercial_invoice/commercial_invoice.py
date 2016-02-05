# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
import os
import time
import six

from ..container.config      import Config as ContainerConfig
from ..container.host_config import HostConfig
from ..registry              import Registry
from .service                import Service
from .injector               import Injector
from ..container_ship        import ContainerShip
from ..utils                 import logger
from ..const import (
    PROJECT_LABEL,
    TEAM_LABEL,
    VERSION_LABEL,
    GIT_LABEL,
    TYPE_LABEL,
    TIMESTAMP_LABEL
)


class CommercialInvoice(object):
    def __init__(self, team, project, services, hosts, transport_service, transport_method, environment=None,
                 data_center=None, registries=None, tags=[], tagging_scheme=None):
        """
        """
        if not isinstance(services, dict):
            raise TypeError(logger.error("services must be a dict."))

        if hosts and not isinstance(hosts, dict):
            raise TypeError(logger.error("hosts must be a dict."))

        self._container_ships  = self._create_container_ships(hosts)
        self._team             = team
        self._project          = project
        self._transport_method = transport_method

        if data_center is not None and not isinstance(data_center, six.string_types):
            raise TypeError(logger.error("environment must be a string"))
        self._data_center = data_center

        if environment is not None and not isinstance(environment, six.string_types):
            raise TypeError(logger.error("environment must be a string"))
        self._environment       = environment

        self._registries        = self._create_registries(registries)
        self._tagging_scheme    = tagging_scheme if tagging_scheme is not None else True
        self._tags              = self._build_tags(tags) if tags else []
        self._services          = services
        self._transport_service = transport_service

    @property
    def injector(self):
        registry = self._registries['injector'] if self._registries.get('injector') else self._registries.get('default')

        return Injector(self._environment, self._data_center, self._project, registry)

    # TODO: come back and revisit once ff config is done.  Kind of strange we don't keep state.  Maybe hold service data per container ship
    @property
    def services(self):
        return self._create_services(self._services)

    @property
    def transport_service(self):
        return self.services.get(self._transport_service)

    @property
    def transport_method(self):
        return self._transport_method

    @property
    def data_center(self):
        return self._data_center

    @property
    def environment(self):
        return self._environment

    @property
    def container_ships(self):
        return self._container_ships

    @property
    def project(self):
        return self._project

    @property
    def team(self):
        return self._team

    @property
    def test(self):
        return self._test

    @test.setter
    def test(self, value):
        if not isinstance(value, bool):
            raise TypeError(logger.error("test must be a bool."))

        self._test = value

    @property
    def tags(self):
        return self._tags

    @tags.setter
    def tags(self, value):
        self._tags = self._build_tags(value)

    @property
    def registries(self):
        return self._registries

    ##
    # Private Methods
    ##
    def _create_labels(self, name, service):
        labels = {
            PROJECT_LABEL: self.project,
            TEAM_LABEL: self.team,
            VERSION_LABEL: "place_holder",
            GIT_LABEL: "place_holder",
            TYPE_LABEL: name,
            TIMESTAMP_LABEL: "{0}".format(int(time.time()))
        }

        current_labels = service.get('labels')

        if current_labels:
            if not isinstance(current_labels, dict):
                raise TypeError(logger.error("labels must be a dict."))

            labels.update(current_labels)

        return labels

    def _build_tags(self, tags):
        """
        """
        tags = tags if isinstance(tags, list) else [tags]

        for tag in tags:
            if not isinstance(tag, six.string_types):
                raise TypeError("tags must be a list of a string")

        if self._tagging_scheme:
            if self._data_center and self._environment:
                self._tag_prefix = "{0}-{1}".format(self._data_center, self._environment)
            elif self._environment:
                self._tag_prefix = self._environment
            elif self._data_center:
                self._tag_prefix = self._data_center
            else:
                self._tag_prefix = None

            if tags and self._tag_prefix:
                tags = ["{0}-{1}".format(self._tag_prefix, tag) for tag in tags]

        return tags

    def _create_registries(self, registries_meta):
        """
        """
        registries = {'docker_hub': Registry()}

        if registries_meta is None:
            logger.warning("There were no registries defined. Defaulting to Docker hub.")
            return registries
        elif isinstance(registries_meta, dict):
            registries.update({alias: Registry(**registry) for alias, registry in six.iteritems(registries_meta)})
        else:
            raise TypeError(logger.error("registries must be a dict"))

        if 'default' not in registries:
            registries['default'] = registries['docker_hub']
            logger.warning("There was not default registry defined. Default will be Docker hub.")

        return registries

    def _create_container_ships(self, hosts):
        """
        :param hosts:
        :return:
        """
        container_ships = {}

        if hosts:
            if 'default' not in hosts:
                default_container_ship     = self._create_container_ship(None)
                container_ships['default'] = {default_container_ship.url.geturl(): default_container_ship}

            for alias, hosts in six.iteritems(hosts):
                if hosts is None:
                    container_ships[alias] = hosts
                elif isinstance(hosts, list):
                    container_ships[alias] = {}

                    for host in hosts:
                        if not host or not isinstance(host, dict):
                            raise ValueError("hosts: {0} is required to be a dict.".format(alias))

                        existing_container_ship = None

                        for container_ship_dict in six.itervalues(container_ships):

                            for address, container_ship in six.iteritems(container_ship_dict):
                                if address == host.get('address') and address not in container_ships[alias]:
                                    existing_container_ship = container_ship
                                    break

                        if existing_container_ship is None:
                            container_ships[alias][host.get('address')] = self._create_container_ship(host)
                        else:
                            container_ships[alias][host.get('address')] = existing_container_ship
                else:
                    raise ValueError(logger.error("hosts is required to be a list or None. host: {0}".format(hosts)))

        else:
            default_container_ship     = self._create_container_ship(None)
            container_ships['default'] = {default_container_ship.url.geturl(): default_container_ship}

        return container_ships

    def _create_container_ship(self, host_data=None):
        """
            # docker env vars. We use them if nothing is supplied.
            DOCKER_HOST=fqdn:port
            DOCKER_TLS_VERIFY=false
            DOCKER_CERT_PATH=/path/
        """
        if not host_data:
            host_data = {}
            path = os.getenv('DOCKER_CERT_PATH')
            host_data['address'] = os.getenv('DOCKER_HOST')

            if not host_data:
                raise LookupError(
                    logger.error("Unable to find docker ENV var: DOCKER_HOST, DOCKER_CERT_PATH, and DOCKER_TLS_VERIFY are required.")
                )

            if not host_data.get('address'):
                raise LookupError(logger.error("Unable to find a value for DOCKER_HOST."))

            if 'tcp://' in host_data['address']:
                host_data['address'] = host_data['address'].replace('tcp://', 'https://')

            host_data['ssl_cert_path'] = os.path.realpath(path)
            host_data['verify']        = os.getenv('DOCKER_TLS_VERIFY')

            if host_data['verify'] == 'yes':
                host_data['verify'] = True
            elif host_data['verify'] == 'no':
                host_data['verify'] = False

        return ContainerShip(
            host_data.get('address'),
            services=host_data.get('services'),
            ssl_cert_path=host_data.get('ssl_cert_path'),
            verify=host_data.get('verify')
        )

    def _configure_service_dependencies(self, services):
        """
        """
        if not isinstance(services, dict):
            raise AttributeError("services is required to be a dict")

        for name, service in six.iteritems(services):
            if not isinstance(service, Service):
                raise AttributeError("{0} must be a Service.".format(name))

        for service in six.itervalues(services):
            reduced_services = services.copy()
            try:
                del reduced_services[service.name]
            except KeyError:
                pass

            service.configure_dependencies(reduced_services)

    def _create_service(self, name, service):
        if not isinstance(service, dict):
            raise TypeError(logger.error("service must be a dict."))

        if not service:
            raise ValueError(logger.error("When defining a service it must have items."))

        service['labels'] = self._create_labels(name, service)
        source_registry   = None
        docker_file       = None
        namespace         = "{0}-{1}".format(self._project, name)
        repository        = None

        if service.get('image'):
            if not isinstance(service['image'], six.string_types):
                raise TypeError(logger.error("When an image is supplied the value must be a string."))

            chunks          = service['image'].split('/')
            length          = len(chunks)
            source_registry = None

            # TODO: update so shipping port is address from image if not use default
            if length > 2:
                registry_alias, repository, namespace = chunks
                if registry_alias not in self.registries:
                    raise LookupError(
                        logger.error("Unable to find {0} in the default or provided registries.".format(registry_alias))
                    )

                source_registry = self.registries[registry_alias]

            elif length > 1:
                repository, namespace = chunks
            else:
                # TODO: update to support defaults etc.
                namespace = chunks[0]

        elif service.get('build'):
            repository = self._team
            docker_file = service['build']
        else:
            raise KeyError("each service must have a either a build or image property.")

        destination_registry = self.registries.get(service.get('export_to', 'default'))

        return Service(
            repository,
            namespace,
            name,
            "{0}-{1}-{2}".format(self.team, self.project, service.alias),
            container_config=ContainerConfig(service),
            host_config=HostConfig(service),
            docker_file=docker_file,
            test_docker_file=service.get('test'),
            source_registry=source_registry,
            destination_registry=destination_registry
        )

    def _create_services(self, service_data):
        services = {}

        for service in six.itervalues(service_data):
            if isinstance(service, dict):
                services[service.alias] = self._create_service(service.alias, service)

        self._configure_service_dependencies(services)

        return services
