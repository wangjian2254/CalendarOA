#coding=utf-8
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'rili.views.index'),

    #caldav 协议支持（未开发成功，暂停）
    url('^calendar/dav/([a-zA-Z0-9_]{3,30})/user/', 'rili.caldav.davuser'),
    url('^calendar/([a-zA-Z0-9_]{3,30})/user/', 'rili.caldav.usercal'),
    url('^\.well-known/caldav', 'rili.caldav.know'),
    url(r'^principals/', 'rili.caldav.principals'),
    #caldav end

    url(r'^CalendarOA_Flex.html$', 'rili.views.index'),
    url(r'^ca/', include('rili.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
