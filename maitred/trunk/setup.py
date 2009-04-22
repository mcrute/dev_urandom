#!/usr/bin/env python

RELEASE = False

__version__ = "0.0.1"

import sys, os
from setuptools import setup, find_packages

setup(
    name = "MaitreD",
    version = __version__,
    
    description = "Python application server.",
    long_description = "Think JBoss for Python.",
    
    author = "Mike Crute",
    author_email = "mcrute@gmail.com",
    license = "MIT",
    
    zip_safe = True,
    packages = find_packages(exclude=['ez_setup', 'examples']),
    include_package_data = True,
    package_data = { '': ['data/*'] },
    namespace_packages = ["maitred"],
    
    install_requires = [
        'ConfigObj',
    ],
    
    entry_points = {
        "maitred.app_handlers": [
            "web_application = maitred.handlers.application:web_application.factory",
            "service = maitred.handlers.application:service.factory",
            "daemon = maitred.handlers.application:daemon.factory",
            "periodical = maitred.handlers.application:periodical.factory",
        ],
        "maitred.service": [
            "mdmsg_queue = "
        ],
        "console_scripts": [
            "maitred = maitred.server:console_script",
        ],
    }
)