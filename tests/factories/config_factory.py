# -*- coding: utf-8; -*-
from __future__ import unicode_literals, absolute_import

import factory

from freight_forwarder.container.config import Config


class ConfigFactory(factory.Factory):
    class Meta:
        model = Config

    attach_stderr    = False
    attach_stdin     = False
    attach_stdout    = False
    cmd              = None
    domain_name      = ''
    entry_point      = None
    env              = {}
    exposed_ports    = {}
    hostname         = ''
    image            = ''
    labels           = {}
    network_disabled = False
    open_stdin       = False
    stdin_once       = True
    tty              = False
    user             = ''
    volumes          = {}
    working_dir      = ''
    detach           = False
