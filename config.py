#!/usr/bin/python

########################################### config ###################################################

urlfetch_limit = 1000000
# urlfetch_limit = 1048576

feed_link = 'http://repo2rss.appspot.com/rss'

urls = {
 'http://mirror.centos.org/centos/5/os/i386/repodata/primary.xml.gz'         : [ 'httpd', 'kernel', 'mysql', 'php' ],
 'http://mirror.centos.org/centos/5/updates/i386/repodata/primary.xml.gz'    : [ 'httpd', 'kernel', 'mysql', 'php' ],
 'http://mirror.centos.org/centos/5/addons/i386/repodata/primary.xml.gz'     : [ 'httpd', 'kernel', 'mysql', 'php' ],
 'http://mirror.centos.org/centos/5/extras/i386/repodata/primary.xml.gz'     : [ 'httpd', 'kernel', 'mysql', 'php' ],
 'http://mirror.centos.org/centos/5/centosplus/i386/repodata/primary.xml.gz' : [ 'httpd', 'kernel', 'mysql', 'php' ],
 'http://mirror.centos.org/centos/5/contrib/i386/repodata/primary.xml.gz'    : [ 'httpd', 'kernel', 'mysql', 'php' ],
 'http://mirror.ourdelta.org/yum/CentOS-MySQL50/5/repodata/primary.xml.gz'   : [ 'MySQL-OurDelta-client', 'MySQL-OurDelta-shared', 'MySQL-OurDelta-server' ],
 'http://74.50.3.177/repos/repodata/primary.xml.gz'                          : [ 'pkg1', 'pkg2', 'pkg3' ],
}

########################################### config ###################################################
