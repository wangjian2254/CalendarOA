from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'rili.views.index'),
    url('^calendar/dav/wangjian/user/', 'rili.caldav.davuser'),
    url('^\.well-known/caldav', 'rili.caldav.know'),
    url(r'^principals/', 'rili.caldav.principals'),
    url(r'^CalendarOA_Flex.html$', 'rili.views.index'),
    url(r'^ca/', include('rili.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
