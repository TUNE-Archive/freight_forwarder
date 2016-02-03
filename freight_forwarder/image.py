# -*- coding: utf-8; -*-
from __future__ import unicode_literals
import os
import docker
import dateutil.parser
import six

from .utils            import parse_stream, normalize_keys, retry, logger
from .registry         import V1, V2
from .container.config import Config as ContainerConfig


class Image(object):

    def __init__(self, client, identifier):
        """
        """
        if not isinstance(client, docker.Client):
            raise Exception("client must be and instance of the docker client")

        self.client = client

        if not isinstance(identifier, six.string_types):
            raise TypeError("image identifier needs to be of type string.")

        self.identifier = identifier
        self.repo_tags = ()
        self._inspect_and_map(identifier)

    def push(self, registry, repository_tag, tag=None):
        """
        """
        if not registry and not isinstance(registry, (V1, V2)):
            raise Exception("Must pass an a sea port object to push the image to.")

        if not isinstance(repository_tag, six.string_types):
            raise TypeError('repository_tag must be a string')

        repository_tag = "{0}/{1}".format(registry.location, repository_tag)
        if ':' not in repository_tag and tag is not None:
            repository_tag = "{0}:{1}".format(repository_tag, tag)

        if registry.ping():
            if repository_tag not in self.repo_tags:
                self.tag(repository_tag)

            parse_stream(self.client.push(repository_tag, stream=True))
            self.client.close()
        else:
            raise Exception("Unable to locate registry @ {}.".format(registry.location))

    def tag(self, repository_tag, tags=[]):
        """
        Tags image with one or more tags.

        Raises exception on failure.
        """
        if not isinstance(repository_tag, six.string_types):
            raise TypeError('repository_tag must be a string')

        if not isinstance(tags, list):
            raise TypeError('tags must be a list.')

        if ':' in repository_tag:
            repository, tag = repository_tag.split(':')
            tags.append(tag)
        else:
            repository = repository_tag

            if not tags:
                tags.append('latest')

        for tag in tags:
            repo_tag = "{0}:{1}".format(repository, tag)

            if repo_tag not in self.repo_tags:
                logger.info("Tagging Image: {0} Repo Tag: {1}".format(self.identifier, repo_tag))
                self.repo_tags = self.repo_tags + (repo_tag, )

                # always going to force tags until a feature is added to allow users to specify.
                try:
                    self.client.tag(self.id, repository, tag)
                except:
                    self.client.tag(self.id, repository, tag, force=True)

    def delete(self, force=False, noprune=False):
        logger.info("deleting image: {0}".format(self.identifier))

        try:
            response = self.client.remove_image(self.id, force, noprune)
        except:
            # dont want to fail if we cant delete.
            logger.info("Couldn't delete image: {0}.".format(self.id))
            return False

        return False if response else True

    def _inspect_and_map(self, identifier):
        """
        example response:
            {
                u'comment': u'',
                u'virtual_size': 566087127,
                u'container': u'a2ea130e8c7a945823c804253c20f7c877376c69a36311a0cc614d5c455f645f',
                u'os': u'linux',
                u'parent': u'14e75a5684c2fabb7db24d92bdda09d11da1179a7d86ab4c9640ef70d1fd4082',
                u'author': u'alexb@tune.com',
                u'checksum': u'tarsum.dev+sha256:1b755912c77197c6a43539f2a708ef89d5849b8ce02642cb702e47afaa8195c3',
                u'created': u'2014-10-16T23:41:25.445801849Z',
                u'container_config': {
                    u'tty': False,
                    u'on_build': [],
                    u'domainname': u'',
                    u'attach_stdin': False,
                    u'image': u'14e75a5684c2fabb7db24d92bdda09d11da1179a7d86ab4c9640ef70d1fd4082',
                    u'port_specs': None,
                    u'hostname': u'2c1b05d4dd63',
                    u'mac_address': u'',
                    u'working_dir': u'',
                    u'entrypoint': [u'/usr/local/bin/dockerjenkins.sh'],
                    u'env': [
                            u'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                            u'REFRESHED_AT=2014-10-14',
                            u'JENKINS_HOME=/opt/jenkins/data',
                            u'JENKINS_MIRROR=http://mirrors.jenkins-ci.org'
                    ],
                    u'memory': 0,
                    u'attach_stdout': False,
                    u'exposed_ports': {
                        u'8080/tcp': {}
                    },
                    u'stdin_once': False,
                    u'cpuset': u'',
                    u'user': u'',
                    u'network_disabled': False,
                    u'memory_swap': 0,
                    u'attach_stderr': False,
                    u'cmd': [
                        u'/bin/sh',
                        u'-c',
                        u'#(nop) ENTRYPOINT [/usr/local/bin/dockerjenkins.sh]'
                    ],
                    u'open_stdin': False,
                    u'volumes': {
                        u'/var/lib/docker': {}
                    },
                    u'cpu_shares': 0
                },
                u'architecture': u'amd64',
                u'docker_version': u'1.3.0',
                u'config': {
                    u'tty': False,
                    u'on_build': [],
                    u'domainname': u'',
                    u'attach_stdin': False,
                    u'image': u'14e75a5684c2fabb7db24d92bdda09d11da1179a7d86ab4c9640ef70d1fd4082',
                    u'port_specs': None,
                    u'hostname': u'2c1b05d4dd63',
                    u'mac_address': u'',
                    u'working_dir': u'',
                    u'entrypoint': [u'/usr/local/bin/dockerjenkins.sh'],
                    u'env': [
                        u'PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin',
                        u'REFRESHED_AT=2014-10-14',
                        u'JENKINS_HOME=/opt/jenkins/data',
                        u'JENKINS_MIRROR=http://mirrors.jenkins-ci.org'
                    ],
                    u'memory': 0,
                    u'attach_stdout': False,
                    u'exposed_ports': {
                        u'8080/tcp': {}
                    },
                    u'stdin_once': False,
                    u'cpuset': u'',
                    u'user': u'',
                    u'network_disabled': False,
                    u'memory_swap': 0,
                    u'attach_stderr': False,
                    u'cmd': None,
                    u'open_stdin': False,
                    u'volumes': {
                        u'/var/lib/docker': {}
                    },
                    u'cpu_shares': 0
                },
                u'id': u'd37e267af092e02aaab68e962fadcc1107a3b42a34b0c581ee1e3a54aed62ad4',
                u'size': 0
            }
        """
        # validate
        try:
            response = normalize_keys(self.client.inspect_image(identifier))

            self.comment = response['comment'] if response['comment'] else None
            self.id = response["id"]
            self.virtual_size = response['virtual_size']
            self.container = response['container']
            self.os = response['os']
            self.parent = response['parent']
            self.author = response.get('author', None)
            self.created_at = self.created_at = dateutil.parser.parse(response['created'], ignoretz=True)
            self.architecture = response['architecture']
            self.docker_version = response['docker_version']
            self.size = response['size']
            self.container_config = ContainerConfig(response.get('container_config')) if response.get('config') else ContainerConfig()
            self.config = ContainerConfig(response.get('config')) if response.get('config') else ContainerConfig()

        except Exception as e:
            raise e

    # Static methods
    @staticmethod
    def all(client, filters=None):
        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client.")

        images = {}

        response = client.images(all=True, filters=filters)

        for image in response:
            image = normalize_keys(image)

            if image['id'] not in images:
                images[image['id']] = Image(client, image['id'])
            continue

        return images

    @staticmethod
    def find_by_name(client, name):
        """
        """
        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client.")

        result = None
        response = client.images(all=True)

        for image in response:
            image = normalize_keys(image)
            if 'repo_tags' in image:
                for repo_tag in image['repo_tags']:
                    if name == repo_tag:
                        result = Image(client, repo_tag)
                        break

        return result

    @staticmethod
    @retry
    def find_all_by_name(client, name):
        """
        """
        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client.")

        images = {}

        try:
            response = client.images(all=True)
            for image in response:
                image = normalize_keys(image)
                if 'repo_tags' in image:
                    if "<none>:<none>" in image['repo_tags']:
                        continue
                    else:
                        for repo_tag in image['repo_tags']:
                            if 'library' in name and '/' in name:
                                repository, name = name.split('/')

                            if name in repo_tag:
                                if image['id'] not in images:
                                    images[image['id']] = Image(client, repo_tag)
                                continue

            return images

        except Exception as e:
            raise e

    @staticmethod
    def pull(client, registry, repository_tag, tag=None):
        """
        """
        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client.")

        if not isinstance(registry, (V1, V2)):
            raise Exception("Must pass an a SeaPort object to pull the image.")

        if not isinstance(repository_tag, six.string_types):
            raise TypeError('repository must be a string')

        if ':' in repository_tag:
            if tag:
                raise AttributeError(
                    'When passing the tag parameter you must remove the tag from repository_tag.'
                )
            elif repository_tag.count(':') > 1:
                raise ValueError('repository_tag can only have 1 tag. More than one : was found.')
            else:
                repository_tag, tag = repository_tag.split(':')
        elif not tag:
            tag = 'latest'

        if not registry.ping():
            raise Exception("Lost comms with {0}".format(registry.location))

        logger.info('Pulling image from: {0}'.format(registry.location))
        if 'index.docker.io' in registry.location:
            response = client.pull(repository_tag, stream=True, tag=tag)
        else:
            response = client.pull("{0}/{1}".format(registry.location, repository_tag), stream=True, tag=tag)

        parse_stream(response)
        client.close()

        return Image(client, '{0}/{1}:{2}'.format(registry.location, repository_tag, tag))

    @staticmethod
    def build(client, repository_tag, docker_file, tag=None, use_cache=False):
        """
        Build a docker image
        """
        if not isinstance(client, docker.Client):
            raise TypeError("client needs to be of type docker.Client.")

        if not isinstance(docker_file, six.string_types) or not os.path.exists(docker_file):
            # TODO: need to add path stuff for git and http etc.
            raise Exception("docker file path doesn't exist: {0}".format(docker_file))

        if not isinstance(repository_tag, six.string_types):
            raise TypeError('repository must be a string')

        if not tag:
            tag = 'latest'

        if not isinstance(use_cache, bool):
            raise TypeError("use_cache must be a bool. {0} was passed.".format(use_cache))

        no_cache = not use_cache

        if ':' not in repository_tag:
            repository_tag = "{0}:{1}".format(repository_tag, tag)
        file_obj = None
        try:
            if os.path.isfile(docker_file):
                path = os.getcwd()
                docker_file = "./{0}".format(os.path.relpath(docker_file))

                # TODO: support using file_obj in the future. Needed for post pre hooks and the injector.
                # with open(docker_file) as Dockerfile:
                #     testing = Dockerfile.read()
                #     file_obj = BytesIO(testing.encode('utf-8'))

                response = client.build(
                    path=path,
                    nocache=no_cache,
                    # custom_context=True,
                    dockerfile=docker_file,
                    # fileobj=file_obj,
                    tag=repository_tag,
                    rm=True,
                    stream=True
                )
            else:
                response = client.build(path=docker_file, tag=repository_tag, rm=True, nocache=no_cache, stream=True)
        except Exception as e:
            raise e
        finally:
            if file_obj:
                file_obj.close()

        parse_stream(response)
        client.close()

        return Image(client, repository_tag)
