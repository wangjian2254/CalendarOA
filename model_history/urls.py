#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'

from django.conf.urls import patterns, url


urlpatterns = patterns('model_history',
    # Examples:



    url(r'^getMyHistory', 'view_history.getHistory'),



)
