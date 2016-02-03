# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

import docker
import factory


class DockerClientFactory(factory.Factory):
    class Meta:
        model = docker.Client

    base_url = None
    version = None
    timeout = 20
    tls = False
