.. _introduction-install:

=========================
Install Freight Forwarder
=========================

OSX Install
===========
Requirements:

    * Python 2.7

    * pip, setuptools, and wheel Python packages.

    * libyaml.  This can be installed via brew.

Install via pip::

    $ pip install freight-forwarder


Ubuntu Install
==============
Ubuntu 14.10:

    wget https://bootstrap.pypa.io/get-pip.py
    sudo python get-pip.py
    aptitude update && sudo aptitude remove libyaml-dev
    pip install libyaml
    sudo pip install freight-forwarder
    freight-forwarder


Arch Linux Install
==================
Arch 4.2.3-1-ARCH:

Because Arch installs python3 as the default python, it is strongly suggested
installing pyenv and using that to manage the local python version.

    # Set the local version to a freight forwarder compatible version
    pyenv local 2.7.9
    # Install setuptools
    wget https://bootstrap.pypa.io/ez_setup.py -O - | python
    # Install pip deps
    pip install wheel
    # Install freight forwarder
    pip install freight-forwarder
    freight-forwarder info


CentOS install
==============
When we install this on CentOS we will need to update these docs.
