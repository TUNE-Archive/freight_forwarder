# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import argparse

from freight_forwarder       import FreightForwarder
from .cli_mixin              import CliMixin


class TestCommand(CliMixin):
    """The test command allows developers to build and run their test docker file without interfering with their
    current running application containers. This command is designed to be ran periodically throughout a developers
    normal development cycle. Its a nice encapsulated way to run a projects test suite.

    .. warning:: This command requires your service definition to have a test Dockerfile.

    :options:
      - ``-h, --help``     (info) - Show the help message
      - ``--data-center``  (**required**) - The data center to deploy. example: sea1, sea3, or us-east-1
      - ``--environment``  (**required**) - The environment to deploy. example: development, test, or production
      - ``--service``      (**required**) - The service that will be used for testing.
      - ``--configs``      (optional) - Inject configuration files. Requires CIA integration.

    :return: exit_code
    :rtype: integer
    """
    def __init__(self, sub_parser):
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception("parser should of an instance of argparse._SubParsersAction")

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('test')
        CliMixin.__init__(self)
        self._build_arguments()
        self._parser.set_defaults(func=self._test)

    def _build_arguments(self):
        """
        build arguments for command.
        """
        # TODO: comeback to allow test path override. maybe?
        # self._parser.add_argument(
        #     '--test-path',
        #     type=utils.validate_path,
        #     required=False,
        #     help=('Path th projects test Dockerfile. Dockerfile should be in the root of the test directory.')
        # )
        self._parser.add_argument(
            '--configs',
            type=bool,
            required=False,
            default=False,
            help="Would you like to inject configuration files?"
        )

    def _test(self, args, **extra_args):
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
            'test',
            args.data_center,
            args.environment,
            args.service
        )

        # run test container.
        bill_of_lading = freight_forwarder.test(commercial_invoice, args.configs)

        # pretty lame... Need to work on return values through to app to make them consistent.
        exit_code = 0 if bill_of_lading else 1

        if exit_code != 0:
            exit(exit_code)
