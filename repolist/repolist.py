#!/usr/bin/python
"""
Subversion Repository Listing Tool
by Mike Crute on July 13, 2008
for SoftGroup Interactive, Inc.
Released under the terms of the BSD license.

Generate a list of protected and unprotected subversion repositories
within a certain directory and pass those to a mako template. The 
original intent was to provide a web-based public listing of svn
repos on a machine but this could be used for anything.
"""

import os
from stat import S_ISDIR as is_directory, ST_MODE as MODE
from ConfigParser import SafeConfigParser
from mako.template import Template

def get_repos(cfg, protected=False, directory='.', urlprepend="/repos/"):	
	"""Get Repository List

	Get a list of subversion repositories on the server by examining
	a directory. The subdirectories are are looked up in a svn
	authentication file to determine if they are locked or unlocked 
	and are then yielded to the caller.
	"""

	directory += "/" if not directory.endswith("/") else ""

	# Determine if the default repo policy is to allow reading
	try:
		default_policy = 'r' in cfg.get('/', '*')
	except:
		default_policy = True

	for item in os.listdir(directory):
		# Skip item if it's not a directory
		if not is_directory(os.stat("%s%s" % (directory, item))[MODE]):
			continue

		try:
			if 'r' not in cfg.get('%s:/' % item, '*') and protected == True:
				yield (item, urlprepend + item)
			
			if 'r' in cfg.get('%s:/' % item, '*') and protected == False:
				yield (item, urlprepend + item)
		except:
			if default_policy != protected:
				yield (item, urlprepend + item)
			else:
				continue


if __name__ == "__main__":
	"""SoftGroup Interactive CGI Driver
	Basically just run the script and output headers for CGI. For internal use.
	"""
	config = SafeConfigParser()
	config.readfp(open('/etc/svn/authen.conf'))

	tmpl = Template(filename='repolist.tpl')
	print "Content-Type: text/html\r\n"
	print tmpl.render(**{
		'locked_repos': [x for x in get_repos(config, protected=True, directory="/var/svn")],
		'unlocked_repos': [x for x in get_repos(config, protected=False, directory="/var/svn")]
	})
