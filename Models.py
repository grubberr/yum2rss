
from google.appengine.ext import db

class URL(db.Model):
	url = db.StringProperty()
	last_modified = db.StringProperty()

class RPM(db.Model):
	url = db.StringProperty()
	name = db.StringProperty()
	ver = db.StringProperty()
	rel = db.StringProperty()
	epoch = db.StringProperty()
	build = db.DateTimeProperty()
