.. _config-overview:

==================
Configuration File
==================

Overview
========

This is the blueprint that defines an applications CI/CD workflow, container configuration, container host configuration,
and its dependencies per environment and data-center. The file should be written in yaml (json is also supported). The objects
in the configuration file have a cascading effect. Meaning that the objects defined deepest in the object structure take
precedent over previously defined values.  This allows for common configuration values to be shared as well as allowing
the flexibility to override values per individual operation.

.. Warning:: Configuration injection isn't included in this configuration file.

Terminology Explanation
=======================

Definitions:

=====================  ==========================================================================
freight-forwarder.yml  | Handles the organization of application services, environments and data-centers.

hosts                  | A server physical/virtual server that has the docker daemon running. The daemon must be configured
                       | to communicate via tcp.

service                | Multiple services are defined to make a project. A service could be an api, proxy, db, etc.

environments           | An object that is used to define where/how containers and images are
                       | being deployed, exported, and tested for each environment.

data centers           | An object that is used to define where/how containers and images are
                       | being deployed, exported, and tested for each data center.

registry               | The docker registry where images will be pushed.
=====================  ==========================================================================

Root Level Properties
=====================

All of the properties at the root of the configuration file either correlate to a service, project metadata,
or environments.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
team                  True     string        | Name of the development team.

project               True     string        | The project that is being worked on.

repository            True     string        | The projects git repo.

services              True     object        | Refer to `Service Properties`_

registries            False    object        | Refer to `Registries Properties`_

environments          True     object        | Refer to `Environments properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_root_properties.yml
    :language: yaml
    :linenos:


Service Properties
==================

Each service object is a component that defines a specific service of a project.  An example would be an api or database.
Services can be built from a Dockerfile or pulled from an image in a docker registry.  The container and host 
configuration can be modified on a per service bases.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
build                 one of   string        | Path to the service Dockerfile.

test                  False    string        | Path to a test Dockerfile that should be used to verify
                                             | images before pushing them to a docker registry.

image                 one of   string        | The name of the docker image in which the service depends
                                             | on. If its being pulled from a registry the fqdn must be
                                             | provided. Example: `registry/itops/cia:latest`.
                                             | If the image property is spectified it will always take 
                                             | precedent over the build property.  
                                             | If a service object has both an image and build specified 
                                             | the image will exclusively be used.

export_to             False    string        | Registry alias where images will be push. This will be
                                             | set to the default value if nothing is provided. The alias
                                             | is defined in `Registries Properties`_

Container Config      any of                 | Refer to `Container Config Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_service.yml
    :language: yaml
    :linenos:

Registries Properties
=====================
The registries object is a grouping of docker registries that images will be pulled from or pushed to. The alias of each
registry can be used in any image definition `image: docker_hub/library/centos:6.6`. By default docker_hub is provided for all users.
The default property will be set to docker_hub unless overridden with any of the defined registries.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
registry (alias)      True     object        | Refer to `Registry Properties`_
default               False    object        | Refer to `Registry Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_registries.yml
    :language: yaml
    :linenos:


Registry Properties
===================

The docker registry that will be used to pull or push validated docker images.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
address               True     string        | Address of docker host, must provide http scheme.
                                             | Example: https://your_dev_box.office.priv:2376

ssl_cert_path         False     string       | Full system path to client certs.
                                             | Example: /etc/docker/certs/client/dev/

verify                False    bool          | Validate certificate authority?

auth                  False    object        | Refer to `Registry Auth Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_registry.yml
    :language: yaml
    :linenos:

Registry Auth Properties
========================

These are properties required for authentication with a registry.  Currently basic and
registry_rubber auth are support. Dynamic auth uses `Registry Rubber`_ to support
nonce like basic auth credentials. Please refer to `Registry Rubber`_ documentation
for a deeper understanding of the service.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
address               True     string        | Address of docker host, must provide http scheme.
                                             | Example: https://your_dev_box.office.priv:2376

ssl_cert_path         False    string        | Full system path to client certs.
                                             | Example: /etc/docker/certs/client/dev/

verify                False    bool          | Validate certificate authority?

type                  False    string        | Type of auth. Currently supports basic and registry_rubber.
                                             | Will default to basic.
===================== ======== ============= =============================================================

.. literalinclude:: ./example_registry_auth.yml
    :language: yaml
    :linenos:

Environments properties
=======================

The Environments object is a grouping of instructions and configuration values that define the behavior for a CI/CD pipeline
based on environment and data center. The environments and data centers are both user defined.

.. Warning:: If using CIA:  The environments and data centers need to match what is defined in CIA. Freight Forwarder
    will pass these values to the injector to obtain the correct configuration data.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
environment           True     object        | Refer to `Environment Properties`_ valid environments are
                                             | ci, dev, development, test, testing, perf, performance,
                                             | stage, staging, integration, prod, production.

