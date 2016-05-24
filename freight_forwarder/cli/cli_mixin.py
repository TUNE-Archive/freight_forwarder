# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import argparse

from freight_forwarder.utils import normalize_value


class CliMixin(object):
    """Simple class to add some common arguments to to each command.
    """
    def __init__(self):
        """
        """
        if not self._parser:
            raise AttributeError("self._parser must be defined.")

        self._parser.add_argument(
            '--data-center',
            action=NormalizeValue,
            required=True,
            type=str,
            default='local',
            help='The data center to run tests in. example: sea1, sea3, or us-east-1'
        )

        self._parser.add_argument(
            '--environment',
            action=NormalizeValue,
            required=True,
            type=str,
            default='development',
            help='The environment to run tests in. example: development, test, or production'
        )

        self._parser.add_argument(
            '--service',
            action=NormalizeValue,
            type=str,
            required=True,
            help="What service would you like do export / deploy?  defaults to 'all'."
        )

        self._parser.add_argument(
            '-D', '--verbose',
            required=False,
            action='store_true',
            default=False,
            help='enable verbose output'
        )


class NormalizeValue(argparse.Action):
    """

    """
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")

        super(NormalizeValue, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, normalize_value(values))
