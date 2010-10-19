#!/usr/bin/env python

from __future__ import with_statement
import sys
import os

DIR_PATH = '/home/ant/GAE/google_appengine'

EXTRA_PATHS = [
  DIR_PATH,
  os.path.join(DIR_PATH, 'lib', 'antlr3'),
  os.path.join(DIR_PATH, 'lib', 'django'),
  os.path.join(DIR_PATH, 'lib', 'fancy_urllib'),
  os.path.join(DIR_PATH, 'lib', 'ipaddr'),
  os.path.join(DIR_PATH, 'lib', 'webob'),
  os.path.join(DIR_PATH, 'lib', 'yaml', 'lib'),
]

sys.path = EXTRA_PATHS + sys.path

import yaml

from google.appengine.ext.remote_api import remote_api_stub

def get_app_id():
	with file('app.yaml','r') as fp:
		data = yaml.load(fp)
	return data['application']

def auth_func():

	with open('/home/ant/Private/gmail.com') as fp:
		password = fp.readline()

	return 'grubberr@gmail.com', password

app_id = get_app_id()
host = '%s.appspot.com' % app_id

remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)
