#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'

from django.conf.urls import patterns, url


urlpatterns = patterns('oamessage',
    # Examples:



    url(r'^updateMessage', 'view_message.updateMessage'),
    url(r'^getUnReadCount', 'view_message.getUnReadCount'),
    url(r'^flagMessage', 'view_message.flagMessage'),
    url(r'^getMessageByUser', 'view_message.getMessageByUser'),
    url(r'^getMessageById', 'view_message.getMessageById'),



)
