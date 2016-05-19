# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import argparse

import six

from freight_forwarder       import FreightForwarder
from freight_forwarder.utils import logger
from .cli_mixin              import CliMixin


class DeployCommand(CliMixin):
    """ The deploy command pulls an image from a Docker registry, stops the previous running containers, creates and starts
    new containers, and cleans up the old containers and images on a docker host. If the new container fails to start,
    the previous container is restarted and the most recently created containers and image are removed.

    :options:
      - ``-h, --help``      (info) - Show the help message
      - ``--data-center``   (**required**) - The data center to deploy. example: sea1, sea3, or us-east-1
      - ``--environment``   (**required**) - The environment to deploy. example: development, test, or production
      - ``--service``       (**required**) - The Service that will be built and exported.
      - ``--tag``           (optional) - The tag of a specific image to pull from a registry. example: sea3-development-latest
      - ``-e, --env``       (optional) - list of environment variables to create on the container will override existing. example: MYSQL_HOST=172.17.0.4

    :return: exit_code
    :rtype: integer
    """

    def __init__(self, sub_parser):
        """Constructor for Docker Command class."""
        logger.setup_logging('cli')
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise TypeError(logger.error("parser should of an instance of argparse._SubParsersAction"))

        # Set up deploy parser and pass deploy function to defaults.
        self._parser = sub_parser.add_parser('deploy')
        CliMixin.__init__(self)
        self._build_arguments()
        self._parser.set_defaults(func=self.deploy)

    def _build_arguments(self):
        """
        build arguments for command.
        """
        # TODO: add tests to confirm deployments
        self._parser.add_argument(
            '-t', '--tag',
            required=False,
            type=six.text_type,
            default=None,
            help='This tag will override image tag provided in the configuration file.'
        )

        self._parser.add_argument(
            '-e', '--env',
            required=False,
            type=six.text_type,
            action='append',
            default=None,
            help='environment variables to create in the container at run time.'
        )

    def deploy(self, args, **extra_args):
        """Deploy a docker container to a specific container ship (host)

        :param args:
        :type args:
        """
        if not isinstance(args, argparse.Namespace):
            raise TypeError(logger.error("args should of an instance of argparse.Namespace"))

        # create new freight forwarder
        freight_forwarder = FreightForwarder(verbose=args.verbose)

        # create commercial invoice this is the contact given to freight forwarder to dispatch containers and images
        commercial_invoice = freight_forwarder.commercial_invoice(
            'deploy',
            args.data_center,
            args.environment,
            args.service
        )

        # deploy containers.
        bill_of_lading = freight_forwarder.deploy_containers(commercial_invoice, args.tag, args.env)

        # pretty lame... Need to work on return values through to app to make them consistent.
        exit_code = 0 if bill_of_lading else 1

        if exit_code != 0:
            exit(exit_code)
