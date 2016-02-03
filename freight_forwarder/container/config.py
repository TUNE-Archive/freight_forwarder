# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import six
import shlex

from freight_forwarder.utils import is_valid_hostname, is_valid_domain_name


class Config(object):
    def __init__(self, properties={}):
        """
        "Config": {
            "AttachStderr": true,
            "AttachStdin": false,
            "AttachStdout": true,
            "Cmd": [
                "/bin/sh",
                "-c",
                "exit 9"
            ],
            "Domainname": "",
            "Entrypoint": null,
            "Env": [
                "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
            ],
            "ExposedPorts": null,
            "Hostname": "ba033ac44011",
            "Image": "ubuntu",
            "Labels": {
                "com.example.vendor": "Acme",
                "com.example.license": "GPL",
                "com.example.version": "1.0"
            },
            "MacAddress": "",
            "NetworkDisabled": false,
            "OnBuild": null,
            "OpenStdin": false,
            "PortSpecs": null,
            "StdinOnce": false,
            "Tty": false,
            "User": "",
            "Volumes": null,
            "WorkingDir": ""
        }
        """
        self.attach_stderr    = properties.get('attach_stderr', False)
        self.attach_stdin     = properties.get('attach_stdin', False)
        self.attach_stdout    = properties.get('attach_stdout', False)
        self.cmd              = properties.get('cmd') or properties.get('command', None)
        self.domain_name      = properties.get('domain_name', '') or properties.get('domainname', '')
        self.entry_point      = properties.get('entry_point') or properties.get('entrypoint', None)
        self.env              = properties.get('env') or properties.get('env_vars', {})
        self.exposed_ports    = properties.get('exposed_ports', {})
        self.hostname         = properties.get('hostname', '')
        self.image            = properties.get('image', '')
        self.labels           = properties.get('labels', {})
        self.network_disabled = properties.get('network_disabled', False)
        self.open_stdin       = properties.get('open_stdin', False)
        self.stdin_once       = properties.get('stdin_once', True)
        self.tty              = properties.get('tty', False)
        self.user             = properties.get('user', '')
        self.volumes          = properties.get('volumes', {})
        self.working_dir      = properties.get('working_dir', '')
        # helper properties to make attaching and detaching easy
        self.detach           = properties.get('detach', False)

        # TODO: come back at a later date to add as needed
        # self._port_specs      = properties.get('port_specs', None)
        # self._on_build        = properties.get('on_build', None)
        # self._mac_address     = properties.get('mac_address', None)

    def to_dict(self):
        return dict([(name, getattr(self, name)) for name in dir(self) if not name.startswith('_') and not callable(getattr(self, name))])

    def docker_py_dict(self):
        """Convert object to match valid docker-py properties.
        """
        return {
            'image': self.image,
            'command': self.cmd,
            'hostname': self.hostname,
            'user': self.user,
            'detach': self.detach,
            'stdin_open': self.open_stdin,
            'tty': self.tty,
            'ports': self.exposed_ports,
            'environment': self.env,
            'volumes': self.volumes,
            'network_disabled': self.network_disabled,
            'entrypoint': self.entry_point,
            'working_dir': self.working_dir,
            'domainname': self.domain_name,
            'labels': self.labels
        }

    @property
    def attach_stderr(self):
        return self._attach_stderr

    @attach_stderr.setter
    def attach_stderr(self, value):
        """
        """
        if not isinstance(value, bool):
            raise TypeError("attach_stderr must be of type bool.  {0} was passed.".format(type(value)))

        if value:
            self.detach = False

        self._attach_stderr = value

    @property
    def attach_stdin(self):
        return self._attach_stdin

    @attach_stdin.setter
    def attach_stdin(self, value):
        """
        """
        if not isinstance(value, bool):
            raise TypeError("attach_stdin must be of type bool.  {0} was passed.".format(type(value)))

        if value:
            self.detach = False

        self._attach_stdin = value

    @property
    def attach_stdout(self):
        return self._attach_stdout

    @attach_stdout.setter
    def attach_stdout(self, value):
        """
        """
        if not isinstance(value, bool):
            raise TypeError("attach_stdout must be of type bool.  {0} was passed.".format(type(value)))

        if value:
            self.detach = False

        self._attach_stdout = value

    @property
    def command(self):
        return self.cmd

    @command.setter
    def command(self, value):
        self.cmd = value

    @property
    def cmd(self):
        return self._cmd

    @cmd.setter
    def cmd(self, value):
        """
        """
        if isinstance(value, list):
            for part in value:
                if not isinstance(part, six.string_types):
                    raise TypeError("every value in the cmd list needs to be a string.")

            self._cmd = value
        elif isinstance(value, six.string_types):
            self._cmd = shlex.split(value)
        elif value is None:
            self._cmd = value
        else:
            raise TypeError("cmd must be a None, str, or list.")

    @property
    def detach(self):
        return self._detach

    @detach.setter
    def detach(self, value):
        """
        """
        if not isinstance(value, bool):
            raise TypeError("detach must be of type bool.  {0} was passed.".format(type(value)))

        self._detach = value

        if self._detach:
            self.attach_stdout = False
            self.attach_stderr = False
            self.stdin_once    = False
            self.attach_stdin  = False

    @property
    def domain_name(self):
        return self._domain_name

    @domain_name.setter
    def domain_name(self, domain_name):
        """
        """
        if not isinstance(domain_name, six.string_types):
            raise TypeError("domain_name must be a string.  {0} was passed.".format(type(domain_name)))

        if domain_name and not is_valid_domain_name(domain_name):
            raise ValueError("{0} isn't a valid domain_name").format(domain_name)
        else:
            self._domain_name = domain_name

    @property
    def entry_point(self):
        return self._entry_point

    @entry_point.setter
    def entry_point(self, value):
        if isinstance(value, list):
            for part in value:
                if not isinstance(part, six.string_types):
                    raise TypeError("every value in the entry_point list needs to be a string")

            self._entry_point = value
        elif isinstance(value, six.string_types):
            self._entry_point = shlex.split(value)

        elif value is None:
            self._entry_point = value
        else:
            raise TypeError("entry_point must be a None, str, or list.")

        self._entry_point = value

    @property
    def environment(self):
        return self.env

    @environment.setter
    def environment(self, environment):
        self.env = environment

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, env_vars):
        """
        """
        if isinstance(env_vars, list):
            for env_var in env_vars:
                if not isinstance(env_var, six.string_types):
                    raise TypeError("When passing environment variables in a list each value must be a str.")

                if '=' not in env_var:
                    raise AttributeError(
                        "When passing environment variables in a list they must be in the following format: KEY=VALUE"
                    )

            self._env = env_vars
        elif isinstance(env_vars, dict):
            env_list = []

            for key, value in six.iteritems(env_vars):
                env_list.append("{0}={1}".format(key, value))

            self._env = env_list
        else:
            raise TypeError('environment variables must be a list or dict.')

    def merge_env(self, env):
        """
        :param env:
        :return:
        """
        # convert to dict to allow update
        current_env = dict(item.split('=') for item in self._env)

        # do validation and set new values.
        self.env = env

        # convert to dict to allow update
        new_env = dict(item.split('=') for item in self._env)

        # update old with new
        current_env.update(new_env)

        # apply updated values
        self.env = current_env

    @property
    def env_vars(self):
        """
        """
        return self.env

    @env_vars.setter
    def env_vars(self, value):
        """
        """
        self.env = value

    @property
    def exposed_ports(self):
        return self._exposed_ports

    @exposed_ports.setter
    def exposed_ports(self, value):
        """
        """
        self._exposed_ports = {}

        if value is None:
            self._exposed_ports = None
        elif isinstance(value, list):
            for port in value:
                self._exposed_ports[self._get_valid_port(port)] = {}

        elif isinstance(value, dict):
            for port, port_obj in six.iteritems(value):
                if not isinstance(port_obj, dict) or port_obj:
                    raise ValueError("port object must be an empty dict. {0} was passed".format(port_obj))

                self._exposed_ports[self._get_valid_port(port)] = port_obj
        else:
            raise TypeError("exposed_ports must be a list, dict, or None.")

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, hostname):
        """ hostname setter

        """
        if not isinstance(hostname, six.string_types):
            raise TypeError("hostname must be a string.  {0} was passed.".format(type(hostname)))

        # if a host name is passed and its not valid raise else set hostname empty strings are the docker default.
        if hostname and not is_valid_hostname(hostname):
            raise ValueError("{0} isn't a valid hostname").format(hostname)
        else:
            self._hostname = hostname

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        if not isinstance(value, six.string_types):
            raise TypeError("image must be a str.")

        # TODO: add more specific validation ie ubuntu  itops/cia  etc.
        self._image = value

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, value):
        """
        """
        if value is None:
            self._labels = value
        elif isinstance(value, dict):
            for label_key, label_value in six.iteritems(value):
                if not isinstance(label_key, six.string_types) or not isinstance(label_value, six.string_types):
                    raise TypeError("the labels dict must key and value must both be strings.")

            self._labels = value
        else:
            raise TypeError('labels can only be a dict or None.')

    @property
    def network_disabled(self):
        return self._network_disabled

    @network_disabled.setter
    def network_disabled(self, value):
        if not isinstance(value, bool):
            raise TypeError("network_disabled must be a bool.")

        self._network_disabled = value

    @property
    def open_stdin(self):
        return self._open_stdin

    @open_stdin.setter
    def open_stdin(self, value):
        if not isinstance(value, bool):
            raise TypeError("open_stdin must be of type bool.  {0} was passed.".format(type(value)))

        if value:
            self._stdin_once   = True
            self._attach_stdin = True
            self.detach = False

        self._open_stdin = value

    @property
    def stdin_once(self):
        return self._stdin_once

    @stdin_once.setter
    def stdin_once(self, value):
        if not isinstance(value, bool):
            raise TypeError("stdin_once must be of type bool.  {0} was passed.".format(type(value)))

        self._stdin_once = value

    @property
    def tty(self):
        return self._tty

    @tty.setter
    def tty(self, tty):
        if not isinstance(tty, bool):
            raise TypeError("tty must be of type bool.  {0} was passed.".format(type(tty)))

        self._tty = tty

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, user):
        """
        """
        if not isinstance(user, six.string_types):
            raise TypeError("user must be a string. {0} was passed.".format(type(user)))

        self._user = user

    @property
    def volumes(self):
        return self._volumes

    @volumes.setter
    def volumes(self, value):
        """
        """
        if value is None:
            self._volumes = None
        elif isinstance(value, list):
            self._volumes = {}
            for volume in value:
                # TODO: validate path not existence but unix filesystem syntax
                if not isinstance(volume, six.string_types):
                    raise TypeError("each volume must be a string. {0} was passed.".format(type(volume)))

                self._volumes[volume] = {}

        elif isinstance(value, dict):
            for volume, volume_obj in six.iteritems(value):
                if not isinstance(volume, six.string_types):
                    raise TypeError("each volume key must be a string. {0} was passed.".format(type(volume)))

                if not isinstance(volume_obj, dict):
                    raise TypeError("volumes values must be dict. {0} was passed".format(type(volume_obj)))

                if volume_obj:
                    raise AttributeError("volume value must be an empty dict. {0} was passed".format(volume_obj))

            self._volumes = value

        else:
            raise TypeError("volumes must be a dict, list, or None")

    @property
    def working_dir(self):
        return self._working_dir

    @working_dir.setter
    def working_dir(self, value):
        """
        """
        # TODO: validate path not existence but unix filesystem syntax
        if not isinstance(value, six.string_types):
            raise TypeError("working dir must be a string. {0} was passed.".format(type(value)))

        self._working_dir = value

    ##
    # static methods
    ##
    @classmethod
    def allowed_config_attributes(cls):
        return tuple(six.text_type(name) for name in dir(cls) if not name.startswith('_') and not callable(getattr(cls, name)))

    ###
    # private methods
    ##
    def _get_valid_port(self, port):
        """
        :param port:
        :return "port/protocol":
        """
        if '/' in port:
            port, protocol = port.split('/')
        else:
            protocol = 'tcp'

        try:
            int(port)
        except ValueError:
            raise ValueError("{0} isn't a valid port number.".format(port))

        if protocol not in ('tcp', 'udp'):
            raise ValueError("exposed ports only supports udp or tcp. {0} was passed".format(protocol))

        return "{0}/{1}".format(port, protocol)
