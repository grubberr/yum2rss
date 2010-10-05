#!/usr/bin/python

import remote_api
import code

from google.appengine.ext import db
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.api import users

code.interact('App Engine interactive console for %s' % (remote_api.app_id,), None, locals())
