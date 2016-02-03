#!/usr/bin/env python
import os
from setuptools import setup, find_packages

import freight_forwarder


ROOT_DIR = os.path.dirname(__file__)
SOURCE_DIR = os.path.join(ROOT_DIR)


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

requirements = [
    "docker-py>=1.6.0",
    "ipaddress==1.0.16",
    "requests>=2.5.3",
    "python-dateutil>=2.4.0",
    "six>=1.9.0",
    "pyyaml==3.10",
    "argparse==1.3.0",
    "psutil==3.4.2"
]

setup(
    name=freight_forwarder.__title__,
    version=freight_forwarder.__version__,
    description="Python client and CLI to aid in CI/CD workflow using Docker.",
    author='Alex Banna',
    author_email='alexb@tune.com',
    url='https://github.com/TuneOSS/freight_forwarder',
    scripts=["bin/freight-forwarder"],
    packages=find_packages(exclude=['tests*']),
    install_requires=requirements,
    # tests_require=test_requirements,
    # test_suite='tests',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities',
    ],
)
