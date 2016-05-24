# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
from sys        import stdout
from time       import sleep
import os

import six
import yaml
import requests
import psutil
from yaml.representer import SafeRepresenter

from .utils                 import normalize_keys, parse_hostname, logger, normalize_value
from .commercial_invoice    import CommercialInvoice
from .config                import Config, ACTIONS_SCHEME, ConfigUnicode

ROOT_PATH  = os.path.realpath(os.path.dirname(__file__))
STATE_PATH = os.path.join(os.getenv('HOME'), '.freight_forwarder', 'data', 'state')


class FreightForwarder(object):
    """
    The FreightForwarder class will be in charge of handling all communication between the end user, container ships,
    and ship yards. it will also handle fleet orchestration and discovery. If no config is present then a invoice /
    shipping and receiving port must be provided.
    """
    def __init__(self, config_path_override=None, verbose=False):
        # create config
        self._config = Config(path_override=config_path_override, verbose=verbose)

        # validate config file
        self._config.validate()

        # TODO: move bill of lading to its own object.
        self._bill_of_lading = None

    @property
    def config(self):
        return self._config

    @property
    def project(self):
        return self._config.project

    @property
    def team(self):
        return self._config.team

    def commercial_invoice(self, action, data_center, environment, transport_service, tagging_scheme=None):
        """
        :param action:
        :param data_center:
        :param environment:
        :param transport_service:
        :param tagging_scheme:
        :return:
        """
        if action not in ACTIONS_SCHEME:
            raise LookupError(logger.error("{0} isn't a support action.".format(action)))

        config_value = self._config.get(environment, 'environments')
        if config_value is None:
            raise LookupError(logger.error("Was unable to find environment: {0} in the config.".format(environment)))
        else:
            environment = config_value

        config_value = self._config.get(data_center, 'environments', environment.name)
        if config_value is None:
            raise LookupError(
                logger.error("Was unable to find data center: {0} in environment: {1}".format(data_center, environment.name))
            )
        else:
            data_center = config_value

        config_value = self._config.get(transport_service, 'environments', environment.name, data_center.name, action)
        if config_value is None:
                raise LookupError(
                    logger.error('Was unable to find the service: {0} attempting to be transported.'.format(transport_service))
                )
        else:
            transport_service = config_value

        # if we're exporting we need to use other services deploy definitions to avoid issues
        if action == 'export':
            services = self.__get_services('deploy', data_center, environment)
            services[transport_service.name] = transport_service
        else:
            services = self.__get_services(action, data_center, environment)

        return CommercialInvoice(
            team=self.team,
            project=self.project,
            services=services,
            hosts=self._config.get('hosts', 'environments', environment.name, data_center.name, action),
            transport_service=transport_service.alias,
            transport_method=action,
            data_center=data_center.alias,
            environment=environment.alias,
            registries=self._config.get('registries'),
            tags=self._config.get('tags', 'environments', environment.name, data_center.name, action),
            tagging_scheme=tagging_scheme
        )

    def container_ships(self, action):
        # TODO: return all hosts in config
        pass

    def environments(self):
        return self._config.environment_references()

    def data_centers(self, environment):
        return self._config.data_center_references(environment)

    def services(self):
        # TODO: return a list of all service names
        pass

    def deploy_containers(self, commercial_invoice, tag=None, env=None):
        """
        Deploy containers to specific container ship.
        'restart_policy' = {"maximum_retry_count": 5, "name": "always"}
        """
        commercial_invoice = self.__validate_commercial_invoice(commercial_invoice, 'deploy')

        fleet = self.__assemble_fleet(commercial_invoice)
        logger.info('Running deploy.')

        try:
            for address, container_ship in six.iteritems(fleet):
                # write state file
                self.__write_state_file(address, commercial_invoice.data_center, commercial_invoice.environment)

                # get new transport service for each container ship
                transport_service = commercial_invoice.transport_service

                # if source tag is provided override what was parsed in image.
                if tag:
                    transport_service.source_tag = tag

                # if env is provided merge what has been passed.
                if env:
                    transport_service.container_config.merge_env(env)

                # during a deploy always restart containers on failure. if detach is true.
                if transport_service.container_config.detach:
                    transport_service.host_config.restart_policy = {"maximum_retry_count": 5, "name": "always"}

                # validate service configs for deployment
                self.__service_deployment_validation(transport_service)

                # check with dispatch to see if its okay to export.
                self.__wait_for_dispatch(address)

                logger.info("dispatching service: {0} on host: {1}.".format(transport_service.alias, address))
                self.__dispatch(container_ship, transport_service)

                if self._bill_of_lading.get('failures'):
                    container_ship.recall_service(transport_service)
                else:
                    container_ship.offload_previous_containers(transport_service)
                    # clean up service expired service cargo.
                    container_ship.offload_expired_service_cargo(transport_service)

            return False if self._bill_of_lading.get('failures') else True
        finally:
            # complete distribution and delete state file.
            self.__complete_distribution(commercial_invoice)

    def quality_control(self, commercial_invoice, attach=False, clean=None, test=None, configs=None, use_cache=False, env=None):
        """
        :param attach:
        :param clean:
        :param test:
        :param configs:
        :return:
        """
        commercial_invoice = self.__validate_commercial_invoice(commercial_invoice, 'quality_control')

        fleet = self.__assemble_fleet(commercial_invoice)
        logger.info('Running quality control.')

        try:
            for address, container_ship in six.iteritems(fleet):
                # write state file
                self.__write_state_file(address, commercial_invoice.data_center, commercial_invoice.environment)

                # get new transport service
                transport_service = commercial_invoice.transport_service

                # if env is provided merge what has been passed.
                if env is not None:
                    transport_service.container_config.merge_env(env)

                # share some host info with user.
                container_ship.report()

                # check with dispatch to see if its okay to export.
                self.__wait_for_dispatch(address)

                logger.info('dispatching service: {0} on host: {1}.'.format(
                    transport_service.alias,
                    address
                ))

                # TODO: need to inject on all services during qc if configs == true
                if configs:
                    container_ship.injector = commercial_invoice.injector if configs else None

                if attach:
                    dependents = False
                else:
                    dependents = True

                self.__dispatch(container_ship, transport_service, attach, configs, dependents, test, use_cache)

                if clean:
                    # delete containers.
                    container_ship.offload_service_containers(transport_service)

                    # delete images
                    container_ship.offload_service_cargo(transport_service)
                else:
                    # clean up previous containers
                    container_ship.offload_previous_containers(transport_service)

                    # clean up service expired service cargo.
                    container_ship.offload_expired_service_cargo(transport_service)

            # TODO: Do something with failures / return bill of lading
            return False if self._bill_of_lading.get('failures') else True
        finally:
            # complete distribution and delete state file.
            self.__complete_distribution(commercial_invoice)

    def test(self, commercial_invoice, configs):
        """
        """
        commercial_invoice = self.__validate_commercial_invoice(commercial_invoice, 'test')

        fleet = self.__assemble_fleet(commercial_invoice)
        logger.info('Running tests.')

        try:
            for address, container_ship in six.iteritems(fleet):
                # write state file
                self.__write_state_file(address, commercial_invoice.data_center, commercial_invoice.environment)

                # get new transport service
                transport_service = commercial_invoice.transport_service
                if not transport_service:
                    raise LookupError("unable to find {0} in config.")

                # check with dispatch to see if its okay to export.
                self.__wait_for_dispatch(address)

                logger.info("dispatching service: {0} on host: {1}.".format(transport_service.alias, address))
                if not container_ship.test_service(transport_service, configs):
                    raise AssertionError(
                        "Service: {0} Failed tests on Host: {1}.".format(transport_service.alias, container_ship.url.geturl())
                    )

                container_ship.offload_expired_service_cargo(transport_service)

            # TODO: need to return bill of lading
            return True
        finally:
            # complete distribution and delete state file.
            self.__complete_distribution(commercial_invoice)

    def offload(self, commercial_invoice):
        """
        """
        # TODO: allow for offloading of containers or images only.
        commercial_invoice = self.__validate_commercial_invoice(commercial_invoice, 'offload')

        fleet = self.__assemble_fleet(commercial_invoice)
        logger.info('Running offload.')

        try:
            for address, container_ship in six.iteritems(fleet):
                # write state file
                self.__write_state_file(address, commercial_invoice.data_center, commercial_invoice.environment)

                # get new transport service
                transport_service = commercial_invoice.transport_service
                if not transport_service:
                    raise LookupError("unable to find {0} in config.")

                # check with dispatch to see if its okay to export.
                self.__wait_for_dispatch(address)

                logger.info("offloading service: {0} on host: {1}.".format(transport_service.alias, address))
                container_ship.offload_all_service_containers(transport_service)
                container_ship.offload_all_service_cargo(transport_service)
            return True
        finally:
            self.__complete_distribution(commercial_invoice)

    def export(self, commercial_invoice, clean=None, configs=None, tags=None, test=None, use_cache=False,
               validate=True):
        """
        """
        commercial_invoice = self.__validate_commercial_invoice(commercial_invoice, 'export')

        # get docker host being used to export
        fleet = self.__assemble_fleet(commercial_invoice)

        if tags:
            commercial_invoice.tags = tags

        if len(fleet) > 1:
            raise ValueError(
                "When exporting images only one host can be supplied. if exported host isn't defined "
                "the default hosts will be used."
            )

        try:
            for address, container_ship in six.iteritems(fleet):
                # write state file
                self.__write_state_file(address, commercial_invoice.data_center, commercial_invoice.environment)
                transport_service = commercial_invoice.transport_service

                # check with dispatch to see if its okay to export.
                self.__wait_for_dispatch(address)
                logger.info("Exporting Docker image for service: {0} on host: {1}.".format(transport_service.alias, address))

                # share some host info with user.
                container_ship.report()

                # cleaning up existing containers that might conflict while exporting images.
                container_ship.offload_all_service_containers(transport_service)

                # create injector if configs is true for the service being deployed
                if configs:
                    container_ship.injector = commercial_invoice.injector if configs else None

                if validate:
                    # dispatch service and test.
                    self.__dispatch(container_ship, transport_service, False, configs, False, test, use_cache)
                else:
                    self.__dispatch_export_no_validation(container_ship, transport_service, configs, use_cache)

                if self.__verify_for_export(container_ship, transport_service) is False:
                    return False

                # export image
                container_ship.export(transport_service, commercial_invoice.tags)

                # remove all of the containers used for testing.
                container_ship.offload_all_service_containers(transport_service)

                if clean:
                    # delete all service images
                    container_ship.offload_service_cargo(transport_service)
                else:
                    # clean up old service cargo.
                    container_ship.offload_expired_service_cargo(transport_service)

            # TODO: Do something with failures / return bill of lading.
            return False if self._bill_of_lading and self._bill_of_lading.get('failures') else True
        finally:
            # complete distribution and delete state file.
            self.__complete_distribution(commercial_invoice)

    ##
    # private methods
    ##
    def __assemble_fleet(self, commercial_invoice):
        if not isinstance(commercial_invoice, CommercialInvoice):
            raise TypeError('commercial_invoice must be a instance of CommercialInvoice.')

        if commercial_invoice.transport_method == 'export':
            host_alias = commercial_invoice.transport_method
        else:
            host_alias = normalize_value(commercial_invoice.transport_service.name).replace('-', '_')

        fleet = commercial_invoice.container_ships.get(
            host_alias,
            commercial_invoice.container_ships.get('default')
        )

        for address, container_ship in six.iteritems(fleet):
            try:
                container_ship.healthy()
            except requests.exceptions.ConnectionError:
                raise LookupError("Unable to locate container ship @ {0}.".format(address))

        return fleet

    def __set_bill_of_lading(self, container_ship, service, verified):
        if self._bill_of_lading is None:
            self._bill_of_lading = {
                "failures": {},
                "successful": {}
            }

        bill_of_lading = self._bill_of_lading["successful" if verified else "failures"]
        address        = container_ship.url.geturl()

        if bill_of_lading.get(address):
            bill_of_lading[address].append(service)
        else:
            bill_of_lading[address] = [service]

    def __dispatch_dependencies(self, container_ship, service, configs, dependents, test, use_cache):
        """
        """
        # TODO: validation
        if service.dependencies:
            for name, dependency in six.iteritems(service.dependencies):
                if not dependency.containers:
                    dependency_containers = container_ship.find_service_containers(dependency)
                    if not dependency_containers:
                        self.__dispatch_service(container_ship, dependency, False, configs, dependents, test, use_cache)

                        if dependency.dependents and dependents:
                            for name, dependent in six.iteritems(dependency.dependents):
                                if name != service.name:
                                    self.__dispatch_service(container_ship, dependent, False, configs, dependents, test, use_cache)

    def __dispatch_service(self, container_ship, service, attach, configs, dependents, test, use_cache):
        """
        """
        self.__dispatch_dependencies(container_ship, service, None, dependents, test, use_cache)

        # load containers if they haven't been.
        if not service.containers:
            container_ship.load_containers(service, configs, use_cache)

        if container_ship.start_service_containers(service, attach):
            if test is None or test is True:
                if service.test_docker_file:
                    if not container_ship.test_service(service, configs):
                        raise AssertionError(
                            "Service: {0} Failed tests on Host: {1}.".format(service.name, container_ship.url.geturl())
                        )

                    self.__set_bill_of_lading(container_ship, service, True)
                    return

            self.__set_bill_of_lading(container_ship, service, True)
        else:
            self.__set_bill_of_lading(container_ship, service, False)
            logger.error(
                "failed while dispatching service: {0} on host: {1}.".format(service.name, container_ship.url.geturl())
            )

    def __dispatch_export_no_validation(self, container_ship, transport_service, configs, use_cache):
        try:
            container_ship.load_cargo(transport_service, configs, use_cache)
        except Exception as e:
            # TODO - lookup exception and return actual value
            if hasattr(e, 'message'):
                logger.error("Exception raised from the container build process. "
                             "Message: {0}".format(e.message))
            else:
                logger.error("Exception raised: {0}".format(e))

            raise e

    def __dispatch(self, container_ship, service, attach=False, configs=None, dependents=True, test=False, use_cache=False):

        self.__dispatch_service(container_ship, service, attach, configs, dependents, test, use_cache)

        if service.dependents and dependents and not attach:
            for name, dependent in six.iteritems(service.dependents):
                self.__dispatch(container_ship, dependent, False, None, dependents, test, use_cache)

    def __get_services(self, action, data_center, environment):
        services = {}

        for key in self._config.service_references:
            service = self._config.get(key, 'environments', environment.name, data_center.name, action)

            if isinstance(service, dict):
                services[key] = service
            else:
                raise ValueError(logger.error('Every service defined must be an object, {0} was not.'.format(key)))

        return services

    def __wait_for_dispatch(self, address):
        dispatch_queue = self.__get_dispatch_queue(address)
        if not dispatch_queue:
            return True

        host = parse_hostname(address)
        state_path = os.path.join(STATE_PATH, self.team, self.project, host)
        current_pid = None
        while current_pid != os.getpid():
            try:
                current_pid = dispatch_queue.pop(0)[1]
                queue_length = len(dispatch_queue)

                if queue_length > 0:
                    logger.info("Dispatch for {0} has a queue count of {1} for {2}-{3}.".format(
                        host,
                        queue_length,
                        self.team,
                        self.project
                    ))

                currently_dispatched = psutil.Process(current_pid)

                if current_pid == os.getpid():
                    break
                else:
                    state_data = self.__get_state_data(address, current_pid)
                    if state_data:
                        logger.info("Please wait for dispatch while pid: {0} completes {1} "
                                    "for {2}-{3} in data center: {4} for environment: {5}.".format(
                                        state_data.get('pid'),
                                        state_data.get('action'),
                                        state_data.get('team'),
                                        state_data.get('project'),
                                        state_data.get('data_center'),
                                        state_data.get('environment'))
                                    )

                    while currently_dispatched.is_running():
                        stdout.write('.')
                        stdout.flush()
                        sleep(1)
                    else:
                        stdout.write('\n')

            except psutil.NoSuchProcess:
                logger.info("Was unable to find pid: {0}.".format(current_pid))
                self.__delete_state_file(state_path, current_pid)

        return True

    def __get_state_data(self, address, pid):
        host = parse_hostname(address)
        state_path = os.path.join(STATE_PATH, self.team, self.project, host)
        current_state_file = os.path.join(state_path, "{0}.yml".format(pid))

        if os.path.isfile(current_state_file):
            with open(current_state_file, 'r') as f:
                try:
                    return normalize_keys(yaml.safe_load(f))
                except:
                    logger.warning("unable to load yml in state file.")

        else:
            logger.warning("Was unable to find state file.")
            return None

    def __write_state_file(self, address, data_center, environment):
        host = parse_hostname(address)
        state_path = os.path.join(STATE_PATH, self.team, self.project, host)
        if not os.path.exists(state_path):
            os.makedirs(state_path)

        state_file = os.path.join(state_path, "{0}.yml".format(os.getpid()))
        if os.path.isfile(state_file):
            raise RuntimeError("Unable to run freight forwarder pid already in use.")
        else:
            # TODO: move to a yaml util
            def config_unicode_presenter(dumper, data):
                return dumper.represent_scalar('tag:yaml.org,2002:str', data)

            SafeRepresenter.add_representer(ConfigUnicode, config_unicode_presenter)

            with open(state_file, 'w') as f:
                f.write(
                    yaml.safe_dump(
                        {
                            "team": self.team,
                            "project": self.project,
                            "environment": environment,
                            "data_center": data_center,
                            "host": host,
                            "pid": os.getpid()
                        }
                    )
                )

    def __get_dispatch_queue(self, address):
        host = parse_hostname(address)
        state_path = os.path.join(STATE_PATH, self.team, self.project, host)
        pids = []
        for path in os.listdir(state_path):
            file_path = os.path.join(state_path, path)
            created_at = os.path.getctime(file_path)
            pid, ext = os.path.splitext(path)
            try:
                pid = int(pid)
            except:
                logger.error("unable to cast pid to int for filename. deleting {0}".format(file_path))
                os.remove(file_path)
                continue

            pids.append((created_at, pid))

        # sort by date.
        return sorted(pids, key=lambda x: x[0])

    def __delete_state_file(self, address, pid):
        # TODO: need to write state file per commercial invoice not per service. I think that is why we see multiple
        # attempts to delete already deleted files.
        # TODO: add more state data. might want to consider using this for consul.
        host = parse_hostname(address)
        state_path = os.path.join(STATE_PATH, self.team, self.project, host)
        current_state_file = os.path.join(state_path, "{0}.yml".format(pid))

        if os.path.isfile(current_state_file):
            logger.info("Deleting state file for pid: {0}.".format(pid))
            os.remove(current_state_file)
            return True
        else:
            logger.info("Was unable to delete state file.")
            return False

    def __complete_distribution(self, commercial_invoice):
        cleaned = []
        for container_ships in six.itervalues(commercial_invoice.container_ships):

            for address, container_ship in six.iteritems(container_ships):
                if address in cleaned:
                    continue

                # clean up dangling images
                container_ship.clean_up_dangling_images()

                # remove state file
                self.__delete_state_file(address, os.getpid())

                cleaned.append(address)

    def __service_deployment_validation(self, service, validated=[]):
        if not service:
            raise ValueError("service_deployment_validation requires a service")
        if service.name in validated:
            return True

        if service.docker_file:
            raise ValueError(
                "Service: {0} Can't build when deploying.  Please provide an image and retry.".format(service.alias)
            )

        validated.append(service.name)

        if service.dependencies:
            for dependency in six.itervalues(service.dependencies):
                self.__service_deployment_validation(dependency, validated)

        if service.dependents:
            for dependent in six.itervalues(service.dependents):
                self.__service_deployment_validation(dependent, validated)

    def __validate_commercial_invoice(self, commercial_invoice, transport_method):
        """

        :param commercial_invoice:
        :param transport_method:
        :return:
        """
        if not isinstance(commercial_invoice, CommercialInvoice):
            raise TypeError('commercial_invoice must be an instance of CommercialInvoice')

        if commercial_invoice.transport_method != transport_method:
            raise AssertionError(
                'The commercial invoice provided isn\'t for '
                '{0}. The transport method provided: {1}'.format(transport_method, commercial_invoice.transport_method)
            )

        return commercial_invoice

    def __verify_for_export(self, container_ship, transport_service):
        """
        Verify the bill of lading has no failures for the defined transport_service while exporting
        :param container_ship:
        :param transport_service:
        :return:
        """
        verified = True
        if self._bill_of_lading and self._bill_of_lading.get('failures'):
            failures = self._bill_of_lading.get('failures')
            if container_ship.url.geturl() in failures:
                failed_services = failures[container_ship.url.geturl()]
                for service in failed_services:
                    if transport_service == service:
                        verified = False
                    else:
                        pass

            return verified
        else:
            return verified
