.. _injector-overview:

========
Injector
========

Overview
========

The injector was built and designed to create configuration files and share them with freight forwarder during the CI process.
We use the injector to make api calls to CIA an internal tool that we use to manage configuration files.  The injector uses CIA's
response and writes configuration files to disk, shares them with freight forwarder using a shared volume, and returns `Injector Response`_
to provide metadata about the configuration files.  This doesn't have to be limited to configuration files and can be
extended by creating a new injector container so long as it follows a few rules.

.. note:: If injection is required during export set --configs=true. This will be changed to --inject in the future.

Workflow
========
    - Freight Forwarder pulls the injector image defined in environment variable ``INJECTOR_IMAGE``. The value must be in the following format ``repository/namespace:tag``.

    - Freight Forwarder passes `Environment Variables`_ to the injector container when its created.

    - Freight Forwarder then runs the injector.

    - Freight Forwarder uses the data returned from the injector to create intermediate containers based on the application image.

    - Freight Forwarder than commits the changes to the application image.

Creating Injector Images
========================
When creating an injector image the container created from the image is required to produce something to inject into
the the application image. Freight Forwarder provides `Environment Variables`_ to the injector container as a way to
identify what resources it should create. After the injector creates the required resources it must return a valid
`Injector Response`_.  Freight Forwarder will then use that response to commit the required resources into the application image.

After the injector image has been created and tested the end user will need to provide the ``INJECTOR_IMAGE`` environment variable
with a string value in the following format: ``repository/namespace:tag``.  In addition, to the environment variable the end user will have to
set --configs=true. This will tell Freight Forwarder to use the provided image to add a layer to the application image
after it has been built or pulled from a docker registry. A specific registry can be defined in the configuration file with the alias of
"injector". If the injector alias isn't defined the default registry will be used.

Environment Variables
=====================
These environment variables will be passed to the injector container every run.  They will change based on the Freight
Forwarder configuration file, user provided environment variables, and command line options.

====================== ======== ============= =============================================================
Name                   Required Type          Description
====================== ======== ============= =============================================================
INJECTOR_CLIENT_ID     False    string        | OAuth client id, this must be provided by the user.

INJECTOR_CLIENT_SECRET False    string        | OAuth secret id, this must be provided by the user.

ENVIRONMENT            True     string        | Current environment being worked on. example: development
                                              | This maps to what is being passed to --environment option.

DATACENTER             True     string        | Current data center being worked on. example: us-west-02
                                              | This maps to what is being passed to --data-center option.

PROJECT                True     string        | Current project being worked on. example: itops
                                              | This maps to what is in the users configuration file.

SERVICE                True     string        | Current service being worked on. example: app
                                              | This maps to what is being passed to --service option.

====================== ======== ============= =============================================================

Injector Response
=================
The injector container must return a list of objects each with the following properties formatted in json. This metadata
will be used to copy files and configure them correctly for the application image.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
name                  True     string        | Name of the file being written.

path                  True     string        | Application container Path in which to write file.

config_path           True     string        | Path to find file inside of the injector container.

user                  True     string        | File belongs to this user, user must already exist.

group                 True     string        | File belongs to the this group, group must already exist.

chmod                 True     int or string | File permissions.

checksum              True     string        | MD5 sum of file.

notifications         False    object        | Refer to `Notifications Object`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_injector_response.json
    :language: json
    :linenos:

Notifications Object
====================
The notifications object allows the injector to pass a message to the user or raise an exception if it fails to
complete a task.  If an error is provided in the notifications object freight forwarder will raise the error, this will
result in a failed run.

===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
info                  False    list          | Send a message to the user informing them of something. list of `Message Object`_

warnings              False    list          | Warn the user about a potential issue. list of `Message Object`_

errors                False    list          | Raise an error and terminate current freight forwarder run.
                                             | list of `Message Object`_
===================== ======== ============= =============================================================

.. literalinclude:: ./example_notifications.json
    :language: json
    :linenos:

.. warning:: If an errors notification is provided freight forwarder will terminate the current run.

Message Object
==============
===================== ======== ============= =============================================================
Name                  Required Type          Description
===================== ======== ============= =============================================================
type                  True     string        | Type of message.

details               True     string        | The message to deploy to the end user.

===================== ======== ============= =============================================================

.. literalinclude:: ./example_message.json
    :language: json
    :linenos:
