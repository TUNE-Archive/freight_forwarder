# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import os

import logging
import logging.config
import six


CONFIG = {
    "version": 1,
    "formatters": {
        "default": {
            "format": "%(message)s"
        },
        "cli-error": {
            "format": "$magenta%(levelname)s$reset - $intense_green%(message)s$reset"
        },
        "cli-warning": {
            "format": "$intense_yellow%(levelname)s$reset - %(message)s"
        },

        "config-failure": {
            "format": " $intense_red\u2715$reset %(message)s"
        },

        "config-message": {
            "format": " %(message)s"
        },

        "config-success": {
            "format": " $intense_green\u2713$reset %(message)s"
        },

        "config-start": {
            "format": "\u2605 %(message)s \u2605"
        },

        "container": {
            "format": "$intense_blue%(container)s$reset -$intense_red*$reset- %(message)s"
        },
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },

    'handlers': {
        "cli": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout"
        },
        "cli-error": {
            "class": "logging.StreamHandler",
            "level": "ERROR",
            "formatter": "cli-error",
            "stream": "ext://sys.stdout"
        },

        "cli-warning": {
            "class": "logging.StreamHandler",
            "level": "WARNING",
            "formatter": "cli-warning",
            "stream": "ext://sys.stdout"
        },
    },
    "loggers": {
        "cli": {
            "level": "DEBUG",
            "handlers": ["cli", 'cli-error', 'cli-warning'],
            "propagate": False
        }
    },
    "root": {
        "level": "DEBUG"
    }
}

LEVELS = (
    'CRITICAL',
    'ERROR',
    'WARN',
    'WARNING',
    'INFO',
    'DEBUG',
    'NOTSET'
)

COLORS = (
    'black',
    'red',
    'green',
    'yellow',
    'blue',
    'magenta',
    'cyan',
    'white'
)

TYPOGRAPHY = {
    'reset': 0,
    'bold_on': 1,
    'bold_off': 22
}

globals()['ansi_codes'] = {}


def ansi(code, intense=False):
    prefix = "\033["
    if intense:
        prefix = "{0}1;".format(prefix)

    return "{0}{1}m".format(prefix, code)

for key, value in six.iteritems(TYPOGRAPHY):
    globals()['ansi_codes'][key] = ansi(value)

for i, color in enumerate(COLORS):
    globals()['ansi_codes'][color] = ansi(30 + i)
    globals()['ansi_codes']["intense_{0}".format(color)] = ansi(30 + i, intense=True)

_logger = logging.getLogger()


class ConfigFilter(logging.Filter):
    def filter(self, log_record):
        if hasattr(log_record, 'config'):
            return True
        else:
            return False


class CliWarningFilter():
    def filter(self, log_record):
        if log_record.levelno == 30:
            return True

        return False


class CliFilter(logging.Filter):
    def filter(self, log_record):
        if log_record.levelno >= 30:
            return False

        return True


class ColorFormatter(logging.Formatter):
    def __init__(self, msg, color=True):
        self.color = color

        logging.Formatter.__init__(self, self.set_color(msg))

    def set_color(self, msg):
        if self.color and "$" in msg:
            for name, code in six.iteritems(ansi_codes):
                msg = msg.replace("${0}".format(name), code)

        return msg

    def format(self, record):
        default_format = self._fmt

        if hasattr(record, 'formatter'):
            formatter = CONFIG['formatters'].get(record.formatter)
            if formatter:
                self.__set_fmt(self.set_color(formatter['format']))

        # TODO: validate container
        if hasattr(record, 'prefix'):
            if record.prefix is not None:
                self.__set_fmt('{0}{1}'.format(record.prefix, self._fmt))

        result = logging.Formatter.format(self, record)
        self.__set_fmt(default_format)

        return result

    def __set_fmt(self, fmt):
        if hasattr(self, '_style'):
            self._style._fmt = fmt

        self._fmt = fmt


def setup_logging(name):
    global _logger

    if 'handlers' in CONFIG:
        for handler in CONFIG['handlers'].values():
            if 'File' in handler['class']:
                handler['filename'] = os.path.join(os.path.dirname(__file__), 'logs', handler['filename'])

    logging.config.dictConfig(CONFIG)

    if name and name in CONFIG.get('handlers', {}):
        _logger = logging.getLogger(name)

        for handler in _logger.handlers:

            formatter_name = CONFIG['handlers'][handler.name]['formatter']
            fmt = CONFIG['formatters'][formatter_name]['format']

            handler.setFormatter(ColorFormatter(fmt))

            if handler.name == 'cli-warning':
                handler.addFilter(CliWarningFilter())

            if handler.name == 'cli':
                handler.addFilter(CliFilter())

    else:
        raise LookupError("Was unable to set up handler for {0}.".format(name))


def exception(msg, *args, **kwargs):
    _logger.exception(msg, *args, **kwargs)


def critical(msg, *args, **kwargs):
    _logger.critical(msg, *args, **kwargs)


def fatal(msg, *args, **kwargs):
    _logger.fatal(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    _logger.error(msg, *args, **kwargs)
    return msg


def warning(msg, *args, **kwargs):
    _logger.warning(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    _logger.info(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    _logger.debug(msg, *args, **kwargs)


def set_level(level):
    if not isinstance(level, six.string_types):
        raise TypeError('level must be a string.')

    level = level.upper()
    if level not in LEVELS:
        raise LookupError('was unable to find level: {0} in {1}'.format(level, ', '.join(LEVELS)))

    level = logging.getLevelName(level)
    _logger.setLevel(level)


def get_level():
    return logging.getLevelName(_logger.level)
