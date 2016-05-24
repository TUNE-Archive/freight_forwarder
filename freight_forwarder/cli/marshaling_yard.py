# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import argparse
import six

from freight_forwarder.utils    import logger
from freight_forwarder.config   import Config
from freight_forwarder.registry import Registry


class MarshalingYardCommand(object):
    """ MarshalingYard interacts with a docker registry and provides information concerning the images and tags.

      - ``--alias``        (optional) - The registry alias defined in freight-forwarder config file. defaults: 'default'.

      One of the options is required

      - ``search``         Searches defined registry with keyword
      - ``tags``           Returns tag associated with value provided from the specified registry

    :return: exit_code
    :rtype: integer

    """
    def __init__(self, sub_parser):
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception("parser should of an instance of argparse._SubParsersAction")

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('marshaling-yard')
        self._build_arguments()
        self._add_additional_sub_commands()

    def _add_additional_sub_commands(self):
        sub_parser = self._parser.add_subparsers(
            title='marshaling-yard',
            description='command to interact with docker registries',
            help='additional help'
        )
        # add search sub command.
        MarshalingYardSearch(sub_parser)

        # add tags sub command.
        MarshalingYardTags(sub_parser)

    def _build_arguments(self):
        """
        build arguments for command.
        """
        self._parser.add_argument(
            '-a', '--alias',
            required=False,
            default='default',
            type=str,
            help='registry alias created in freight-forwarder.yml. Example: tune_dev'
        )


class MarshalingYardTags(object):

    def __init__(self, sub_parser):
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception("parser should of an instance of argparse.ArgumentParser")

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('tags')
        self._build_arguments()
        self._parser.set_defaults(func=self._tags)

    def _build_arguments(self):
        """
        build arguments for command.
        """
        self._parser.add_argument(
            'image_name',
            metavar='IMAGE_NAME',
            type=six.text_type,
            help='Name of the image example: \"namespace/repository\"'
        )

    def _tags(self, args, **extra_args):
        # create config
        config = Config(verbose=args.verbose)

        # validate config file
        config.validate()

        # create registries
        registries = _create_registries(config.get('registries'))

        marshaling_yard = registries.get(args.alias)

        if not marshaling_yard:
            raise LookupError('was unable to find a registry aliased: {0} in the configuration file.'.format(args.alias))

        logger.info('From: {0}'.format(marshaling_yard.location))
        for tag in marshaling_yard.tags(args.image_name):
            logger.info(tag)

    def _delete(self, args, **extra_args):
        """
        Export is the entry point for exporting docker images.
        """
        raise NotImplementedError

        # if not isinstance(args, argparse.Namespace):
        #     raise Exception("args should of an instance of argparse.Namespace")
        #
        # # create new freight forwarder to create a commercial_invoice and export goods.
        # freight_forwarder = FreightForwarder()
        #
        # # create commercial_invoice
        # commercial_invoice = freight_forwarder.commercial_invoice(
        #     'export',
        #     args.data_center,
        #     args.environment,
        #     args.service
        # )
        #
        # bill_of_lading = None
        #
        # transport_service = commercial_invoice.transport_service
        # if transport_service:
        #     marshaling_yard = commercial_invoice.transport_service.destination_registry
        #
        #     repository = "{0}-{1}".format(freight_forwarder.project, args.service)
        #     tag        = "{0}-{1}-{2}".format(commercial_invoice.data_center, commercial_invoice.environment, args.tag)
        #     try:
        #         logger.info("Attempting to delete image for service: {0} tagged: {1}".format(repository, tag))
        #         bill_of_lading = marshaling_yard.delete_tag(freight_forwarder.team, repository, tag)
        #         logger.info("Tag was successfully deleted.")
        #     except Exception as e:
        #         logger.error(e.message)
        #         bill_of_lading = False
        #
        # # pretty lame... Need to work on return values through to app to make them consistent.
        # exit_code = 0 if bill_of_lading else 1
        #
        # if exit_code != 0:
        #     exit(exit_code)


class MarshalingYardSearch(object):
    def __init__(self, sub_parser):
        if not isinstance(sub_parser, argparse._SubParsersAction):
            raise Exception("parser should of an instance of argparse.ArgumentParser")

        # Set up export parser and pass Export class to function call.
        self._parser = sub_parser.add_parser('search')
        self._build_arguments()
        self._parser.set_defaults(func=self._images)

    def _build_arguments(self):
        """
        build arguments for command.
        """
        self._parser.add_argument(
            'terms',
            metavar='TERMS',
            type=six.text_type,
            help='Search terms.  search by namespace or repository. expected formats: '
                 '\"namespace\" or \"repository\" or \"namespace/repository\"'
        )

    def _images(self, args, **extra_args):
        # create config
        config = Config(verbose=args.verbose)

        # validate config file
        config.validate()

        # create registries
        registries = _create_registries(config.get('registries'))

        marshaling_yard = registries.get(args.alias)

        if not marshaling_yard:
            raise LookupError('was unable to find a registry aliased: {0} in the configuration file.'.format(args.alias))

        logger.info('Images:')
        for match in marshaling_yard.search(args.terms):
            logger.info(match)


def _create_registries(registries_meta):
    """
    """
    registries = {'docker_hub': Registry()}

    if registries_meta is None:
        logger.warning("There were no registries defined. Defaulting to Docker hub.")
        return registries
    elif isinstance(registries_meta, dict):
        registries.update({alias: Registry(**registry) for alias, registry in six.iteritems(registries_meta)})
    else:
        raise TypeError(logger.error("registries must be a dict"))

    if 'default' not in registries:
        logger.warning("There was not default registry defined. Default will be Docker hub.")

    return registries