service               False    object        | Refer to `Service Properties`_

host                  False    object        | Refer to `Hosts Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_environments.yml
    :language: yaml
    :linenos:

Environment Properties
======================

The environment of the application.  An application can and one or many environments. Valid environments are ci, dev,
development, test, testing, perf, performance, stage, staging, integration, prod, production.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
hosts                 False    object        | Refer to `Hosts Properties`_ if not defined freight forwarder will use
                                             | the docker environment variables.

data centers          True     object        | Refer to `Data Center Properties`_

services              False    object        | Refer to `Service Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_environment.yml
    :language: yaml
    :linenos:

Data Center Properties
======================

Each environment can have multiple data center objects.  Some examples of data centers: local, sea1, use-east-01, and
us-west-02

===================== ======== ============= =============================================================
Name                  Required Type           Description
===================== ======== ============= =============================================================
hosts                 False    object        | Refer to `Hosts Properties`_ if not defined freight forwarder will use
                                             | the docker environment variables.

service               False    object        | Refer to `Service Properties`_

deploy                one of   object        | Refer to `Deploy Properties`_

export                one of   object        | Refer to `Export Properties`_

quality_control       one of   object        | Refer to `Quality Control Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_data_center.yml
    :language: yaml
    :linenos:

Deploy Properties
=================

The deploy object allows development teams to define unique deployment behavior for specific service, environment, and data center.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
service               True     object        | Refer to `Service Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_deploy.yml
    :language: yaml
    :linenos:

Export Properties
=================

The export object allows development teams to define unique artifact creation behavior for a specific service, environment, and data center.
Export is the only action that allows you to have a specific unique hosts definition (this is a good place for a jenkins or build host).

.. Note:: To remove Freight Forwarders tagging scheme pass --no-tagging-scheme to the cli export command.
.. Warning:: When exporting images Freight Forwarder will use the service definition in deploy for any dependencies/dependents. In addition, if a command is provided in the config for the service being exported Freight Forwarder assumes any changes made should be committed into the image.


===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
service               True     object        | Refer to `Service Properties`_

tags                  False    array[string] | A list of tags that should be applied to the image before
                                             | exporting.
===================== ======== ============= =============================================================

.. literalinclude:: ./example_export.yml
    :language: yaml
    :linenos:

Quality Control Properties
==========================

The quality control object allows developers a way to test containers, images, and workflows locally before deploying or exporting.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
service               True     object        | Refer to `Service Properties`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_quality_control.yml
    :language: yaml
    :linenos:

Hosts Properties
================

The hosts object is a collection of docker hosts in which Freight Forwarder will interact with when  deploying, exporting,
or testing.  Each service can have a collection of its own hosts but will default to the defaults definition or the
standard Docker environment variables: DOCKER_HOST, DOCKER_TLS_VERIFY, DOCKER_CERT_PATH.


===================== ======== ======================== =============================================================
Name                  Required Type                     Description
===================== ======== ======================== =============================================================
service_name (alias)  one of   list[`Host Properties`_] | List of `Host Properties`_

export                one of   list[`Host Properties`_] | List with as single element of `Host Properties`_

default               one of   list[`Host Properties`_] | List of `Host Properties`_
===================== ======== ======================== =============================================================

.. literalinclude:: ./example_hosts.yml
    :language: yaml
    :linenos:


Host Properties
===============
The host object is metadata pertaining to docker hosts.  If using ssl certs they must be the host where
Freight Forwarder is run and be able to be read by the user running the commands.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
address               True     string        | Address of docker host, must provide http scheme.
                                             | Example: https://your_dev_box.office.priv:2376

ssl_cert_path         False    string        | Full system path to client certs.
                                             | Example: /etc/docker/certs/client/dev/

verify                False    bool          | Validate certificate authority?
===================== ======== ============= =============================================================

.. literalinclude:: ./example_host.yml
    :language: yaml
    :linenos:

Host Config Properties
======================

Host configuration properties can be included as a part of the the service definition.
This allows for greater control when configuring a container for specific requirements to operate. It is suggested that
a root level definition of a service be minimalistic compared to how it should be deployed in a specific environment or
data-center.

Refer to `Docker Docs`_ for the full list of of potential properties.

===================== ======== ============= ======================== =============================================================
Name                  Required Type          Default Value            Description
===================== ======== ============= ======================== =============================================================
binds                 False    list          ['/dev/log:/dev/log:rw'] | Default value applied to all containers. This allows for
                                                                      | inherit use of `/dev/log` for logging by the container

cap_add               False    string        None                     | Defined system capabilities to add to the container from the
                                                                      | host. Refer to http://linux.die.net/man/7/capabilities for a
                                                                      | full list of capabilities

