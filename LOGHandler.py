#!/usr/bin/python

from xml.sax.handler import ContentHandler

class LOGHandler(ContentHandler):

	def __init__(self, pkgids, limit = False):

		self.pkgids = pkgids
		self.limit = limit

		self.__pkgid = False
		self.__changelog = False

		self.changelogs = {}

	def startElement(self, name, attrs):

		if name == 'package' and attrs['pkgid'] in self.pkgids:

			self.__pkgid = attrs['pkgid']
			self.changelogs[self.__pkgid] = []

		elif self.__pkgid and name == 'changelog':

			self.__changelog = { 'author' : attrs['author'], 'date' : attrs['date'], 'text' : [] }

	def characters(self, content):

		if self.__changelog:
			self.__changelog['text'].append(content)

	def endElement(self, name):

		if self.__changelog and name == 'changelog':

			self.changelogs[self.__pkgid].append(self.__changelog)
			self.__changelog = False

			if self.limit and len(self.changelogs[self.__pkgid]) >= self.limit:
				self.__pkgid = False

		elif self.__pkgid and name == 'package':
			self.__pkgid = False
