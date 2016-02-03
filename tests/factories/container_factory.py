# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

import dateutil
import factory

from freight_forwarder.container.container import Container

from .config_factory import ConfigFactory
from .docker_client_factory import DockerClientFactory
from .host_config_factory   import HostConfigFactory


class ContainerFactory(factory.Factory):
    class Meta:
        model = Container

    id               = '123'
    name             = 'foo'
    image            = 'bar'
    created_at       = dateutil.parser.parse('2016-01-01T14:51:42.041847+02:00', ignoretz=True)
    client           = DockerClientFactory
    transcribe       = False
    transcribe_queue = None
    transcribe_proc  = None
    config           = ConfigFactory
    host_config      = HostConfigFactory
