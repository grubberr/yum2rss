#!/usr/bin/env python

########################################### config ###################################################

urlfetch_limit = 1000000
# urlfetch_limit = 1048576

feed_link = 'http://yum2rss.appspot.com/rss'

urls = {
 'http://mirror.centos.org/centos/5/os/i386'         : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/5/updates/i386'    : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/5/addons/i386'     : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/5/extras/i386'     : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/5/centosplus/i386' : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/5/contrib/i386'    : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],

 'http://mirror.centos.org/centos/4/os/i386'         : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/4/updates/i386'    : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/4/addons/i386'     : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/4/extras/i386'     : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/4/centosplus/i386' : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],
 'http://mirror.centos.org/centos/4/contrib/i386'    : [ 'httpd', 'kernel', 'mysql', 'php', 'selinux-policy', 'glibc', 'kernel-xen' ],

 'http://mirror.ourdelta.org/yum/CentOS-MySQL50/5'   : [ 'MySQL-OurDelta-client', 'MySQL-OurDelta-shared', 'MySQL-OurDelta-server' ],
 'http://downloads.mongodb.org/distros/centos/5.4/os/i386' : [ 'mongo-stable', 'mongo-stable-server' ],

 'http://74.50.3.177/repos'                          : [ 'pkg1', 'pkg2', 'pkg3' ],

 'http://download.fedoraproject.org/pub/epel/5/i386' : [ 'Django', 'awstats', 'erlang', 'mysql-proxy',
							 'nagios', 'ocaml', 'perl-Crypt-CBC', 'phpMyAdmin', 'phpPgAdmin', 'python-GeoIP',
							 'python-twisted-core', 'python26', 'wordpress' ]
}

########################################### config ###################################################
