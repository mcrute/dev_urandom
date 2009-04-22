#!/usr/bin/env python

import sys, re

class CSSUtils:
	ColorRegex = re.compile('', re.I | re.M | re.U)
	
	@staticmethod
	def compress_color(color):
		pass
	
	@staticmethod
	def is_color(color):
		pass

class CSSContainer:
	selector = ''
	
	def __init__(self):
		pass
	
class CSSParser:
	ValidProperties = (
		'azimuth',
		'background',
		'background-color',
		'background-image',
		'background-repeat',
		'background-attachment',
		'background-position',
		'border',
		'border-top',
		'border-right',
		'border-left',
		'border-bottom',
		'border-color',
		'border-top-color',
		'border-right-color',
		'border-bottom-color',
		'border-left-color',
		'border-style',
		'border-top-style',
		'border-right-style',
		'border-bottom-style',
		'border-left-style',
		'border-width',
		'border-top-width',
		'border-left-width',
		'border-right-width',
		'border-bottom-width',
		'border-collapse',
		'border-spacing',
		'bottom',
		'clear',
		'clip',
		'color',
		'cursor',
		'direction',
		'display',
		'float',
		'font',
		'font-family',
		'font-size',
		'font-style',
		'font-variant',
		'font-weight',
		'height',
		'left',
		'letter-spacing',
		'line-height',
		'list-style',
		'list-style-image',
		'list-style-position',
		'list-style-type',
		'margin',
		'margin-top',
		'margin-right',
		'margin-bottom',
		'margin-left',
		'marker-offset',
		'marks',
		'overflow',
		'padding',
		'padding-top',
		'padding-bottom',
		'padding-right',
		'padding-left',
		'page-break-before',
		'position',
		'right',
		'size',
		'src',
		'table-layout',
		'text-align',
		'text-decoration',
		'text-indent',
		'text-transform',
		'top',
		'vertical-align',
		'visibility',
		'white-space',
		'width',
		'z-index'
	)

	CSSRegex = re.compile(r'([^{]+)\s?{\s?([^}]*)\s?}', re.I | re.M | re.U)
	PropertyRegex = re.compile(r'([^:]+):([^;]+);', re.I | re.M | re.U)
	CommentRegex = re.compile(r'/\*(.|[\r\n])*?\*/', re.I | re.M | re.U)
	
	def __init__(self):
		pass

	def parse(self):
		pass

	def duplicate_check(self):
		pass

def load_file(filename):
	""" Loads a file line by line into a variable and returns it."""
	infile = ''
	
	try:
		theFile = file(filename, "r")
	except IOError:
		sys.exit()

	for line in theFile:
		infile += line

	return infile

if __name__ == '__main__':
	output = CSSParser.CommentRegex.sub(' ', load_file(sys.argv[1]))
	output = CSSParser.CSSRegex.findall(output)

	containers = 0
	errors = 0

	for item in output:
		containers += 1
		properties = re.sub('\s+', ' ', item[1])
		proparray = CSSParser.PropertyRegex.findall(properties)
		container = item[0].strip()
	
		#print "Container: %s" % item[0].strip()
		#print "Contents: %s" %  properties
		print "Property Array: %s \n\n" % proparray
		
		for item in proparray:
			if item[0].strip().lower() not in CSSParser.ValidProperties:
				errors += 1
				print "WARNING: Invalid property '%s' in container '%s'" % (item[0].strip(), container)

	print "---\n\nFound %s containers and %s errors" % (containers, errors)
