.. -*- mode: rst; encoding: utf-8 -*-
.. _index:

=========================================
Freight Forwarder |version| documentation
=========================================
Freight Forwarder is a utility that uses Docker to organize the transportation and distribution of Docker images from
the developer to their application consumers.  It allows the developer to focus on features while relying on Freight
Forwarder to be the expert in continuous integration and continuous delivery.

The `project website`_ can be reference for the following information.  Please report any bugs or feature requests on `Github Issues`_.

.. _project website: https://github.com/TuneOSS/freight_forwarder
.. _Github Issues: https://github.com/TuneOSS/freight_forwarder/issues

.. _index-overview:

Introduction
============
.. toctree::
   :hidden:

   introduction/overview
   introduction/install
   introduction/project_integration
   introduction/workflows

:doc:`introduction/overview`
    A general description of the project.  Something to get you acquainted with Freight Forwarder.
:doc:`introduction/install`
    How do I install this thing?  Some simple install instructions.
:doc:`introduction/project_integration`
    How do I integrate Freight Forwarder with my project?  Explanation of how to integrate with Freight Forwarder, expectations,
    and a few examples.
:doc:`introduction/workflows`
    Examples of different implementations for a variety of services. Single Service definition, Single Server with One
    dependency, Multi-dependency services, etc.

.. _index-basic-usage:

Basic Usage
===========
.. toctree::
   :hidden:

   config/overview
   cli/overview

:doc:`config/overview`
    Configuration file for projects.

:doc:`cli/overview`
    CLI command index.


Extending Freight Forwarder
===========================

.. toctree::
   :hidden:

   injector/overview
   sdk/overview

:doc:`injector/overview`
   Describes how to implement an injector.

:doc:`sdk/overview`
   SDK Documentation.


.. toctree::
   :hidden:

   contributing/overview

.. toctree::
   :hidden:

   faq/overview
