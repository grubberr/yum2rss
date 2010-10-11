#!/usr/bin/python

import remote_api
from google.appengine.ext import db

from Models import RPM
from Models import URL
from Models import LOG

def drop_all_entities(Model):

	count = 0
	q = Model.all(keys_only=True)

	while True:
		keys = q.fetch(100)
		if not keys:
			break
		count += len(keys)
		db.delete(keys)

	print '%s Model - %s entities deleted' % ( Model.kind(), count )

drop_all_entities(RPM)
drop_all_entities(URL)
drop_all_entities(LOG)
