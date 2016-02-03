# -*- coding: utf-8; -*-
from __future__ import unicode_literals

import factory

from freight_forwarder.image import Image
from tests.factories.docker_client_factory import DockerClientFactory


class ImageFactory(factory.Factory):
    class Meta:
        model = Image

    client = DockerClientFactory()
    identifier = 'foo'
