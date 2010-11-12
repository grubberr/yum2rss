
from google.appengine.ext import db

class Repos(db.Model):
	url = db.StringProperty()
	last_modified = db.StringProperty()

class RPM(db.Model):
	url = db.StringProperty()
	name = db.StringProperty()
	ver = db.StringProperty()
	rel = db.StringProperty()
	epoch = db.StringProperty()
	arch = db.StringProperty()
	checksum = db.StringProperty()
	summary = db.StringProperty(multiline=True)
	description = db.TextProperty()
	location = db.StringProperty()
	build = db.DateTimeProperty()
	haslog = db.BooleanProperty(default=False)

class LOG(db.Model):
	author = db.StringProperty()
	date = db.DateTimeProperty()
	text = db.TextProperty()
	RPM = db.ReferenceProperty(RPM,collection_name='changelogs')
