#!/usr/bin/python

import sys

sys.path.insert(0,'/home/ant/GAE/google_appengine')
sys.path.insert(1,'/home/ant/GAE/google_appengine/lib/yaml/lib')

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
