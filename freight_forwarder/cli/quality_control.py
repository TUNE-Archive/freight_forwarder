# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import argparse

from freight_forwarder       import FreightForwarder
from freight_forwarder.utils import logger
from .cli_mixin              import CliMixin


class QualityControlCommand(CliMixin):
    """
    The quality-control command allows development teams to validate freight forwarder work flows without actually
    deploying or exporting.

    :options:
      - ``-h, --help``     (info) - Show the help message
      - ``--data-center``  (**required**) - The data center to deploy. example: sea1, sea3, or us-east-1.
      - ``--environment``  (**required**) - The environment to deploy. example: development, test, or production.
      - ``--service``      (**required**) - The service that will be used for testing.
      - ``--attach``       (optional) - Attach to the service containers output.
      - ``--clean``        (optional) - Remove all images and containers after run.
      - ``-e, --env``      (optional) - list of environment variables to create on the container will override existing. example: MYSQL_HOST=172.17.0.4
      - ``--configs``      (optional) - Inject configuration files. Requires CIA integration.
      - ``--test``         (optional) - Run test Dockerfile must be provided in the configuration file.
      - ``--use-cache``    (optional) - Allows use of cache when building images defaults to false.

    :return: exit_code
    :rtype: integer
    """

    # TODO: need to consider adding shipping port.
    def __init__(self, sub_parser):
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception("parser should of an instance of argparse._SubParsersAction")

        logger.setup_logging('cli')
        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('quality-control')
        CliMixin.__init__(self)
        self._build_arguments()
        self._parser.set_defaults(func=self._quality_control)

    def _build_arguments(self):
        """
        build arguments for command.
        """
        self._parser.add_argument(
            '--attach',
            type=bool,
            required=False,
            default=False,
            help="Attach to containers output?"
        )

        self._parser.add_argument(
            '--clean',
            type=bool,
            required=False,
            default=False,
            help="clean up everything that was created by freight forwarder at the end."
        )

        self._parser.add_argument(
            '--configs',
            type=bool,
            required=False,
            default=False,
            help="Would you like to inject configuration files?"
        )

        self._parser.add_argument(
            '-e', '--env',
            required=False,
            type=str,
            action='append',
            default=None,
            help='environment variables to create in the container at run time.'
        )

        self._parser.add_argument(
            '--test',
            type=bool,
            required=False,
            default=False,
            help="Run tests."
        )

        self._parser.add_argument(
            '--use-cache',
            required=False,
            action='store_true',
            default=False,
            help='Allow build to use cached image layers.'
        )

    def _quality_control(self, args, **extra_args):
        """
        Export is the entry point for exporting docker images.
        """
        if not isinstance(args, argparse.Namespace):
            raise Exception("args should of an instance of argparse.Namespace")

        # create new freight forwarder object
        # config_override=manifest_override
        freight_forwarder = FreightForwarder(verbose=args.verbose)

        # create commercial invoice this is the contact given to freight forwarder dispatch containers and images
        commercial_invoice = freight_forwarder.commercial_invoice(
            'quality_control',
            args.data_center,
            args.environment,
            args.service
        )

        # call quality control with commercial invoice and additional arguments
        bill_of_lading = freight_forwarder.quality_control(
            commercial_invoice,
            attach=args.attach,
            clean=args.clean,
            test=args.test,
            configs=args.configs,
            use_cache=args.use_cache,
            env=args.env
        )

        # pretty lame... Need to work on return values through to app to make them consistent.
        exit_code = 0 if bill_of_lading else 1

        if exit_code != 0:
            exit(exit_code)
