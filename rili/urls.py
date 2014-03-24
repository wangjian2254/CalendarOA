#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'

from django.conf.urls import patterns, url


urlpatterns = patterns('rili',
    # Examples:
    url(r'^menu.xml$', 'views.menu'),
    url(r'^allmanager$', 'views.allmanager'),
    url(r'^currentUser', 'views.currentUser'),
    url(r'^getHyList', 'views.getHyList'),
    url(r'^regUser', 'views.regUser'),
    url(r'^login', 'views.login'),
    url(r'^logout', 'views.logout'),
    url(r'^saveUser', 'views.saveUser'),
    url(r'^updateSchedule', 'views.updateSchedule'),
    url(r'^getScheduleByDate', 'views.getScheduleByDate'),


)
