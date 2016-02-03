.. _project-integration:

===================
Project Integration
===================

Overview
========

Before being able to use Freight Forwarder there must be a Dockerfile in the root of your project. The Project Dockerfile
is a standard Dockerfile definition that contains the instructions required to create a container running the application source code.
The Project Dockerfile must container an entrypoint or cmd to start the application.

If the project has tests a second Dockerfile should be built. This test Dockerfile should reside in the root of the
application tests directory and inherent from the Project Dockerfile. The test Dockerfile should contain instructions
to install test dependencies and have an entrypoint and command that will run the entire applications test suite. The
tests should return a non zero on failure.

If there are dependencies or base image Dockerfiles they can live anywhere in your projects and can be referenced in any
service definition, via the `build: path`.  This allows for more complex projects to be managed with one configuration file.

Example Project Dockerfile::

    FROM  ubuntu:14.04
    MAINTAINER John Doe "jdoe@nowhere.com"
    ENV REFRESHED_AT 2015-5-5

    RUN apt-get update
    RUN apt-get -y install ruby rake

    ADD ./ /path/to/code

    ENTRYPOINT ["/usr/bin/rake"]
    CMD ["start-app"]

Example Test Dockerfile::

    FROM docker_registry/ruby-sanity:latest
    MAINTAINER John Doe "jdoe@nowhere.com"
    ENV REFRESHED_AT 2014-5-5

    RUN gem install --no-rdoc --no-ri rspec ci_reporter_rspec
    ADD ./spec /path/to/code/spec
    WORKDIR /path/to/code
    ENTRYPOINT ["/usr/bin/rake"]
    CMD ["spec"]

.. _project-namespacing:

Namespacing
===========
Freight Forwarder is a bit opinionated about namespaces.  The namespace for images map to the pre-existing docker naming
conventions.  Team/Project map directly to Dockers repository field.

Example Docker namespace::

    repository/name:tag


Example Freight Forwarder namespace::

    team/project:tag

.. _project-tagging:

Tagging
=======
When tagging your images Freight Forwarder will use the data center and/or environment provided in the configuration
file.  Freight Forwarder will prepend those when tagging images.

Example tag::

    datacenter-environment-user_defined_tag

Real Life Example::

    us-east-1-development-beta

.. _project-manifest:

Configuration File
==================
The :ref:`Configuration File<config-overview>` is required and is the what the consumer uses to define their pipeline.

..  _project-configuration-injection-integration:

Configuration Injection Integration
===================================
If there is interest in integrating with the injector please start by referring to the :ref:`Injector<injector-overview>`.


Example Projects
================

    * `Docker Example`_
    * `CIApi`_

Jenkins Integration
===================

