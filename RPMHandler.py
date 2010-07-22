#!/usr/bin/python

from xml.sax import make_parser
import xml.sax.xmlreader
from xml.sax.handler import ContentHandler

import logging

class RPMHandler(ContentHandler):

	_tag_package = False
	_tag_name = False
	_tag_arch = False
	_tag_checksum = False

	def __init__(self, pkgs):
		self._buff = {}
		self.pkgs = []
		self.search_pkgs = pkgs

	def startElement(self, name, attrs):

		if name == 'package':
			self._tag_package = True

		if self._tag_package:

			if name == 'name':
				self._tag_name = True

			if name == 'time':
				self._buff['build'] = int(attrs['build'])

			if name == 'version':
				self._buff['epoch'] = attrs['epoch']
				self._buff['ver'] = attrs['ver']
				self._buff['rel'] = attrs['rel']

			if name == 'arch':
				self._tag_arch = True

			if name == 'checksum':
				self._tag_checksum = True

	def characters(self, content):

		if self._tag_name:
			self._buff['name'] = content

		if self._tag_arch:
			self._buff['arch'] = content

		if self._tag_checksum:
			self._buff['checksum'] = content

	def endElement(self, name):

		if self._tag_package:

			if name == 'name':
				self._tag_name = False

			if name == 'arch':
				self._tag_arch = False

			if name == 'checksum':
				self._tag_checksum = False

		if name == 'package':
			self._tag_package = False

			if self.search_pkgs.has_key(self._buff['name']) and self._buff['build'] > self.search_pkgs[self._buff['name']]:
				self.pkgs.append(self._buff)
			self._buff = {}
