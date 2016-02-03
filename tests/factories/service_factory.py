# -*- coding: utf-8; -*-
from __future__ import unicode_literals

import factory

from freight_forwarder.commercial_invoice.service import Service


class ServiceFactory(factory.Factory):
    class Meta:
        model = Service

    repository       = 'teamexample'
    namespace        = 'appexample-api:asxkl8'
    name             = 'api'
    alias            = 'teamexample-appexample-api'
    container_config = None
    docker_file      = None
    host_config      = None
    source_tag       = None
    test_docker_file = None
    source_registry  = None
    destination_registry = None
