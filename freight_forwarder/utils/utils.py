# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import json
import os
import re
from time import sleep
from sys  import stdout

import six
from ipaddress import IPv4Address
from functools import wraps


from . import logger


def annotate(gen):
    prev_i, prev_val = 0, gen.next()

    for i, val in enumerate(gen, start=1):
        yield prev_i, prev_val
        prev_i, prev_val = i, val

    yield '-1', prev_val


def validate_uri(uri, scheme=True):
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', flags=re.IGNORECASE)

    if regex.match(uri):
        return uri
    else:
        raise(TypeError('%r is not a uri.' % uri))


def validate_path(path):
    if os.path.exists(path):
        return path
    else:
        raise(SystemError("{0} doesn't exist.".format(path)))


def is_valid_domain_name(domain_name):
    if len(domain_name) > 63:
        return False

    allowed = re.compile(r'[a-zA-Z\d-]{,63}(\.[a-zA-Z\d-]{,63})*', re.IGNORECASE)
    return allowed.match(domain_name)


def is_valid_hostname(hostname):
    if len(hostname) > 255:
        return False

    if hostname[-1] == ".":
        hostname = hostname[:-1]

    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def is_valid_ip(ip):
    is_valid = True

    if not isinstance(ip, six.string_types):
        is_valid = False
    else:
        try:
            IPv4Address(ip)
        except ValueError:
            is_valid = False

    return is_valid


def parse_hostname(uri):
    """
    This will parse the hostname and return it on match.  If no match is found it will raise a TypeError.
    :param uri:
    :return hostname:
    """""
    regex = re.compile(r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z]{2,}\.?)|'  # allow domain
                       r'localhost|'  # allow localhost
                       r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',  # allow ip
                       flags=re.IGNORECASE)

    match = regex.search(uri)

    if match:
        return match.group(0)
    else:
        raise TypeError("{0} doesn't contain a valid hostname.".format(uri))


def path_regex(path):
    """
    ^(\/{1}([a-zA-Z0-9\._-])*)(\/{1}([a-zA-Z0-9\._-])+)*(\/|([a-zA-Z0-9\._-])+)$
    """
    regex = re.compile(r'^((|\/{1})([a-zA-Z0-9\._-])*)(\/{1}([a-zA-Z0-9\._-])+)*(\/|([a-zA-Z0-9\._-])+)$')

    return regex.match(path)


def parse_http_scheme(uri):
    """
    match on http scheme if no match is found will assume http
    """
    regex = re.compile(
        r'^(?:http)s?://',
        flags=re.IGNORECASE
    )
    match = regex.match(uri)

    return match.group(0) if match else 'http://'


def retry(f):
    @wraps(f)
    def wrapped_f(*args, **kwargs):
        MAX_ATTEMPTS = 5
        for attempt in range(1, MAX_ATTEMPTS + 1):
            try:
                return f(*args, **kwargs)
            except Exception as e:

                msg = "Meta "
                if args:
                    msg += ', '.join([str(arg) for arg in args if callable(arg.__str__)])

                if kwargs:
                    msg += ', '.join(["{0}: {1}".format(key, value) for key, value in six.iteritems(kwargs)])

                if hasattr(e, 'message'):
                    if e.message:
                        try:
                            error, reason = e.message
                            msg += ' -  Error {0} - Reason {1}'.format(error, reason)
                        except Exception:
                            msg += ' -  Error {0}'.format(e.message)

                logger.warning("Attempt {0}/{1} - {2}".format(attempt, MAX_ATTEMPTS, msg))

                if attempt == MAX_ATTEMPTS:
                    raise LookupError("Max attempt limit reached.")

                sleep(3)

        logger.error("All {0} attempts failed : {1}".format(MAX_ATTEMPTS, msg))

    return wrapped_f


def parse_stream(response):
    """
    take stream from docker-py lib and display it to the user.

    this also builds a stream list and returns it.
    """
    stream_data = []
    stream = stdout

    for data in response:
        if data:
            try:
                data = data.decode('utf-8')
            except AttributeError as e:
                logger.exception("Unable to parse stream, Attribute Error Raised: {0}".format(e))
                stream.write(data)
                continue

            try:
                normalized_data = normalize_keys(json.loads(data))
            except ValueError:
                stream.write(data)
                continue
            except TypeError:
                stream.write(data)
                continue

            if 'progress' in normalized_data:
                stream_data.append(normalized_data)
                _display_progress(normalized_data, stream)

            elif 'error' in normalized_data:
                _display_error(normalized_data, stream)

            elif 'status' in normalized_data:
                stream_data.append(normalized_data)
                _display_status(normalized_data, stream)

            elif 'stream' in normalized_data:
                stream_data.append(normalized_data)
                _display_stream(normalized_data, stream)
            else:
                stream.write(data)

    stream.flush()
    return stream_data


# pre-compile regex
# there is a small bug in this where if you pass SomethingIs_Okay you will get two _ between is and okay
first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def find_key(key, var):
    if hasattr(var, 'iteritems'):
        for k, v in six.iteritems(var):
            if k == key:
                yield v
            if isinstance(v, dict):
                for result in find_key(key, v):
                    yield result
            elif isinstance(v, list):
                for d in v:
                    for result in find_key(key, d):
                        yield result


