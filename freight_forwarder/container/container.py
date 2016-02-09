# -*- coding: utf-8; -*-
from __future__      import unicode_literals
from datetime        import datetime
from multiprocessing import Process, Queue
import time
import sys
import six
import signal
import dateutil.parser
import docker
from docker.errors import APIError

from ..utils import parse_stream, normalize_keys, capitalize_keys, logger
from .config import Config as ContainerConfig
from .host_config import HostConfig


class Container(object):
    """ This is a domain object that represents a docker container.
    """
    def __init__(self, client, name=None, image=None, id=None, container_config={}, host_config={}):
        if not isinstance(container_config, dict):
            raise TypeError('host_config needs to be of type dict.')

        if not isinstance(host_config, dict):
            raise TypeError('host_config needs to be of type dict.')

        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client, not: {0}".format(client))

        if not id and (not name or not image):
            raise AttributeError("Must provide name and image or id when instantiating the Container class.")

        self.client            = client
        self._transcribe       = False
        self._transcribe_queue = None
        self._transcribe_proc  = None
        self.config            = ContainerConfig(container_config)
        self.host_config       = HostConfig(host_config)

        if id:
            self._find_by_id(id)
        else:
            self._create_container(name, image)

    def __del__(self):
        if hasattr(self, '_transcribe_proc'):
            if self._transcribe_proc:
                self._transcribe_proc.terminate()

    @property
    def config(self):
        """
        """
        return self._config

    @config.setter
    def config(self, container_config):
        """
        """
        if not isinstance(container_config, ContainerConfig):
            raise TypeError("container_config must be an instance of Container.Config.")

        self._config = container_config

    @property
    def host_config(self):
        """
        """
        return self._host_config

    @host_config.setter
    def host_config(self, host_config):
        """
        """
        if not isinstance(host_config, HostConfig):
            raise TypeError("host_config must be an instance of HostConfig.")

        if host_config.log_config.get('type') != 'json-file':
            self._transcribe = True

        self._host_config = host_config

    def attach(self, stdout=True, stderr=True, stream=True, logs=False):
        """
        Keeping this simple until we need to extend later.
        """

        try:
            data = parse_stream(self.client.attach(self.id, stdout, stderr, stream, logs))
        except KeyboardInterrupt:
            logger.warning(
                "service container: {0} has been interrupted. "
                "The container will be stopped but will not be deleted.".format(self.name)
            )
            data = None
            self.stop()

        return data

    def commit(self, config, image_name, tag):
        """
        """
        logger.info('Committing changes from {0}.'.format(image_name), extra={'formatter': 'container', 'container': self.name})
        # TODO : Need to build some validation around this
        response = normalize_keys(self.client.commit(self.id, repository=image_name, conf=capitalize_keys(config), tag=tag))

        return response.get('id', False)

    def delete(self, remove_volumes=False, links=False, force=False):
        """
        """
        response = None
        if self.state()["running"]:
            self.stop()

        logger.info('is being deleted.', extra={'formatter': 'container', 'container': self.name})
        try:
            response = self.client.remove_container(self.id, remove_volumes, links, force)
        except APIError as e:
            if e.response.status_code == 404:
                logger.info('is unable to located.', extra={'formatter': 'container', 'container': self.name})
            else:
                raise APIError("Docker Error: {0}".format(e.explanation), e.response)

        return response

    def inspect(self):
        """
        """
        # TODO: build object and return self converted.
        return self.client.inspect_container(self.id)

    def output(self):
        output = self.client.logs(self.id, stdout=True, stderr=True, stream=False, timestamps=False, tail='all')

        return output

    def start(self, attach=False):
        """
        Start a container.  If the container is running it will return itself.

        returns a running Container.
        """
        if self.state()['running']:
            logger.info('is already running.', extra={'formatter': 'container', 'container': self.name})
            return True
        else:
            try:
                logger.info(
                    'is being started.', extra={'formatter': 'container', 'container': self.name}
                )

                # returns None on success
                self.client.start(self.id)
                if self._transcribe:
                    self.start_transcribing()

            except APIError as e:
                #
                # This is some bs... I assume that its needed because of dockers changes in 1.18 api.
                # I will resolve this next week when we stop passing properties to start.

                if e.response.status_code == 500:
                    self.client.start(self.id)
                else:
                    raise RuntimeError("Docker Error: {0}".format(e.explanation))

            if attach:
                self.attach()
                exit_code = self.wait()

            else:
                exit_code = self._wait_for_exit_code()

            return True if exit_code == 0 else False

    def start_transcribing(self):
        """

        :return:
        """
        if not self._transcribe:
            self._transcribe = True

        if self._transcribe_queue is None:
            self._transcribe_queue = Queue()

        if self._transcribe_proc is None:
            # add for debugging
            # print "Starting to record container output for {0}.".format(self.name)
            self._transcribe_proc = Process(target=self._start_recording, args=(self._transcribe_queue,))
            self._transcribe_proc.daemon = True
            self._transcribe_proc.start()

    def state(self):
        """
        {
            "State": {
                "ExitCode": 0,
                "FinishedAt": "2014-10-20T16:45:35.908823764Z",
                "Paused": false,
                "Pid": 774,
                "Restarting": false,
                "Running": true,
                "StartedAt": "2014-10-20T16:47:02.804735752Z"
            }
        }
        """
        response = normalize_keys(self.client.inspect_container(self.id))
        return response['state']

    def running(self):
        state = self.state()

        return state.get('running', False) if state else False

    def stop(self):
        """
        stop the container
        """
        logger.info('is being stopped', extra={'formatter': 'container', 'container': self.name})
        response = self.client.stop(self.id)

        while self.state()['running']:
            time.sleep(1)

        return response

    def wait(self):
        """
        probably want to come back and take a look at this guy.
        """
        response = self.client.wait(self.id)

        return response

    def dump_logs(self):
        """dump entirety of the container logs to stdout

            :returns None
        """
        msg = "log dump: \n"
        if self._transcribe:
            if self._transcribe_queue:
                while not self._transcribe_queue.empty():
                    logs = self._transcribe_queue.get()

                    if isinstance(logs, six.binary_type):
                        logs = logs.decode(encoding='UTF-8', errors="ignore")

                    msg = '{0} {1}'.format(msg, logs)
        else:
            logs = self.client.logs(self.id, stdout=True, stderr=True, stream=False, timestamps=False, tail='all')
            if isinstance(logs, six.binary_type):
                logs = logs.decode(encoding='UTF-8', errors="ignore")

            msg = '{0}{1}'.format(msg, logs)

        logger.error(msg)

    ###
    # Static methods
    ###
    @staticmethod
    def find_by_name(client, name):
        """
        """
        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client.")

        containers = {}

        try:
            response = client.containers(all=True)
            for container in response:
                container = normalize_keys(container)
                if 'names' in container and container["names"]:
                    # TODO: kind of a hack to fix the way name is coming back. look into patching the docker-py lib
                    for container_name in container['names']:
                        if container_name.count('/') is not 1:
                            continue

                        if name in container_name:
                            containers[container_name.replace('/', '')] = Container(client, id=container['id'])
        except Exception as e:
            raise e

        return containers

    ###
    # Private methods
    ##
    def _create_container(self, name, image):
        if name is None or not isinstance(name, six.string_types):
            raise TypeError("name cant be none and must be a string")

        if image is None or not isinstance(image, six.string_types):
            raise TypeError("image cant be none and must be a string")

        self.name          = name
        self._config.image = image
        self.image         = image

        logger.info("is being created.", extra={'formatter': 'container', 'container': self.name})
        host_config = self.client.create_host_config(**self._host_config.docker_py_dict())

        try:
            # docker.errors.APIError: 500 Server Error: Internal Server Error ("No command specified")
            response = normalize_keys(self.client.create_container(
                host_config=host_config,
                name=self.name,
                **self._config.docker_py_dict()
            ))

            if 'id' in response:
                self.id = response['id']

            self.created_at = datetime.utcnow()

            if 'warnings' in response and response['warnings']:
                self.warnings = response['warnings']
                for warning in self.warnings:
                    logger.warning(warning)

            self.client.close()
        except Exception as e:
            # docker.errors.APIError: 500 Server Error: Internal Server Error ("b'Could not get container for something'")

            # python 2.7
            # docker.errors.APIError: 409 Client Error: Conflict ("Conflict. The name
            # "itops-cia-couchdb-injector-builder" is already in use by container 035b9e1cdd7f.
            # You have to delete (or rename) that container to be able to reuse that name.")

            # python 3
            # docker.errors.APIError: 409 Client Error: Conflict ("b'Conflict. The name
            # "tune_platform-freight-forwarder-wheel-01" is already in use by container 4fa07acc188f. You have to delete
            # (or rename) that container to be able to reuse that name.'")
            raise e

    def _find_by_id(self, id):
        """
        Expected response:
                {
                     "Id": "4fa6e0f0c6786287e131c3852c58a2e01cc697a68231826813597e4994f1d6e2",
                     "Created": "2013-05-07T14:51:42.041847+02:00",
                     "Path": "date",
                     "Args": [],
                     "Config": {
                             "Hostname": "4fa6e0f0c678",
                             "User": "",
                             "Memory": 0,
                             "MemorySwap": 0,
                             "AttachStdin": false,
                             "AttachStdout": true,
                             "AttachStderr": true,
                             "PortSpecs": null,
                             "Tty": false,
                             "OpenStdin": false,
                             "StdinOnce": false,
                             "Env": null,
                             "Cmd": [
                                     "date"
                             ],
                             "Dns": null,
                             "Image": "base",
                             "Volumes": {},
                             "VolumesFrom": "",
                             "WorkingDir":""

                     },
                     "State": {
                             "Running": false,
                             "Pid": 0,
                             "ExitCode": 0,
                             "StartedAt": "2013-05-07T14:51:42.087658+02:01360",
                             "Ghost": false
                     },
                     "Image": "b750fe79269d2ec9a3c593ef05b4332b1d1a02a62b4accb2c21d589ff2f5f2dc",
                     "NetworkSettings": {
                             "IpAddress": "",
                             "IpPrefixLen": 0,
                             "Gateway": "",
                             "Bridge": "",
                             "PortMapping": null
                     },
                     "SysInitPath": "/home/kitty/go/src/github.com/docker/docker/bin/docker",
                     "ResolvConfPath": "/etc/resolv.conf",
                     "Volumes": {},
                     "HostConfig": {
                         "Binds": null,
                         "ContainerIDFile": "",
                         "LxcConf": [],
                         "Privileged": false,
                         "PortBindings": {
                            "80/tcp": [
                                {
                                    "HostIp": "0.0.0.0",
                                    "HostPort": "49153"
                                }
                            ]
                         },
                         "Links": ["/name:alias"],
                         "PublishAllPorts": false,
                         "CapAdd: ["NET_ADMIN"],
                         "CapDrop: ["MKNOD"]
                     }
                }
        """

        if not isinstance(id, six.string_types):
            raise TypeError('must supply a string as the id')

        # TODO: We should probably catch container not found error and return out own errors.
        response = normalize_keys(self.client.inspect_container(id))
        # TODO: normalize response to change - to _
        self.id          = response['id']
        self.name        = response['name'].replace('/', '')
        self.image       = response['image']
        # come back and figure the timezone stuff out later.
        self.created_at  = dateutil.parser.parse(response['created'], ignoretz=True)
        self.config      = ContainerConfig(response['config'])
        self.host_config = HostConfig(response['host_config'])

        if self._transcribe:
            self.start_transcribing()

    def _handler(self, signum=None, frame=None):
        # add for debugging
        # print 'Transcriber is being terminated with signum: {1}.\n'.format(self.name, signum)
        sys.exit(0)

    def _start_recording(self, queue):
        """
        """
        for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
            signal.signal(sig, self._handler)

        client = None
        try:
            if isinstance(self.client.verify, bool):
                tls_config = docker.tls.TLSConfig(
                    client_cert=self.client.cert,
                    verify=self.client.verify
                )
            else:
                tls_config = docker.tls.TLSConfig(
                    client_cert=self.client.cert,
                    ca_cert=self.client.verify
                )

            client = docker.Client(self.client.base_url, tls=tls_config, timeout=self.client.timeout, version=self.client.api_version)

            for line in client.attach(self.id, True, True, True, False):
                queue.put(line)
        finally:
            if isinstance(client, docker.Client):
                client.close()

    def _wait_for_exit_code(self, timer=10):
        """
        """
        exit_code = None

        # wait up to ten seconds for an exit code.
        for i in range(0, timer):
            time.sleep(1)
            container_state = self.state()
            exit_code = container_state['exit_code']

            if exit_code is None or exit_code == 0:
                if exit_code == 0 and i == 10:
                    break

                continue
            else:
                break

        return exit_code
