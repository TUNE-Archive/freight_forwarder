# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import platform
import argparse

from docker                  import version as docker_py_version
from freight_forwarder.const import VERSION, DOCKER_API_VERSION
from freight_forwarder.utils import logger


class InfoCommand(object):
    """Display metadata about Freight Forwarder and Python environment.

    :options:
      - ``-h, --help`` (info) - Show the help message.

    Example::

        $ freight-forwarder info
        Freight Forwarder: 1.0.0
        docker-py: 1.3.1
        Docker Api: 1.19
        CPython version: 2.7.10
        elapsed: 0 seconds

    :return: exit_code
    :rtype: int
    """
    def __init__(self, sub_parser):
        logger.setup_logging('cli')
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise logger.error(Exception("parser should of an instance of argparse._SubParsersAction"))

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('info')
        self._parser.set_defaults(func=self._info)

    def _info(self, args, **extra_args):
        """Print freight forwarder info to the user.
        """
        if not isinstance(args, argparse.Namespace):
            raise logger.error(Exception("args should of an instance of argparse.Namespace"))

        logger.info("Freight Forwarder: {0}".format(VERSION))
        logger.info("docker-py: {0}".format(docker_py_version))
        logger.info("Docker Api: {0}".format(DOCKER_API_VERSION))
        logger.info("{0} version: {1}".format(platform.python_implementation(), platform.python_version()))
