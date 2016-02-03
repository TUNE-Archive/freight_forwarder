# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

import factory

from freight_forwarder.registry import V1, V2


class RegistryV1Factory(factory.Factory):
    class Meta:
        model = V1

    address = "http://v1.docker.io"


class RegistryV2Factory(factory.Factory):
    class Meta:
        model = V2

    address = "http://v2.docker.io"
