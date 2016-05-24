# -*- coding: utf-8; -*-
from __future__ import unicode_literals

import argparse
import six
import six.moves

import six

from freight_forwarder       import FreightForwarder
from freight_forwarder.utils import logger
from .cli_mixin              import CliMixin


class ExportCommand(CliMixin):
    """ The export command builds a "service" Docker image and pushes the image to a Docker registry.  A service is
    a defined in the configuration file.

    The export command requires a Registry to be defined in the configuration file or it will default to Docker Hub,
    private registries are supported.

    The export command by default will build the container and its defined dependencies. This will start the targeted
    service container after it's dependencies have been satisfied. If the container is successfully started it will push
    the image to the repository.

    If test is set to true a test Dockerfile is required and should be defined in the configuration file.
    The test Dockerfile will be built and ran after the "service" Dockerfile.  If the test Dockerfile fails the
    application will exit 1 without pushing the image to the registry.

    The configs flag requires integration with CIA.  For more information about CIA please to the documentation.

    When the export command is executed with ``--no-validation`` it will perform the following actions.

        1. Build the defined Dockerfile or pull the image for the service.
        2. Inject a configuration if defined with credentials.
        3. Push the Image to the defined destination registry or the defined default, if no default is defined, it will
           attempt to push the image to Docker Hub.

    To implement with a Continuous Integration solution (i.e. Jenkins, Travis, etc); please refer to below and use the
    ``-y`` option to not prompt for confirmation.

    :options:
      - ``-h, --help``     (info) - Show the help message.
      - ``--data-center``  (**required**) - The data center to deploy. example: us-east-02, dal3, or us-east-01.
      - ``--environment``  (**required**) - The environment to deploy. example: development, test, or production.
      - ``--service``      (**required**) - The Service that will be built and exported.
      - ``--clean``              (optional) - Clean up anything that was created during current command execution.
      - ``--configs``            (optional) - Inject configuration files. Requires CIA integration.
      - ``--tag``                (optional) - Metadata to tag Docker images with.
      - ``--no-tagging-scheme``  (optional) - Turn off freight forwarders tagging scheme.
      - ``--test``               (optional) - Build and run test Dockerfile for validation before pushing image.
      - ``--use-cache``          (optional) - Allows use of cache when building images defaults to false.
      - ``--no-validation``      (optional) - The image will be built, NOT started and pushed to the registry.
      - ``-y``                   (optional) - Disables the interactive confirmation with ``--no-validation``.

    :return: exit_code
    :rtype: integer

    """
    def __init__(self, sub_parser):
        logger.setup_logging('cli')
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception(logger.error("parser should of an instance of argparse._SubParsersAction"))

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('export')
        CliMixin.__init__(self)
        self._build_arguments()
        self._parser.set_defaults(func=self._export)

    def _build_arguments(self):
        """
        build arguments for command.
        """
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
            '--test',
            type=bool,
            required=False,
            default=False,
            help="Run tests."
        )

        self._parser.add_argument(
            '-t', '--tag',
            required=False,
            type=six.text_type,
            action='append',
            help='list of tags applied to the image being exported. example: sh1hash'
        )

        self._parser.add_argument(
            '--use-cache',
            required=False,
            action='store_true',
            default=False,
            help='Allow build to use cached image layers.'
        )

        self._parser.add_argument(
            '--no-tagging-scheme',
            required=False,
            action='store_true',
            default=False,
            help='Turn off freight forwarders tagging scheme.'
        )

        self._parser.add_argument(
            '--no-validation',
            action="store_true",
            required=False,
            default=False,
            help='**UNSAFE**. The image will be built, NOT started, and pushed to the registry'
        )

        self._parser.add_argument(
            '-y',
            required=False,
            action='store_true',
            default=False,
            help='**UNSAFE**. Turn off `--no-validation` interaction during export'
        )

    def _export(self, args, **extra_args):
        """
        Export is the entry point for exporting docker images.
        """
        if not isinstance(args, argparse.Namespace):
            raise TypeError(logger.error("args should of an instance of argparse.Namespace"))

        # Warn the consumer about unsafe Docker Practices
        if args.no_validation:
            logger.warning("#######################################################\n"
                           "Validation has been disabled for this export operation.\n"
                           "This is an unsafe operation and does not verify the "
                           "run time nature of the container.\n"
                           "Any docker image created in this manner will not "
                           "be verified to start. Do not ship broken code.\n"
                           "#######################################################\n",
                           extra={'formatter': 'cli-warning'})

            # Require the consumer to verify their actions
            if not args.y:
                validation_input = six.moves.input("Please type \'yes\' to export the container without validation: ")

                if not (isinstance(validation_input, six.string_types) and ('yes' == validation_input)):
                    raise ValueError("Incorrect type defined. Required value: yes")

        # create new freight forwarder to create a commercial_invoice and export goods.
        freight_forwarder = FreightForwarder(verbose=args.verbose)

        # create commercial invoice this is the contact given to freight forwarder dispatch containers and images
        commercial_invoice = freight_forwarder.commercial_invoice(
            'export',
            args.data_center,
            args.environment,
            args.service,
            tagging_scheme=not args.no_tagging_scheme
        )

        # create commercial_invoice
        bill_of_lading = freight_forwarder.export(
            commercial_invoice,
            clean=args.clean,
            configs=args.configs,
            tags=args.tag,
            test=args.test,
            use_cache=args.use_cache,
            validate=not args.no_validation
        )

        # pretty lame... Need to work on return values through to app to make them consistent.
        exit_code = 0 if bill_of_lading else 1

        if exit_code != 0:
            exit(exit_code)
