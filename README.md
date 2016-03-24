[![Version](https://img.shields.io/pypi/v/freight-forwarder.svg?)](https://pypi.python.org/pypi/freight-forwarder)
[![Downloads](https://img.shields.io/pypi/dm/freight-forwarder.svg?)](https://pypi.python.org/pypi/freight-forwarder)
[![Documentation Status](https://readthedocs.org/projects/freight-forwarder/badge/?version=latest)](http://freight-forwarder.readthedocs.org/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/TuneOSS/freight_forwarder.svg?branch=master)](https://travis-ci.org/TuneOSS/freight_forwarder)
[![Gitter](https://badges.gitter.im/TuneOSS/freight_forwarder.svg)](https://gitter.im/TuneOSS/freight_forwarder?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge)

#Freight Forwarder
Freight Forwarder is a utility that organizes the transportation and distribution of docker images and containers from 
the developer to their applications consumers. It allows the developer to focus on building features while relying on 
Freight Forwarder for continuous integration.

Documentation is available here: [Freight Forwarder Documentation](http://freight-forwarder.readthedocs.org/en/latest).

##Description
Freight Forwarder is an SDK and CLI that focuses on continuous integration and continuous delivery.

At first glance it looks and feels a lot like Compose. However, Compose is very focused on the developers workflow and 
easing the pain of multiple container environments. Freight Forwarder can be used to accomplish that same task and much more. 

Freight Forwarder focuses on how Docker images are built, tested, pushed, and then deployed. The images being pushed to the registry 
are the artifacts being deployed. There should be no additional changes made to the images after being exported. In addition, 
the containers should be able to start taking traffic or doing work on initialization. 

When deploying from one environment to the next it is suggested to:

    1. Pull the image from the previous environment make configuration changes and commit those changes to a new image layer.
    2. Testing should be run with the new configuration changes.
    3. After the image is verified, it will be pushed up to the registry and tagged accordingly.
    4. That image will then be used when deploying to that environment..

##Installation
Follow these [instructions](http://freight-forwarder.readthedocs.org/en/latest/introduction/install.html).

Freight Forwarder works on Docker version 1.8, API version 1.20.

##Contributing
Want to write some code? Check out the [contributing documentation](http://freight-forwarder.readthedocs.org/en/latest/contributing/overview.html).

##Contributors
* [abanna](http://github.com/abanna) - 2015-Current
* [davidremm](http://github.com/davidremm) - 2015-Current
* [fin09pcap](http://github.com/fin09pcap) - 2015-Current
* [jyoung360](http://github.com/jyoung360) - 2015-Current

## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
