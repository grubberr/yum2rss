#!/usr/bin/env python

import os
import re

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from Models import Repos
from Models import User
from Models import UserRepos

def getUserEntity(user):

	entity = User.all().filter('user =',user).get()

	if not entity:
		entity = User(user=user)
		entity.put()

	return entity


class AddReposPage(webapp.RequestHandler):

	def get(self):
		UserEntity = getUserEntity(users.get_current_user())
		user_urls = [ item.repos.url for item in UserEntity.UserRepos ]
		unused_ReposList = [ item for item in Repos.all().fetch(500) if item.url not in user_urls ]

		path = os.path.join(os.path.dirname(__file__) + '/templates', 'AddReposPage.html')
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(template.render(path,{ 'ReposList' : unused_ReposList }))

	def post(self):
		UserEntity = getUserEntity(users.get_current_user())
		key = self.request.get('key')

		self.response.headers['Content-Type'] = 'text/html'

		try:
			ReposEntity = db.get(db.Key(key))
			packages = self.request.get('packages')
			packages_list = list(set([ pkg for pkg in re.split(r'[\s,]+',packages) if pkg != '' ]))

			if packages_list:
				UserRepos(user=UserEntity, repos=ReposEntity, packages=packages_list).put()
				self.redirect('/home/')
			else:
				self.response.out.write('Packages cannot be empty')

		except db.BadKeyError:
			self.response.out.write('wrong id')

class EditReposPage(webapp.RequestHandler):

	def get(self):
		UserEntity = getUserEntity(users.get_current_user())
		key = self.request.get('key')

		self.response.headers['Content-Type'] = 'text/html'

		try:
			UserReposEntity = db.get(db.Key(key))
			assert UserReposEntity.user.key() == UserEntity.key()

			url = UserReposEntity.repos.url
			packages = ', '.join(UserReposEntity.packages)

			path = os.path.join(os.path.dirname(__file__) + '/templates', 'EditReposPage.html')
			self.response.out.write(template.render(path,{ 'url': url, 'key': key, 'packages' : packages }))

		except (db.BadKeyError, AssertionError):
			self.response.out.write('wrong id')

	def post(self):

		self.response.headers['Content-Type'] = 'text/html'

		try:
			UserReposEntity = db.get(db.Key(self.request.get('key')))

			packages = self.request.get('packages')
			packages_list = list(set([ pkg for pkg in re.split(r'[\s,]+',packages) if pkg != '' ]))

			if packages_list:
				UserReposEntity.packages = packages_list
				UserReposEntity.put()

				self.redirect('/home/')
			else:
				self.response.out.write('Packages cannot be empty')

		except db.BadKeyError:
			self.response.out.write('wrong id')

class DeleteReposPage(webapp.RequestHandler):

	def get(self):

		self.response.headers['Content-Type'] = 'text/html'

		try:
			db.delete(db.Key(self.request.get('key')))
			self.redirect('/home/')

		except db.BadKeyError:
			self.response.out.write('wrong id')

class MainPage(webapp.RequestHandler):

	def get(self):
		UserEntity  = getUserEntity(users.get_current_user())
		UserReposList = UserEntity.UserRepos.fetch(500)

		path = os.path.join(os.path.dirname(__file__) + '/templates', 'MainPage.html')
		self.response.headers['Content-Type'] = 'text/html'
		self.response.out.write(template.render(path,
				{ 'UserReposList' : UserReposList,
				  'nickname' : users.get_current_user().nickname(),
				  'logout' : users.create_logout_url('/'),
				  'user_key' : UserEntity.key()
				}))

application = webapp.WSGIApplication(
				[('/home/', MainPage),
				 ('/home/AddRepos', AddReposPage),
				 ('/home/EditRepos', EditReposPage),
				 ('/home/DeleteRepos', DeleteReposPage)],
				debug=False)

def main():
	run_wsgi_app(application)

if __name__ == '__main__':
	main()
