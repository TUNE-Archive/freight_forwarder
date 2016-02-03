# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import
import factory

from freight_forwarder.registry import V2


class V2Factory(factory.Factory):
    class Meta:
        model = V2

    address = 'http://127.0.0.1:2376'
    kwargs = {}
