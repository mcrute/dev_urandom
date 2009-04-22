"""ObDict setup script! yaay!"""

from __future__ import with_statement
import sys
from setuptools import setup

VERSION = '0.2.0'
URL = 'http://meatballhat.com/attic/code/ObDict/dist/'
DESCRIPTION_FILE = 'README'
SUMMARY = "mapping container type with __getitem__ and __getattr__ access"
AUTHOR = 'Dan Buch'
AUTHOR_EMAIL = 'daniel.buch@gmail.com'
CLASSIFIERS = [l.strip() for l in \
"""Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Libraries :: Python Modules""".splitlines()]


def _get_long_description():
    """retreives the long description from file"""
    with open(DESCRIPTION_FILE, 'rb') as ld_file:
        return ld_file.read() or 'UNKNOWN'


def main():
    """wraps the call to setup() for ease of editing in ipython :)"""
    setup(name='ObDict', version=VERSION,
        description=SUMMARY,
        long_description=_get_long_description(),
        classifiers=CLASSIFIERS,
        author=AUTHOR, author_email=AUTHOR_EMAIL,
        maintainer=AUTHOR, maintainer_email=AUTHOR_EMAIL,
        url=URL, download_url=URL, license='MIT',
        platforms=['any'], test_suite='nose.collector',
        py_modules=['obdict'], include_package_data=True, 
        zip_safe=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
