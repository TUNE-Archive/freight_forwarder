# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import argparse

from freight_forwarder       import FreightForwarder
from .cli_mixin              import CliMixin


class OffloadCommand(CliMixin):
    """The offload Command removes all containers and images related to the service provided.

    :options:
      - ``-h, --help``     (info) - Show the help message.
      - ``--data-center``  (**required**) - The data center to deploy. example: sea1, sea3, or us-east-1
      - ``--environment``  (**required**) - The environment to deploy. example: development, test, or production
      - ``--service``      (**required**) - This service in which all containers and images will be removed.

    :return: exit_code
    :rtype: integer
    """
    def __init__(self, sub_parser):
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception("parser should of an instance of argparse._SubParsersAction")

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('offload')
        CliMixin.__init__(self)
        self._parser.set_defaults(func=self._offload)

    def _offload(self, args, **extra_args):
        """
        Export is the entry point for exporting docker images.
        """
        if not isinstance(args, argparse.Namespace):
            raise Exception("args should of an instance of argparse.Namespace")

        # create new freight forwarder object
        freight_forwarder = FreightForwarder(verbose=args.verbose)

        # create commercial invoice this is the contact given to freight forwarder dispatch containers and images
        commercial_invoice = freight_forwarder.commercial_invoice(
            'offload',
            args.data_center,
            args.environment,
            args.service
        )

        # off load container and images.
        bill_of_lading = freight_forwarder.offload(commercial_invoice)

        # pretty lame... Need to work on return values through to app to make them consistent.
        exit_code = 0 if bill_of_lading else 1

        if exit_code != 0:
            exit(exit_code)
