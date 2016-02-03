# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

import factory

from freight_forwarder.container_ship import Injector
from tests.factories.v2_factory import V2Factory


class InjectorFactory(factory.Factory):
    class Meta:
        model = Injector

    environment = 'development'
    data_center = 'local'
    project = 'test'
    registry = V2Factory()
    client_id = '123'
    client_secret = 'foo'
    injector_image = '123'