cap_drop              False    string        None                     | Defined system capabilities to remove from the container from the
                                                                      | host. Refer to http://linux.die.net/man/7/capabilities for a
                                                                      | full list of capabilities

devices               False    list          None                     | Device to add to the container from the host
                                                                      | Format of devices should match as shown below. Permissions
                                                                      | need to be set appropriately.
                                                                      | "/path/to/dev:/path/inside/container:rwm'

links                 False    list          []                       | Add link to another container

lxc_conf              False    list          []                       | Add custom lxc options

readonly_root_fs      False    boolean       False                    | Read-only root filesystem
readonly_rootfs

security_opt          False    list          None                     | Security Options

memory                False    int           0                        | Memory limit

memory_swap           False    int           0                        | Total memory (memory + swap), -1 to disable swap

cpu_shares            False    int           0                        | CPU shares (relative weight)

port_bindings         False    list/dict     {}                       | Map the exposed ports from host to the container
ports

publish_all_ports     False    boolean       False                    | All exposed ports are associated with an ephemeral
                                                                      | port

privileged            False    boolean       False                    | Give extended privileges to this container

dns                   False                  None                     | Set custom DNS servers

dns_search            False                  None                     | Set custom DNS search domains

extra_hosts           False                  None                     | Add additional hosts as needed to the container

network_mode          False    string        bridge                   | Network configuration for container environment

volumes_from          False    list          []                       | Mount volumes from the specified container(s)

cgroup_parent         False    string        ''                       | Optional parent cgroup for the container

log_config            False    dict          json-file                | Defined logging configuration for the container.
                                                                      | Reference the logging-driver for appropriate
                                                                      | docker engine version
                                                                      | Default Value:
                                                                      | {
                                                                      |  "type": json-file,
                                                                      |  "config": {
                                                                      |    "max-files": "2",
                                                                      |    "max-size": "100m"
                                                                      |    }
                                                                      | }

ulimits               False    dict          None                     | Defined user process resource limits for the
                                                                      | containers run time environment
                                                                      |
                                                                      | Example:
                                                                      |
                                                                      | ulimits:
                                                                      |   - name: memlock
                                                                      |    soft: 3000000
                                                                      |    hard: 3000000

restart_policy        False    dict          {}                       | This defines the behavior of the container
                                                                      | on failure
===================== ======== ============= ======================== =============================================================

.. literalinclude:: ./example_host_config.yml
    :language: yaml
    :linenos:

Container Config Properties
===========================

Container config properties are container configuration settings that can be changed by the developer to meet the container run time requirements.
These properties can be set at any level but the furthest in the object chain will take presidents. Please refer to
`Docker Docs`_ for a full list of properties.

===================== ======== ============= ======================== =============================================================
Name                  Required Type          Default Value            Description
===================== ======== ============= ======================== =============================================================
attach_stderr         False    boolean       False                    | Attach to stderr

attach_stdin          False    boolean       False                    | Attach to stdin and pass input into Container

attach_stdout         False    boolean       False                    | Attach to stdout

cmd                   False    list          None                     | Override the command directive on the container
command

domain_name           False    string        ''                       | Domain name for the container
domainname

entry_point           False    list          ''                       | Defined entrypoint for the container
entrypoint

env                   False    list          ''                       | Defined environment variables for the container
env_vars

exposed_ports         False    list          ''                       | Exposes port from the container. This
                                                                      | allows a container without an 'EXPOSE' directive to make
                                                                      | it available to the host

hostname              False    string        ''                       | hostname of the container

image                 False    string        ''                       | defined image for the container

labels                False    dict|none     {}                       | labels to be appended to the container

network_disabled      False    boolean       False                    | Disable network for the container

open_stdin            False    boolean       False                    | This defined multiple values:
                                                                      | stdin_once   = True
                                                                      | attach_stdin = True
                                                                      | detach       = False

stdin_once            False    boolean       False                    | Opens stdin initially and closes once data transfer has been
                                                                      | completed

tty                   False    boolean       False                    | Open interactive pseudo tty

user                  False    string        ''                       | Allows the developer to set a default
                                                                      | user to run the first process with the

volumes               False    list          None                     | List of volumes exposed by the container

working_dir           False    string        ''                       | Starting work directory for the container

detach                False    boolean       False                    | Default Values applied:
                                                                      | attach_stdout = False
                                                                      | attach_stderr = False
                                                                      | stdin_once    = False
                                                                      | attach_stdin  = False
===================== ======== ============= ======================== =============================================================

.. _Registry Rubber: https://github.com/TuneOSS/Registry-Rubber
.. _CIA: https://github.com/adapp/cia
.. _Docker Docs: https://docs.docker.com/
.. _Docker Github: https://github.com/docker/docker
