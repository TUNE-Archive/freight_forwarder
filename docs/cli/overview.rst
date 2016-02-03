.. _cli-overview:

===
CLI
===

Overview
========
Freight Forwarder CLI consumes the SDK and makes requests to a docker registry api and the docker client api.  
The CLI must be run in the same location as the configuration file (freight-forwarder.yml). 
Additional information regarding the configuration files can be found :ref:`Config documentation <config-overview>`.

For full usage information::

    freight-forwarder --help


.. note:: Example Service Definition
.. code-block:: yaml
    :linenos:

    api:
        build: "./"
        test: "./tests/"
        ports:
            - "8000:8000"
        links:
            - db


.. _cli-info:

Info
====
.. currentmodule:: freight_forwarder.cli.info
.. autoclass:: InfoCommand(args)

.. _cli-deploy:

Deploy
======
.. currentmodule:: freight_forwarder.cli.deploy
.. autoclass:: DeployCommand(args)

.. _cli-export:

Export
======
.. currentmodule:: freight_forwarder.cli.export
.. autoclass:: ExportCommand(args)

.. _cli-offload:

Offload
=======
.. currentmodule:: freight_forwarder.cli.offload
.. autoclass:: OffloadCommand(args)

.. _cli-quality-control:

Quality Control
===============
.. currentmodule:: freight_forwarder.cli.quality_control
.. autoclass:: QualityControlCommand(args)

.. _cli-test:

Test
====
.. currentmodule:: freight_forwarder.cli.test
.. autoclass:: TestCommand(args)

.. _cli-marshaling-yard:

Marshalling Yard
================
.. currentmodule:: freight_forwarder.cli.marshaling_yard
.. autoclass:: MarshalingYardCommand(args)
