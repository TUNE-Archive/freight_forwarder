.. _general-overview:

================
General Overview
================

Freight Forwarder focuses on continuous integration and continuous delivery. At first glance it looks and feels a lot like Fig/Compose.
However, Fig/Compose are very focused on the developers workflow and easing the pain of multiple container environments. Freight Forwarder
can be used to accomplish that same task and much more. Freight Forwarder focuses on how Docker images are built, tested, pushed,
and then deployed. Freight Forwarder uses an image based CI/CD approach, which means that the images being pushed to the registry are the artifacts
being deployed. Images should be 100% immutable, meaning that no additional changes should need to be made to the images after being exported.
It is expected that containers will be able to start taking traffic or doing work on initialization. When deploying from one environment to the next,
the image from the previous environment will be pulled from the registry and configuration changes will be made and committed to a new image.
Testing will be ran with the new configuration changes. After the image is verified, it will be pushed up to the registry and
tagged accordingly. That image will then be used when deploying to that environment.

Freight Forwarder works on Docker version 1.8, API version 1.20.

Please review the :ref:`project integration <project-integration>` documentation to start integrating your project with Freight Forwarder.

.. _general-config:

Configuration File
==================
The configuration file defines your CI/CD pipeline.  The definition of the manifest is something developers will have
to define to support their unique workflow.  This empowers the developer to define the CI/CD pipeline without interaction
with an operations team.

:ref:`Configuration file documentation <config-overview>`

.. warning:: The :ref:`configuration file <config-overview>` is required if your planning to use the :ref:`CLI <cli-overview>`.

.. _general-sdk:

SDK
===

Freight forwarder is an SDK that interacts with the docker daemon api.  The SDK provides and abstraction layer for CI/CD
pipelines as well as the docker api itself.  The SDK allows developers to use or extend its current functionality.

:ref:`SDK documentation <sdk-overview>`

.. _general-cli:

CLI
===
Freight Forwarder CLI consumes the SDK and provides an easy to use interface for developers, system administrators, and CI services.
The CLI provides all of the functionality required to support a complete CI/CD workflow both locally and remote.  If a project has a
manifest the cli provides an easy way to override values without having to modify the manifest itself.

:ref:`CLI documentation <cli-overview>`

.. _general-injector:

Injector
========
Freight Forwarder plays a roll in the injection process.  It will pull an Injector Image from a registry then create and run the container.
The Injector shares whatever files that need to be injected with freight forwarder with a shared volume. Freight Forwarder then copies,
chowns, and chmods the files into the application image based on the metadata provided in the injectors response.

:ref:`Injector documentation<injector-overview>`
