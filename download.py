#!/usr/bin/python

import sys
import zlib
import os
import logging
import cgi

import datetime
import time
import xml.etree.cElementTree as ET

from xml.sax import make_parser
import xml.sax.xmlreader
from xml.sax.handler import ContentHandler

from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db

from Models import RPM
from Models import URL
import config
from RPMHandler import RPMHandler

def get_last_modified(url):
	query = URL().all().filter('url =',url)
	entity = query.get()
	if entity:
		return entity.last_modified
	else:
		return None

def set_last_modified(url,last_modified):
	query = URL().all().filter('url =',url)
	entity = query.get()
	if entity:
		entity.last_modified = last_modified
	else:
		entity = URL(url=url,last_modified=last_modified)
	entity.put()

if os.environ['PATH_INFO'] == '/download':

	for repos in config.urls.keys():
		url = repos + '/repodata/repomd.xml'
		params = { 'url': url,
			   'repos': repos,
			   'parser': '/parse_repomd' }
		taskqueue.Queue('url-queue').add(taskqueue.Task(url='/url_task',params=params))

elif os.environ['PATH_INFO'] == '/url_task':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	repos = form.getfirst('repos')
	parser = form.getfirst('parser')

	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	headers = {}
	if get_last_modified(url):
		headers = {'If-Modified-Since': get_last_modified(url) }
	result = urlfetch.fetch(url,method=urlfetch.HEAD,headers=headers,deadline=10)

	if result.status_code == 200L:

		memcache.set('last-modified',result.headers['last-modified'],namespace=url)

		length = int(result.headers['Content-Length'])

		if result.headers.has_key('Accept-Ranges') or ( length < config.urlfetch_limit ):

			ranges = map(lambda x,y: [x,y],range(0,length-1,config.urlfetch_limit),range(config.urlfetch_limit-1,length,config.urlfetch_limit))
			ranges[-1][1] = length - 1

			memcache.set('ranges',ranges,namespace=url)
			memcache.set('lock',len(ranges),namespace=url)
			memcache.delete('count',namespace=url)

			for _range in ranges:
				params = { 'url': url,
					   'repos': repos,
					   'parser': parser,
					   'range_start': _range[0],
					   'range_end': _range[1] }
				taskqueue.Queue('download-chunk-queue').add(taskqueue.Task(url='/download_chunk_task', params=params))

elif os.environ['PATH_INFO'] == '/download_chunk_task':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	repos = form.getfirst('repos')
	parser = form.getfirst('parser')
	_range = ( int(form.getfirst('range_start')), int(form.getfirst('range_end')) )

	logging.info('bytes=%d-%d' % ( _range[0], _range[1] ))
	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	result = urlfetch.fetch(url,method=urlfetch.GET,headers={'Range': 'bytes=%d-%d' % ( _range[0], _range[1] )},deadline=10)
	memcache.set("%d-%d" % ( _range[0], _range[1] ),result.content,namespace=url)

	if memcache.decr('lock',namespace=url) == 0:
		taskqueue.Queue('parse-xml-queue').add(taskqueue.Task(url=parser,params = { 'url': url, 'repos': repos }))

elif os.environ['PATH_INFO'] == '/parse_repomd':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	repos = form.getfirst('repos')

	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	try:

		ranges = memcache.get('ranges',namespace=url)
		assert ranges, "memcache key 'ranges' invalid"
		ranges = [ "%d-%d" % ( r[0], r[1] ) for r in ranges ]
		ranges_data = memcache.get_multi(ranges,namespace=url)

		xml = ''
		for _range in ranges:
			assert ranges_data.has_key(_range), "memcache key '%s' invalid" % ( _range, )
			xml += ranges_data[_range]

		primary = False

		metadata = ET.fromstring(xml)
		for data in metadata.findall('{http://linux.duke.edu/metadata/repo}data'):
			if data.attrib['type'] == 'primary':
				location = data.find('{http://linux.duke.edu/metadata/repo}location')
				primary = location.attrib['href']

		assert primary, "wrong repomd.xml file"
		url = repos + '/' + primary

		params = { 'url': url,
			   'repos': repos,
			   'parser': '/parse_xml_task' }
		taskqueue.Queue('url-queue').add(taskqueue.Task(url='/url_task',params=params))

	except:
		logging.warning("Unexpected error: %s" % ( sys.exc_info()[1], ))

elif os.environ['PATH_INFO'] == '/parse_xml_task':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	repos = form.getfirst('repos')

	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	d = zlib.decompressobj(16 + zlib.MAX_WBITS)

	pkgs = {}
	query = db.GqlQuery('SELECT * FROM RPM WHERE name = :1 AND url = :2 ORDER BY build DESC LIMIT 1')
	for _pkg in config.urls[repos]:
		query.bind(_pkg,repos)
		if query.count() > 0:
			pkgs[_pkg] = int(time.mktime(query.get().build.timetuple()))
		else:
			pkgs[_pkg] = 1

	ch = RPMHandler(pkgs)

	p = make_parser(['xml.sax.xmlreader.IncrementalParser'])
	p.setContentHandler(ch)

	try:

		for _range in memcache.get('ranges',namespace=url):

			content = memcache.get("%d-%d" % ( _range[0], _range[1] ),namespace=url)
			data = d.decompress(content)
			p.feed(data)

		for i in ch.pkgs:
			pkg = RPM()
			pkg.url = repos
			pkg.name = i['name']
			pkg.ver = i['ver']
			pkg.rel = i['rel']
			pkg.epoch = i['epoch']
			pkg.arch = i['arch']
			pkg.checksum = i['checksum']
			pkg.summary = ''.join(i['summary'])
			pkg.description = ''.join(i['description'])
			pkg.build = datetime.datetime.fromtimestamp(i['build'])
			pkg.location = i['location']
			pkg.put()

		set_last_modified(url,memcache.get('last-modified',namespace=url))

	except:
		logging.warning("Unexpected error: %s" % ( sys.exc_info()[1], ))

	# flush memory
	for _range in memcache.get('ranges',namespace=url):
		memcache.delete("%d-%d" % ( _range[0], _range[1] ),namespace=url)
	memcache.delete('ranges',namespace=url)
	memcache.delete('last-modified',namespace=url)
	memcache.delete('lock',namespace=url)
