#!/usr/bin/env python

import remote_api
from google.appengine.ext import db

from Models import RPM
from Models import Repos
from Models import LOG
from Models import User
from Models import UserRepos

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
drop_all_entities(Repos)
drop_all_entities(LOG)
drop_all_entities(User)
drop_all_entities(UserRepos)
