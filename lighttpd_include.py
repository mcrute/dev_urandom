#!/usr/bin/python
"""
Lighttpd Include Generator
by Mike Crute (7/12/2008)
for SoftGroup Interactie, Inc.

Replace the sucky perl-based include generator that ships with
lighttpd on debian-based distros. Basically it chdirs into the
lighttpd config dir /etc/lighttpd/ and makes a list of all the
files in a directory that you pass as the only argument.
"""

__version__ = "$Rev$"
__author__ = "$Author$"
__date__ = "$Date$"

import os
import sys
from glob import glob

def make_includes(directory):
    os.chdir("/etc/lighttpd")
    for file in glob("%s/*.conf" % directory):
        print 'include "%s"' % file

if __name__ == "__main__":
    if len(sys.argv) is not 2:
        print "Usage: %s [directory]" % sys.argv[0]
    else:
        make_includes(sys.argv[1])
