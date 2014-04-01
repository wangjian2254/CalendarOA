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
    url(r'^getContacts', 'view_contacts.getContacts'),
    url(r'^findUser', 'view_contacts.findUser'),
    url(r'^joinContacts', 'view_contacts.joinContacts'),
    url(r'^regUser', 'views.regUser'),
    url(r'^login', 'views.login'),
    url(r'^logout', 'views.logout'),
    url(r'^saveUser', 'views.saveUser'),
    url(r'^getMyGroup', 'view_group.getMyGroup'),
    url(r'^updateSchedule', 'views.updateSchedule'),
    url(r'^delSchedule', 'views.delSchedule'),
    url(r'^getScheduleByDate', 'views.getScheduleByDate'),
    url(r'^getTaskByStatus', 'view_task.getTaskByStatus'),
    url(r'^updateTask', 'view_task.updateTask'),
    url(r'^delTask', 'view_task.delTask'),
    url(r'^doTask', 'view_task.doTask'),
    url(r'^warningTask', 'warningcron.warningTask'),


)