def normalize_keys(suspect, snake_case=True):
    """
    take a dict and turn all of its type string keys into snake_case
    """
    if not isinstance(suspect, dict):
        raise TypeError('you must pass a dict.')

    for key in list(suspect):
        if not isinstance(key, six.string_types):
            continue

        if snake_case:
            s1 = first_cap_re.sub(r'\1_\2', key)
            new_key = all_cap_re.sub(r'\1_\2', s1).lower()  # .replace('-', '_')
        else:
            new_key = key.lower()

        value = suspect.pop(key)
        if isinstance(value, dict):
            suspect[new_key] = normalize_keys(value, snake_case)
        elif isinstance(value, list):
            for i in range(0, len(value)):
                if isinstance(value[i], dict):
                    normalize_keys(value[i], snake_case)

            suspect[new_key] = value
        else:
            suspect[new_key] = value

    return suspect


def normalize_value(value, snake_case=True):
    """
    :param value:
    :return value:
    """
    if not isinstance(value, six.string_types):
        raise TypeError("the value passed to value must be a string")

    if snake_case:
        s1 = first_cap_re.sub(r'\1_\2', value)
        new_value = all_cap_re.sub(r'\1_\2', s1).lower()  # .replace('-', '_')
    else:
        new_value = value.lower()

    return new_value


def capitalize_keys(suspect):
    """
    :param suspect:
    :return new dict with capitalized keys:
    """
    if not isinstance(suspect, dict):
        raise TypeError('you must pass a dict.')

    converted = {}

    for key in list(suspect):
        if not isinstance(key, six.string_types):
            continue

        if key[0].isupper():
            continue

        if '_' in key:
            new_key = ''.join([chunk.capitalize() for index, chunk in enumerate(key.split('_'))])
        else:
            new_key = key.capitalize()

        value = suspect.get(key)
        if type(value) is dict:
            converted[new_key] = capitalize_keys(value)
        elif type(value) is list:
            converted[new_key] = [capitalize_keys(x) if isinstance(x, dict) else x for x in value]
        else:
            converted[new_key] = value

    return converted


def _display_progress(data, stream):
    """
    expecting the following data scheme:
        {
            u'status': u'Pushing',
            u'progressDetail': {
                                    u'current': 655337,
                                    u'start': 1413994898,
                                    u'total': 20412416
                                },
            u'id': u'51783549ce98',
            u'progress': u'[=>                                                 ] 655.3 kB/20.41 MB 30s'
        }

        {
            u'status': u'Buffering to disk',
            u'progressDetail': {
                                    u'current': 13369344,
                                    u'start': 1413994898
                               },
            u'id': u'51783549ce98',
            u'progress': u'13.37 MB'
        }
    """
    if type(data) is not dict:
        raise TypeError("data should be of type dict. the following was passed: {0}".format(data))

    stream.write("\r%s %s" % (data['status'], data['progress']))

    if 'Pushing' in data['status']:
        if data['progress_detail']['current'] == data['progress_detail'].get('total'):
            stream.write("\n")

    stream.flush()


def _display_error(normalized_data, stream):
    """
    print error message from docker-py stream and raise Exception.
    {
        u'message': u"Error getting container 981c3e17bfc6138d1985c0c8f5616e9064e56559e817646ad38211a456d6bcf2 from driver
        devicemapper: Error mounting '/dev/mapper/docker-8:3-34393696-981c3e17bfc6138d1985c0c8f5616e9064e56559e817646ad38211a456d6bcf2'
        on '/data/docker/devicemapper/mnt/981c3e17bfc6138d1985c0c8f5616e9064e56559e817646ad38211a456d6bcf2': no such file
        or directory"
    }

    """
    # TODO: need to revisit this later.
    error = normalized_data['error']
    if 'error_detail' in normalized_data:
        stream.write("exit code: {0}\n".format(normalized_data['error_detail'].get('code'),
                                               'There was no exit code provided'))

        stream.write(normalized_data['error_detail'].get('message', 'There were no message details provided.'))

    raise DockerStreamException(error)


def _display_status(normalized_data, stream):
    """
    print status message from docker-py stream.
    """
    if 'Pull complete' in normalized_data['status'] or 'Download complete' in normalized_data['status']:
        stream.write("\n")

    if 'id' in normalized_data:
        stream.write("%s - " % normalized_data['id'])

    stream.write("{0}\n".format(normalized_data['status']))


def _display_stream(normalized_data, stream):
    """
    print stream message from docker-py stream.
    """
    try:
        stream.write(normalized_data['stream'])
    except UnicodeEncodeError:
        stream.write(normalized_data['stream'].encode("utf-8"))


class DockerStreamException(Exception):
    def __init__(self, message):
        self.message = message
        super(DockerStreamException, self).__init__(self.message)

    def __str__(self):
        return super(DockerStreamException, self).__str__()
