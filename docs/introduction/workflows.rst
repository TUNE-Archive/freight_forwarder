.. _workflows-overview:

=========
Workflows
=========

Overview
========

The following section will define multiple methods for the building, exporting, and deploying of containers with freight-forwarder. It will be broken down into examples by individual scenarios to allow for expansion. The scenarios will assume that standard root keys are in the configuration file are present.

There are some best practices to follow when iterating on the *freight-forwarder.yaml* configuration file.

1. When defining the Dockerfile, add all source code near the end of the Dockerfile to promote the use of cached images during development. Use finalized images for configuration injection or build without using cache. This reduces any potential issues associated with cached images leaving traces of previous builds.
2. Reduce the amount of dependencies that are installed in the final image. As an example, when building a java or go project, separate the `src` or `build` container into a separate container that can provide the go binary or jar for consuming in another container.
3. Begin the Dockerfile with more `RUN` directives, but once it is tuned in, combine the statements into one layer.

Example::

    RUN ls -la
    RUN cp -rf /home/example /example
    # configures this into one layer if possible
    RUN ls -la \
        && cp -rf /home/exampe /example

4. Examine other projects. Determine if the image needs to be more dynamic and to be utilized for multiple definitions or purposes. For example, an elasticsearch node can be defined as a master, data, or client node. These are configuration changes that can be changed by environment variables. Is this needed to fulfill the specification or will there exist defined images for different nodes that need to remain complete without a dynamic nature?

.. _workflows-scenario1:

Scenario #1 - Single Service No Dependencies
============================================

THe service below requires no dependencies (external services) and can run entirely by itself.

configuration::

    api:
      build: ./
      ports:
        - "8000:8000"
      env_vars:
        - ...

.. _workflows-scenario2:

Scenario #2 - Single Service with Cache
=======================================

The service requires memcach/redis/couchbase as a caching service. When locally deployed or in quality-control, this will allow for the defined `cache` container to be started to facilitate the shared cache for the api.

configuration::

    api:
      build: ./
      ports:
        - "8000:8000"
      env_vars:
        - ...

    cache:
      image: default_registry/repo/image:<tag>
      ports:
        - "6379:6739"

    environments:
      development:
        local:
          hosts: ...
          api:
            links:
              - cache

This would suffice for most local development. But what happens you need to run a container with a defined service that is in staging or production? You can define the service as a separate dependency that is pre-configured to meet the specs for your service to operate. Ideally, this should be **configured** as a Dockerfile inside your project. This provides the additional benefit of providing a uniform development environment for all develops to work in unison on the project.

export configuration::

    staging_hostname:
      image: default_registry/repo/image:tag
      ports:
        - "6379:6379"

    environments:
      development:
        use01:
          export:
            api:
              image: default_registry/repo/baseimage_for_service:tag
              links:
                - staging_hostname
              # or
              extra_hosts:
                - "staging_hostname:ip_address"
                - "staging_hostname:ip_address"
              # or
              extra_hosts:
                staging_hostname: ip_address

.. _workflows-scenario3:

Scenario #3 - Single Service with Multiple Dependencies
=======================================================

This would be an example of a majority of services that required multiple dependencies for a variety of reasons. For example, it might require a shared cache with a database for relational queries, and an ElasticSearch cluster for analytics, metrics, logging, etc.

configuration::

    esmaster:
      ...
    esdata:
      links:
        - esmaster
    api:
      links:
        - esdata
        - mysql
        - cache
    nginx:
      env_vars:
        - "use_ssl=true"
    mysql:
      ...
    cache:
      ...

    environments:
      development:
        quality-control:
          nginx:
            links:
              - api

When *quality-control* or *deploy* is performed as the action, this will start all associated containers for the service. Internally, all *dependents* and *dependencies* will be analyzed and started in the required order. The list below represents the order in which containers will be created and started.


1. mysql or cache
2. cache or mysql
3. esmaster
4. esdata
5. api
6. nginx

When attempting to export a service, all dependencies will be started; but no dependents. For example, if attempting to export the *api*, *mysql*, *cache*, *esmaster* and then *esdata* will be started before the api is built from the Dockerfile or the image is pulled and started.
