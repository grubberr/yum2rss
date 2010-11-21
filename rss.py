#!/usr/bin/env python

import PyRSS2Gen
import datetime

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.api.datastore_errors import BadRequestError

from Models import RPM
from Models import User
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

	output += "<p><strong>Change Log:</strong></p>\n"
	output += "<pre>\n"
	for logs in pkg.changelogs[0:3]:
		output += "%s - %s\n%s\n" % ( logs.date.ctime(), logs.author, logs.text )
	output += "</pre>\n"

	return output

def get_link(pkg):
	return pkg.url + '/' + pkg.location

def get_pkgs(UserEntity):

	show_days = 3
	show_nums = 20

	def get_base_query():
		return RPM.all().filter('haslog =',True).order('-build').filter('users =',UserEntity)

	pkgs = get_base_query().filter('build >',(datetime.datetime.now() - datetime.timedelta(days=show_days))).fetch(100)

	if len(pkgs) == 0:
		pkgs = get_base_query().fetch(show_nums)
	elif 0 < len(pkgs) < show_nums:
		pkgs += get_base_query().filter('build <',pkgs[-1].build).fetch(show_nums - len(pkgs))

	return pkgs

class MainPage(webapp.RequestHandler):

	def get(self):

		key = self.request.get('key')

		if key:

			try:
				UserEntity = db.get(db.Key(key))
			except (db.BadKeyError, BadRequestError):
				UserEntity = None

			if isinstance(UserEntity,User):
				items = []
				lastBuildDate = None

				for pkg in get_pkgs(UserEntity):

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

				self.response.headers['Content-Type'] = 'text/xml'
				self.response.out.write(rss.to_xml())
				return

		self.error(404)


application = webapp.WSGIApplication(
				[('/rss', MainPage)],
				debug=False)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
