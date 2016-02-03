# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import os
import copy
import re

import docker
import six
from six.moves.urllib.parse import urlparse
from requests.packages      import urllib3

from .const                       import DOCKER_API_VERSION, DOCKER_DEFAULT_TIMEOUT
from .container                   import Container
from .commercial_invoice.injector import Injector
from .commercial_invoice.service  import Service
from .image                       import Image
from .utils                       import utils, logger


class ContainerShip(object):
    def __init__(self, address, **kwargs):
        """
        explain me ; )

        """
        utils.validate_uri(address)
        # TODO: update me with a config file entry need to update to get the version from docker and use that.
        self.API_VERSION = DOCKER_API_VERSION
        self.url         = urlparse(address)

        if self.url.scheme == 'https':
            # TODO: Need to allow for ca to be passed if not disable warnings.
            urllib3.disable_warnings()

            for cert_name_type in ('ca', 'cert', 'key'):
                cert_path = utils.validate_path(os.path.join(kwargs['ssl_cert_path'], "{0}.pem".format(cert_name_type))) \
                    if 'ssl_cert_path' in kwargs and kwargs['ssl_cert_path'] else None
                setattr(self, 'SSL_{0}_PATH'.format(cert_name_type.upper()), cert_path)

            self.SSL_VERIFY = kwargs['verify'] if 'verify' in kwargs and isinstance(kwargs['verify'], bool) else True

            if not self.SSL_VERIFY:
                self.SSL_CA_PATH = None

            client_certs = (self.SSL_CERT_PATH, self.SSL_KEY_PATH) if self.SSL_KEY_PATH and self.SSL_CERT_PATH else None
            tls_config   = docker.tls.TLSConfig(client_cert=client_certs, ca_cert=self.SSL_CA_PATH, verify=self.SSL_VERIFY)

            self._client_session = docker.Client(self.url.geturl(), tls=tls_config, timeout=DOCKER_DEFAULT_TIMEOUT, version=self.API_VERSION)
        else:
            self._client_session = docker.Client(self.url.geturl(), timeout=DOCKER_DEFAULT_TIMEOUT, version=self.API_VERSION)

        self._docker_info = self._client_session.version()
        self._injector = None

    @property
    def injector(self):
        return self._injector

    @injector.setter
    def injector(self, value):
        if not isinstance(value, Injector):
            raise TypeError(logger.error("injector must be an instance of Injector."))

        self._injector = value

    def report(self):
        logger.info("Container Ship: {0}".format(self.url.geturl()))
        logger.info("docker-py: {0}".format(docker.version))
        logger.info("Docker Api: {0}".format(self.API_VERSION))
        logger.info("Docker Daemon:")
        for key, value in six.iteritems(self._docker_info):
            logger.info("\t {0}: {1}".format(key, value))

        logger.info("Reporting for Dispatch.")

    def healthy(self):
        # TODO: write code?
        return self._client_session.ping()

    def inspect(self):
        # TODO: build object out of returned data.
        return self._client_session.info()

    def manifest(self):
        # TODO get a list of all containers and cargo
        pass

    def recall_service(self, service):
        """
        This method assumes that its a roll back during a deployment.  If not used during a deployment session

        This method should be extended later to be more useful.
        """
        if not isinstance(service, Service):
            raise TypeError("service must be of type Service.")

        logger.warning("The deployment for {0} on {1} failed starting the rollback.".format(service.alias, self.url.geturl()))

        def anonymous(anonymous_service):
            if not isinstance(anonymous_service, Service):
                raise TypeError("service must be an instance of Service.")

            containers = self.find_previous_service_containers(anonymous_service)
            if containers:
                for name in list(anonymous_service.containers.keys()):
                    del anonymous_service.containers[name]

                anonymous_service.cargo.delete()

                for name, container in six.iteritems(containers):
                    # TODO: add function to container obj to see if its running.
                    if container.state().get('running'):
                        logger.info(
                            "is already running... Might want to investigate.",
                            extra={'formatter': 'container', 'container': container.name}
                        )
                    else:
                        if container.start():
                            logger.info(
                                "is restarted and healthy.",
                                extra={'formatter': 'container', 'container': container.name}
                            )
                        else:
                            logger.error(
                                "failed to start.",
                                extra={'formatter': 'container', 'container': container.name}
                            )

                            container.dump_logs()
                            raise Exception(
                                "The deployment for {0} on {1} went horribly wrong".format(container.name, self.url.geturl())
                            )

        self._service_map(service, anonymous, descending=False)

    def containers(self):
        self._client_session.containers(all=1)

    def load_containers(self, service, configs, use_cache):
        """
        :param service_name:
        :return None:
        """
        if not isinstance(service, Service):
            raise TypeError("service must be and instance of service.  {0} was passed.".format(service))

        if not self.healthy():
            logger.error("unable to connect to container ship.")
            raise Exception('lost comms with our container ship')

        self._load_service_containers(service, configs, use_cache)

    def cargoes(self):
        return Image.all(self._client_session)

    def clean_up_dangling_images(self):
        """
        Clean up all dangling images.
        """
        cargoes = Image.all(client=self._client_session, filters={'dangling': True})
        for id, cargo in six.iteritems(cargoes):
            logger.info("Removing dangling image: {0}".format(id))
            cargo.delete()

    def export(self, service, tags=[]):
        """
        """
        # TODO: need finalize export process.
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service.")

        if not service.cargo:
            raise ValueError("Couldn't export Service: {0} image because one wasn't provided.".format(service.name))

        if service.destination_registry.auth:
            self._request_auth(service.destination_registry)

        if not service.destination_registry.ping():
            raise Exception("Was unable to locate registry: {0}".format(service.destination_registry.location))

        logger.info(
            "Exporting image {0} to {1}.".format(service.cargo.identifier, service.destination_registry.location)
        )

        # TODO: just add team name to the service... good god. need to review this.... still kind of jacked up
        chunks = service.alias.split('-')
        repository_tag = "{0}/{1}".format(chunks.pop(0), '-'.join(chunks))

        # During an export if you pass a command override we assume you want to make changes to your image.
        # This needs to be revisit this to make more solid at a later date.
        if service.containers.first and service.containers.first.config.cmd:
            service.cargo = Image(
                self._client_session,
                service.containers.first.commit(service.containers.first.config.to_dict(), repository_tag, "latest")
            )

        if tags:
            service.cargo.tag("{0}/{1}".format(service.destination_registry.location, repository_tag), tags)

        response = service.cargo.push(service.destination_registry, repository_tag)

        return True if not response else False

    def find_service_containers(self, service):
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service")

        # find all running containers that include basename
        results = Container.find_by_name(self._client_session, "{0}".format(service.alias))
        current_containers = {}
        application_regex = re.compile(r'\A%s-\d{2,3}' % service.alias, flags=re.IGNORECASE)

        # if we find containers
        if results:
            for container in six.itervalues(results):
                if application_regex.match(container.name):
                    current_containers[container.name] = container

        return current_containers

    def find_previous_service_containers(self, service):
        previous_containers = {}
        results = self.find_service_containers(service)

        if results:
            for container in six.itervalues(results):
                if container.name not in service.containers:
                    previous_containers[container.name] = container
                    continue

        return previous_containers

    def load_cargo(self, service, inject_configs=None, use_cache=False):
        if not isinstance(service, Service):
            raise TypeError("service must be and instance of service.  {0} was passed.".format(service))

        if not self.healthy():
            logger.error("unable to connect to container ship.")
            raise Exception('lost comms with our container ship')

        self._load_service_cargo(service, inject_configs, use_cache)

    def offload_project(self, team, project):
        """

        :param team:
        :param project:
        :return:
        """
        containers = Container.find_by_name(self._client_session, "{0}-{1}".format(team, project))
        if containers:
            logger.info("Deleting all team: {0} project: {1} containers.".format(team, project))
            for container in six.itervalues(containers):
                container.delete()
                Image(self._client_session, container.image).delete()

        image_name = "{0}/{1}".format(team, project)
        cargoes = Image.find_all_by_name(self._client_session, image_name)

        if cargoes:
            logger.info("deleting all {0} images.".format(image_name))
            for id, image in six.iteritems(cargoes):
                image.delete(force=True)

    def offload_service_cargo(self, service):

        def anonymous(anonymous_service):
            if not isinstance(anonymous_service, Service):
                raise TypeError("service must be an instance of Service.")

            if anonymous_service.cargo:
                logger.info("Offloading cargo for {}.".format(anonymous_service.alias))
                anonymous_service.cargo.delete(force=True)

        self._service_map(service, anonymous, descending=True)

    def offload_all_service_cargo(self, service):
        """Remove docker images for a specific service.  This method will call itself recursively for dependents and
         dependencies.

        :param service_name:
        :return None:
        """
        def anonymous(anonymous_service):
            if not isinstance(anonymous_service, Service):
                raise TypeError("service must be an instance of Service.")

            cargoes = Image.find_all_by_name(
                self._client_session,
                "{0}/{1}".format(anonymous_service.repository, anonymous_service.namespace)
            )

            if cargoes:
                logger.info("Offloading all images for {0}.".format(anonymous_service.alias))
                for cargo in six.itervalues(cargoes):
                    cargo.delete(force=True)

        self._service_map(service, anonymous, descending=True)

    def offload_expired_service_cargo(self, service):
        """Remove docker images for a specific service.  This method will call itself recursively for dependents and
         dependencies.

        :param service:
        :return None:
        """
        # TODO: move offload cargo logic to this method
        self._service_map(service, self._offload_cargo, descending=True)

    def offload_service_containers(self, service):
        """
        :param service:
        :return:
        """
        def anonymous(anonymous_service):
            if not isinstance(anonymous_service, Service):
                raise TypeError("service must be an instance of Service.")

            if anonymous_service.containers:
                logger.info("Deleting service: {0} containers.".format(anonymous_service.name))
                for container_name in list(anonymous_service.containers.keys()):
                    del anonymous_service.containers[container_name]

        self._service_map(service, anonymous, descending=True)

    def offload_all_service_containers(self, service):
        """Deletes all containers related to the service.
        """
        def anonymous(anonymous_service):
            if not isinstance(anonymous_service, Service):
                raise TypeError("service must be an instance of Service.")

            containers = self.find_service_containers(anonymous_service)
            if containers:
                logger.info("Deleting service: {0} containers.".format(anonymous_service.name))
                for container in six.itervalues(containers):
                    container.delete()

        self._service_map(service, anonymous, descending=True)

    def offload_previous_containers(self, service):

        def anonymous(anonymous_service):
            if not isinstance(anonymous_service, Service):
                raise TypeError("service must be an instance of Service.")

            containers = self.find_previous_service_containers(anonymous_service)

            if containers:
                for name, container in six.iteritems(containers):
                    # TODO: add function to container obj to see if its running.
                    if not container.state().get('running'):
                        container.delete()

        self._service_map(service, anonymous, descending=True)

    def start_service_containers(self, service, attach):
        """
        :param service:
        :return bool:
        """
        if not isinstance(service, Service):
            TypeError("Service must be a instance of Service.")

        if not service.containers:
            raise AttributeError("Must load containers before attempting to start them.")

        containers = self.find_service_containers(service)
        if containers:
            for name, container in six.iteritems(containers):
                # TODO: add function to container obj to see if its running.
                if container.state().get('running'):
                    container.stop()

        for name, container in six.iteritems(service.containers):
            if not container.start(attach=attach):
                logger.error("service container: {0} failed to start.".format(name))
                container.dump_logs()

                return False

        return True

    def test_service(self, service, configs):
        """
        Run test container attach to it then clean up when the test run is complete.
        """
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service.")

        if not service.test_docker_file:
            raise Exception("Must provide a test docker file to run tests.")

        container = None
        try:
            logger.info("Testing Service: {0}".format(service.name))
            # tag image to make sure it exists for tests
            parent_image_name = "{0}/{1}:latest".format(service.repository, service.namespace)

            if not Image.find_by_name(self._client_session, parent_image_name):
                logger.info(
                    "Couldn't find application image: {0}.  Attempting to create or pull.".format(parent_image_name)
                )

                self._load_service_cargo(service, configs, use_cache=False)

                if not service.cargo:
                    raise LookupError("Was unable to find a parent image: {0}".format(parent_image_name))

                service.cargo.tag(parent_image_name)

            # TODO: update for dynamic configs.
            repository_tag = "{0}/{1}-test".format(service.repository, service.namespace)
            image = Image.build(
                self._client_session,
                repository_tag,
                docker_file=service.test_docker_file,
                use_cache=False
            )
            container_name = self._container_registration("{0}-test".format(service.alias))

            # update config with any changes.
            self._update_container_host_config(service)

            # update container config for tests
            test_container_config        = copy.deepcopy(service.container_config)
            test_container_config.detach = True

            # update host config for tests
            test_container_host_config                   = copy.deepcopy(service.host_config)
            test_container_host_config.restart_policy    = None
            test_container_host_config.port_bindings     = None
            test_container_host_config.publish_all_ports = True

            container = Container(
                self._client_session,
                name=container_name,
                image=image.id,
                container_config=test_container_config.to_dict(),
                host_config=test_container_host_config.to_dict()
            )

            return container.start(attach=True)
        finally:
            if container is not None:
                container.delete(remove_volumes=True)

            results = Container.find_by_name(self._client_session, "{0}-test".format(service.alias))
            if results:
                for test_container in six.itervalues(results):
                    if not test_container.state().get('running'):
                        Image(test_container.image).delete()
                        test_container.delete(remove_volumes=True)

    ###
    # private methods
    ###
    def _service_map(self, service, callback, descending=False):
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service.")

        service_list = [service.dependents, service.dependencies]

        if descending:
            service_list.reverse()

        # going to leave this here until 100% sure everything works.
        # func = lambda dep: None if getattr(dep, 'marked', None) else self._service_map(dep, callback)
        def closure(dep):
            if dep:
                for service in dep:
                    if not getattr(service, 'marked', None):
                        self._service_map(service, callback)

        # set marked_for_deletion property to avoid infinite loop.
        setattr(service, 'marked', True)

        first_group = service_list.pop()
        if first_group:
            closure(first_group.values())

        callback(service)

        second_group = service_list.pop()
        if second_group:
            closure(second_group.values())

        delattr(service, 'marked')

    def _offload_cargo(self, service):
        """
        """
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service.")

        base_name = "{0}/{1}".format(service.repository, service.namespace)

        # TODO: update when we start using links
        cargoes = Image.find_all_by_name(self._client_session, base_name)

        # TODO when config is created this should become a parameter
        limit = 2
        while len(cargoes) > limit:
            expired_cargo  = None
            test_cargo_key = None

            for key, suspect_cargo in six.iteritems(cargoes):
                # TODO: move this logic into Image class
                if "{0}-test".format(base_name) in suspect_cargo.identifier:
                    test_cargo_key = key
                    break

                if expired_cargo is None:
                    expired_cargo = suspect_cargo
                    continue

                if suspect_cargo.created_at < expired_cargo.created_at:
                    expired_cargo = suspect_cargo

            if test_cargo_key is not None:
                del cargoes[test_cargo_key]

            elif expired_cargo is not None:
                expired_cargo.delete()
                del cargoes[expired_cargo.id]
        else:
            logger.info("Done offloading Cargo for {0}.".format(base_name))

    def _container_registration(self, alias):
        """
        Check for an available name and return that to the caller.
        """
        containers = Container.find_by_name(self._client_session, alias)

        def validate_name(name):
            valid = True
            if name in containers:
                valid = False

            return valid

        count = 1
        container_name = "{0}-0{1}".format(alias, count)
        while not validate_name(container_name):
            count += 1
            container_index = count if count > 10 else "0{0}".format(count)
            container_name = "{0}-{1}".format(alias, container_index)

        return container_name

    def _load_dependency_containers(self, service):
        """
        """
        if not isinstance(service, Service):
            raise TypeError("service must be and instance of Service.")

        if service.dependencies:
            if not isinstance(service.dependencies, dict):
                raise TypeError("service dependencies must be a dict.")

            for dependency in six.itervalues(service.dependencies):
                if not dependency.containers:
                    containers = self.find_service_containers(dependency)
                    if containers:
                        for name, container in six.iteritems(containers):

                            if dependency.name in service.host_config.links:
                                if not container.state().get('running'):
                                    raise RuntimeError(
                                        "Service: {0} has a link dependency on {1}. However, {2} isn't currently running."
                                        " Please delete or start {2} and try again.".format(
                                            service.name,
                                            dependency.name,
                                            name
                                        )
                                    )

                            service.dependencies[dependency.name].containers[name] = container

                            if not service.dependencies[dependency.name].cargo:
                                service.dependencies[dependency.name].cargo = Image(self._client_session, container.image)

                    else:
                        raise LookupError("Was unable to find Service: {0} Dependency: {1}".format(service.name, dependency.name))
        else:
            logger.info("There are no dependency containers to load.")

    def _offload_service_containers(self, service):
        """
        :param service:
        :return:
        """
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service")

        if service.containers:
            for key in list(service.containers.keys()):
                if key in service.containers:
                    del service.containers[key]

    def _load_service_cargo(self, service, inject_configs, use_cache=False):
        """
        :param service:
        :return None:
        """
        if not isinstance(service, Service):
            raise TypeError("service must of an instance of Service")

        repository = "{0}/{1}".format(service.repository, service.namespace)

        if service.source_registry:
            if service.source_tag:
                repository = "{0}:{1}".format(repository, service.source_tag)

            if service.source_registry.auth:
                self._request_auth(service.source_registry)

            service.cargo = Image.pull(
                self._client_session,
                service.source_registry,
                repository
            )
        elif service.docker_file:
            service.cargo = Image.build(
                self._client_session,
                repository,
                service.docker_file,
                use_cache=use_cache
            )
        else:
            raise LookupError("Couldn't locate image or Dockerfile. Every service is required to have one or the other.")

        # dynamically inject configuration files if required.
        if inject_configs is True and self._injector:
            self._injector.inject(self._client_session, service)

    def _load_service_containers(self, service, configs, use_cache):
        """
        :param service:
        :return:
        """
        if not isinstance(service, Service):
            raise TypeError("service must of an instance of Service")

        if not service.containers:
            container_name = self._container_registration(service.alias)

            if service.dependencies:
                self._load_dependency_containers(service)

            if not service.cargo:
                self._load_service_cargo(service, configs, use_cache)

            self._update_container_host_config(service)
            service.containers[container_name] = Container(
                self._client_session,
                container_name,
                service.cargo.id,
                container_config=service.container_config.to_dict(),
                host_config=service.host_config.to_dict()
            )

    def _update_container_host_config(self, service):
        """
        :param service:
        :return None:
        """
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of Service")

        if service.dependencies:

            self._load_dependency_containers(service)

            if service.host_config.links:
                self._update_links(service)

            if service.host_config.volumes_from:
                self._update_volumes_from(service)

    def _update_links(self, service):
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of service")

        for index, link in enumerate(service.host_config.links):
            if link == service.name:
                raise ReferenceError(
                    "Link Error: It is not possible to link {0} to {1}.".format(
                        service.alias,
                        link
                    )
                )

            if link in service.dependencies:
                for name, container_to_link in six.iteritems(service.dependencies[link].containers):
                    service.host_config.links[index] = "{0}:{1}".format(container_to_link.id, link)

    def _update_volumes_from(self, service):
        if not isinstance(service, Service):
            raise TypeError("service must be an instance of service")

        for index, volume_bind in enumerate(service.host_config.volumes_from):
            if volume_bind == service.name:
                raise ReferenceError(
                    "VolumeFrom Error: It is not possible to bind a volume from {0} to {1}.".format(
                        service.name,
                        volume_bind
                    )
                )

            if ':' in volume_bind:
                volume_bind, permissions = volume_bind.split(':')

            if volume_bind in service.dependencies:
                for name, container_to_bind in six.iteritems(service.dependencies[volume_bind].containers):
                    service.host_config.volumes_from[index] = container_to_bind.id

    def _request_auth(self, registry):
        """
             self, username, password=None, email=None, registry=None,
              reauth=False, insecure_registry=False, dockercfg_path=None):
        """
        if registry:
            if registry.auth:
                registry.auth.load_dockercfg()

            try:
                self._client_session.login(username=registry.auth.user,
                                           password=registry.auth.passwd,
                                           dockercfg_path=registry.auth.config_path,
                                           reauth=True if registry.auth.auth_type == 'registry_rubber' else False,
                                           registry=registry.auth.registry)
            except Exception:
                raise
        else:
            raise Exception("a registry is required when requesting auth.")
