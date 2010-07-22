#!/usr/bin/python

import PyRSS2Gen
import datetime

from google.appengine.ext import db

from Models import RPM
import config

items = []
lastBuildDate = None

pkgs = db.GqlQuery('SELECT * FROM RPM ORDER BY build DESC')

for pkg in pkgs:

	if not lastBuildDate:
		lastBuildDate = pkg.build

	items.append(
		PyRSS2Gen.RSSItem(
			title = '%s:%s-%s-%s' % ( pkg.epoch, pkg.name, pkg.ver, pkg.rel ),
			link = pkg.url,
			description = pkg.url,
			guid = PyRSS2Gen.Guid(pkg.url,1),
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
