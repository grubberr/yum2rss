#!/usr/bin/python

from google.appengine.ext import db

from Models import RPM
from Models import URL

db.delete(RPM.all().fetch(500))
db.delete(RPM.all().fetch(500))
db.delete(RPM.all().fetch(500))

db.delete(URL.all().fetch(500))
db.delete(URL.all().fetch(500))
db.delete(URL.all().fetch(500))
