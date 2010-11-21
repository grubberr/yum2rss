#!/usr/bin/env python

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
from Models import Repos
from Models import LOG
from Models import UserRepos
import config
from RPMHandler import RPMHandler
from LOGHandler import LOGHandler

def get_last_modified(url):
	query = Repos.all().filter('url =',url)
	entity = query.get()
	if entity:
		return entity.last_modified
	else:
		return None

def set_last_modified(url,last_modified):
	query = Repos.all().filter('url =',url)
	entity = query.get()
	if entity:
		entity.last_modified = last_modified
	else:
		entity = Repos(url=url,last_modified=last_modified)
	entity.put()

def get_pkgs_for_url(url):
	ReposEntiry = Repos.all().filter('url =',url).get()
	pkgs = set()
	if ReposEntiry:
		for UserReposEntiry in ReposEntiry.UserRepos:
			for pkg in UserReposEntiry.packages:
				pkgs.add(pkg)

	return list(pkgs)

if os.environ['PATH_INFO'] == '/download':

	urls = set()
	for UserRepos in UserRepos.all():
		urls.add(UserRepos.repos.url.encode())

	for repos in urls:
		url = repos + '/repodata/repomd.xml'
		params = { 'url': url,
			   'repos': repos,
			   'parser': '/parse_repomd' }
		taskqueue.Queue('url-queue').add(taskqueue.Task(url='/url_task',params=params))

elif os.environ['PATH_INFO'] == '/url_task':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	other_url = form.getfirst('other_url')
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
					   'other_url': other_url,
					   'repos': repos,
					   'parser': parser,
					   'range_start': _range[0],
					   'range_end': _range[1] }
				taskqueue.Queue('download-chunk-queue').add(taskqueue.Task(url='/download_chunk_task', params=params))

elif os.environ['PATH_INFO'] == '/download_chunk_task':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	other_url = form.getfirst('other_url')
	repos = form.getfirst('repos')
	parser = form.getfirst('parser')
	_range = ( int(form.getfirst('range_start')), int(form.getfirst('range_end')) )

	logging.info('bytes=%d-%d' % ( _range[0], _range[1] ))
	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	result = urlfetch.fetch(url,method=urlfetch.GET,headers={'Range': 'bytes=%d-%d' % ( _range[0], _range[1] )},deadline=10)
	memcache.set("%d-%d" % ( _range[0], _range[1] ),result.content,namespace=url)

	if memcache.decr('lock',namespace=url) == 0:
		taskqueue.Queue('parse-xml-queue').add(taskqueue.Task(url=parser,params = { 'url': url, 'other_url': other_url, 'repos': repos }))

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
		other = False

		metadata = ET.fromstring(xml)
		for data in metadata.findall('{http://linux.duke.edu/metadata/repo}data'):
			if data.attrib['type'] == 'primary':
				location = data.find('{http://linux.duke.edu/metadata/repo}location')
				primary = location.attrib['href']
			if data.attrib['type'] == 'other':
				location = data.find('{http://linux.duke.edu/metadata/repo}location')
				other = location.attrib['href']

		assert primary, "wrong repomd.xml file"
		assert other, "wrong repomd.xml file"
		url = repos + '/' + primary
		other_url = repos + '/' + other

		params = { 'url': url,
			   'other_url': other_url,
			   'repos': repos,
			   'parser': '/parse_xml_task' }
		taskqueue.Queue('url-queue').add(taskqueue.Task(url='/url_task',params=params))

	except:
		logging.warning("Unexpected error: %s" % ( sys.exc_info()[1], ))

elif os.environ['PATH_INFO'] == '/parse_xml_task':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	other_url = form.getfirst('other_url')
	repos = form.getfirst('repos')

	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	d = zlib.decompressobj(16 + zlib.MAX_WBITS)

	pkgs = {}
	query = db.GqlQuery('SELECT * FROM RPM WHERE name = :1 AND url = :2 ORDER BY build DESC LIMIT 1')
	for _pkg in get_pkgs_for_url(repos):
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


		ReposEntiry = Repos.all().filter('url =',repos).get()

		for i in ch.pkgs:
			UserKeys = [ UserRepos.user.key() for UserRepos in ReposEntiry.UserRepos.filter('packages =',i['name']) ]
			if UserKeys:
				pkg = RPM()
				pkg.users = UserKeys
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

		params = { 'url': other_url,
			   'repos': repos,
			   'parser': '/parse_other' }
		taskqueue.Queue('url-queue').add(taskqueue.Task(url='/url_task',params=params))

	except:
		logging.warning("Unexpected error: %s" % ( sys.exc_info()[1], ))

	# flush memory
	for _range in memcache.get('ranges',namespace=url):
		memcache.delete("%d-%d" % ( _range[0], _range[1] ),namespace=url)
	memcache.delete('ranges',namespace=url)
	memcache.delete('last-modified',namespace=url)
	memcache.delete('lock',namespace=url)

elif os.environ['PATH_INFO'] == '/parse_other':

	form = cgi.FieldStorage()
	url = form.getfirst('url')
	repos = form.getfirst('repos')

	logging.info('url=%s' % ( url, ) )
	logging.info('X-AppEngine-TaskRetryCount=%s' % ( os.environ['HTTP_X_APPENGINE_TASKRETRYCOUNT'], ))

	RPM_hash = {}
	for pkg in db.GqlQuery('SELECT * FROM RPM WHERE url = :1 AND haslog = :2',repos,False):
		RPM_hash[pkg.checksum] = pkg

	ch = LOGHandler(RPM_hash.keys(),limit=3)
	p = make_parser(['xml.sax.xmlreader.IncrementalParser'])
	p.setContentHandler(ch)
	d = zlib.decompressobj(16 + zlib.MAX_WBITS)

	try:
		for _range in memcache.get('ranges',namespace=url):
			content = memcache.get("%d-%d" % ( _range[0], _range[1] ),namespace=url)
			data = d.decompress(content)
			p.feed(data)

		LOG_list = []

		for pkgid in ch.changelogs.keys():

			for changelog in ch.changelogs[pkgid]:
				log = LOG()
				log.author = changelog['author']
				log.date = datetime.datetime.fromtimestamp(int(changelog['date']))
				log.text = ''.join(changelog['text'])
				log.RPM = RPM_hash[pkgid].key()
				LOG_list.append(log)

			RPM_hash[pkgid].haslog = True

		db.put(LOG_list)
		db.put(RPM_hash.values())

		set_last_modified(url,memcache.get('last-modified',namespace=url))

	except:
		logging.warning("Unexpected error: %s" % ( sys.exc_info()[1], ))

	# flush memory
	for _range in memcache.get('ranges',namespace=url):
		memcache.delete("%d-%d" % ( _range[0], _range[1] ),namespace=url)
	memcache.delete('ranges',namespace=url)
	memcache.delete('last-modified',namespace=url)
	memcache.delete('lock',namespace=url)
