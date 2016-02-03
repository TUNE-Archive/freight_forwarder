from __future__ import unicode_literals, absolute_import
import os
from time import sleep
import json
import six

from ..utils                 import logger
from .service                import Service
from ..image                 import Image
from ..container             import Container
from ..container.config      import Config as ContainerConfig
from ..container.host_config import HostConfig
from ..registry              import V1, V2


# TODO: need to provide away for this to be a plugin would be great to be able to do bin injection as well.
# cia isn't currently open sourced will come soon after ff is folks are interested.
class Injector(object):
    def __init__(self, environment, data_center, project, registry, client_id=None, client_secret=None, injector_image=None):
        """
        :param service_alias:
        :param environment:
        :param data_center:
        :param client_id:
        :param client_secret:
        :return:
        """
        self._environment = environment
        self._data_center = data_center
        self._project     = project

        if not isinstance(registry, (V1, V2)):
            raise TypeError('registry must be an instance of V1 or V2.')

        self._registry         = registry
        self._injector_image   = os.getenv('INJECTOR_IMAGE')   if injector_image   is None else injector_image

        if not self._injector_image:
            raise AttributeError('INJECTOR_IMAGE must be available in the environment or passed to the Injector constructor')

        self._client_id     = os.getenv('INJECTOR_CLIENT_ID')     if client_id     is None else client_id
        self._client_secret = os.getenv('INJECTOR_CLIENT_SECRET') if client_secret is None else client_secret

    @property
    def environment(self):
        return self._environment

    @property
    def data_center(self):
        return self._data_center

    @property
    def project(self):
        return self._project

    def inject(self, client_session, service):
        """
        """
        injector_service = self._create_injector_service(target=service)

        if not isinstance(service, Service):
            raise TypeError(logger.error("Service must be an instance of service"))

        if not service.cargo:
            raise LookupError(logger.error("Service must have cargo to inject files."))

        logger.warning("Starting the injection process on service: {0}.".format(service.alias))
        injector_service.intermediate_image = None

        try:
            injector_container_name, injector_response = self._create_configs(client_session, injector_service)
            intermediate_name = "{0}-{1}-01".format(injector_service.alias, 'intermediate')

            logger.info("Creating {0}.".format(intermediate_name), extra={'container': 'injector'})

            container_config = ContainerConfig()
            container_config.entry_point = ["/bin/sh"]
            container_config.cmd = self._generate_injection_cmd(injector_response)
            container_config.detach = False

            container_host_config = HostConfig()
            container_host_config.restart_policy = None
            container_host_config.volumes_from = injector_container_name

            injector_service.containers[intermediate_name] = Container(
                client_session,
                intermediate_name,
                service.cargo.id,
                container_config=container_config.to_dict(),
                host_config=container_host_config.to_dict()
            )

            if not injector_service.containers[intermediate_name].start(attach=False):
                logger.error(injector_service.containers[intermediate_name].dump_logs(), extra={'container', 'injector'})
                raise RuntimeError(logger.error("was unable to create the required config files."))

            config = service.cargo.config.to_dict()
            injector_service.intermediate_image = Image(
                client_session,
                injector_service.containers[intermediate_name].commit(config, intermediate_name, "latest")
            )

            # intermediate_name = self._container_registration(injector_service.alias, 'intermediate')
            intermediate_name = "{0}-{1}-02".format(injector_service.alias, 'intermediate')
            logger.info("Creating {0}.".format(intermediate_name), extra={"container": 'injector'})
            injector_service.containers[intermediate_name] = Container(
                client_session,
                intermediate_name,
                injector_service.intermediate_image.id,
                container_config=service.cargo.config.to_dict()
            )

            image_name = "{0}/{1}".format(service.repository, service.namespace)
            logger.info(
                "Updating service: {0} image: {1}".format(service.name, image_name),
                extra={"container": 'injector'}
            )

            service.cargo = Image(
                client_session,
                injector_service.containers[intermediate_name].commit(config, image_name, "latest")
            )

        finally:
            if injector_service:
                if injector_service.containers:
                    logger.info("Cleaning up injector and intermediate containers.", extra={"container": 'injector'})
                    for key in list(injector_service.containers):
                        del injector_service.containers[key]

                if injector_service.intermediate_image:
                    injector_service.intermediate_image.delete()

    ###
    # Protected methods
    ###
    def _create_configs(self, client_session, injector_service):
        """
        """
        logger.info("Creating files.", extra={'container': 'injector'})

        injector_service.cargo = Image.pull(
            client_session,
            injector_service.source_registry,
            "{0}/{1}:{2}".format(injector_service.repository, injector_service.namespace, injector_service.source_tag)
        )

        # self._container_registration
        injector_container_name = "{0}-{1}".format(injector_service.alias, 'builder')
        injector_service.containers[injector_container_name] = Container(
            client_session,
            injector_container_name,
            injector_service.cargo.id,
            container_config=injector_service.container_config.to_dict(),
            host_config=injector_service.host_config.to_dict()
        )

        try:
            injector_service.containers[injector_container_name].start()
            while not injector_service.containers[injector_container_name].output():
                sleep(0.5)
            else:
                injector_response = json.loads(
                    injector_service.containers[injector_container_name].output().decode('utf-8')
                )

        except ValueError:
            raise ValueError(
                logger.error('The injector responded with malformed data. response: {0}'.format(
                    injector_service.containers[injector_container_name].dump_logs()))
            )

        return injector_container_name, injector_response

    def _create_injector_service(self, target):
        host_config_data = {
            "restart_policy": None
        }

        # "INJECTOR_VERBOSE=True" for debugging
        # "INJECTOR_HOST=cia.ops.tune.com"
        # "INJECTOR_PORT=80"
        container_config_data = {
            "detach": False,
            "env_vars": [
                "INJECTOR_CLIENT_ID={0}".format(self._client_id),
                "INJECTOR_CLIENT_SECRET={0}".format(self._client_secret),
                "ENVIRONMENT={0}".format(self._environment),
                "SERVICE={0}".format(target.name),
                "PROJECT={0}".format(self._project),
                "DATACENTER={0}".format(self._data_center)
            ]
        }

        if not isinstance(self._injector_image, six.string_types):
            raise TypeError('injector image must be a string')

        chunks = self._injector_image.split('/')
        length = len(chunks)

        if length is 2:
            repository, namespace = chunks
        elif length is 1:
            namespace = chunks[0]
            repository = 'library'
        else:
            raise AttributeError('Injector image must be in one of the following formats: repository/namespace:tag '
                                 'or namespace:tag')

        return Service(
            repository,
            namespace,
            'injector',
            "{0}-injector".format(target.alias),
            container_config=ContainerConfig(container_config_data),
            host_config=HostConfig(host_config_data),
            source_registry=self._registry
        )

    def _generate_injection_cmd(self, meta_data):
        """ example injector response:
        [
           {
              "config_path":"/configs/cli_config.py",
              "path":"/opt/cia-cli/cia_sdk/config",
              "user":"injector",
              "status_code":201,
              "chmod":755,
              "checksum":"a4bcf3939dd3a6aa4e04ee9f92131df4",
              "created":"2015-08-04T22:48:25Z",
              "updated":"2015-08-04T22:48:25Z",
              "group":"injector"
           }
        ]

        """
        cmd = []
        self._validate_templates(meta_data)
        for i, config_data in enumerate(meta_data):
            container_path = os.path.join(config_data['path'], config_data['name'])

            cmd.append("mkdir")
            cmd.append("-p")
            cmd.append(config_data['path'])
            cmd.append("&&")
            cmd.append("cp")
            cmd.append("-f")
            cmd.append(config_data['config_path'])
            cmd.append(container_path)
            cmd.append("&&")
            cmd.append("chown")
            cmd.append("{0}:{1}".format(config_data['user'], config_data['group']))
            cmd.append(container_path)
            cmd.append("&&")
            cmd.append("chmod")
            cmd.append(six.text_type(config_data['chmod']))
            cmd.append(container_path)

            if i + 1 < len(meta_data):
                cmd.append("&&")

        cmd = ["-c", " ".join(cmd)]
        return cmd

    def _validate_templates(self, templates):
        """
        :param templates:
        :return:
        """
        if templates is None:
            return templates

        if not isinstance(templates, list):
            raise TypeError(logger.error("templates should be a list."))

        for template in templates:
            if not isinstance(template, dict):
                raise TypeError(logger.error("each item to be injected must be a dict."))

            if template.get('notifications'):
                for level, notification in six.iteritems(template.get('notifications')):
                    if level == 'errors':
                        logger.error(
                            "errors were returned during the injection process. errors: {0}".format(notification),
                            extra={"container": 'injector'}
                        )
                        raise Exception(notification)

            for key in ('user', 'name', 'group', 'chmod', 'config_path', 'path', 'checksum'):
                if key not in template:
                    raise KeyError(logger.error("The injector didn't return a {0}.".format(key)))

        return templates
