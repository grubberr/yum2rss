#!/usr/bin/python

import PyRSS2Gen
import datetime

from google.appengine.ext import db

from Models import RPM
import config

def get_title(pkg):
	if pkg.epoch == '0':
		title = '%s-%s-%s.%s' % ( pkg.name, pkg.ver, pkg.rel, pkg.arch )
	else:
		title = '%s:%s-%s-%s.%s' % ( pkg.epoch, pkg.name, pkg.ver, pkg.rel, pkg.arch )

	return title

def get_description(pkg):
	description = "<br/>\n".join(pkg.description.split("\n")) + "<br/>\n"
	output = """<p><strong> %s </strong> - %s </p>
<p> %s </p>
""" % ( pkg.name, pkg.summary, description )

	return output

def get_link(pkg):
	return pkg.url + '/' + pkg.location

items = []
lastBuildDate = None

pkgs = db.GqlQuery('SELECT * FROM RPM ORDER BY build DESC')

for pkg in pkgs:

	if not lastBuildDate:
		lastBuildDate = pkg.build

	items.append(
		PyRSS2Gen.RSSItem(
			title = get_title(pkg),
			link = get_link(pkg),
			description = get_description(pkg),
			guid = PyRSS2Gen.Guid(pkg.checksum,0),
			pubDate = pkg.build,
	))

if not lastBuildDate:
	lastBuildDate = datetime.datetime.fromtimestamp(0)

rss = PyRSS2Gen.RSS2(

    title = "rpm feed",
    link = config.feed_link,
    description = "rpm feed",
    lastBuildDate = lastBuildDate,
    items = items

)

print "Content-type: text/xml\n"
print rss.to_xml()
