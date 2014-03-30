#coding=utf-8
#author:u'王健'
#Date: 14-3-28
#Time: 下午10:49
from django.http import HttpResponse
from CalendarOA.settings import MEDIA_ROOT

__author__ = u'王健'



def davuser(request):
    with open('%s/davuser.txt'%MEDIA_ROOT,'w') as f:
        f.write(request.body)
    r='''<D:multistatus xmlns:CS="http://calendarserver.org/ns/" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:D="DAV:">
 <D:response>
  <D:href>/calendar/r/dav/w ellknow n/</D:href>
  <D:propstat>
   <D:prop>
    <D:resourcetype>
     <D:collection/>
    </D:resourcetype>
    <D:principal-URL xmlns:ns4="http://apple.com/ns/ical/">
     <D:href>/calendar/dav/wangjian/user/</D:href>
    </D:principal-URL>
   </D:prop>
   <D:status>HTTP/1.1 200 OK</D:status>
  </D:propstat>
  <D:propstat>
   <D:prop>
    <A:current-user-principal xmlns:A="DAV:"/>
   </D:prop>
   <D:status>HTTP/1.1 404 Not Found</D:status>
  </D:propstat>
 </D:response>
</D:multistatus>
    '''
    return HttpResponse(r)

def principals(request):
    with open('%s/principals.txt'%MEDIA_ROOT,'w') as f:
        f.write(request.body)
    return HttpResponse('')
def know(request):
    with open('%s/know.txt'%MEDIA_ROOT,'w') as f:
        f.write(request.body)
    r='''<D:multistatus xmlns:CS="http://calendarserver.org/ns/" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:D="DAV:">
 <D:response>
  <D:href>/.well-known/caldav</D:href>
  <D:propstat>
   <D:prop>
    <D:resourcetype>
     <D:collection/>
    </D:resourcetype>
    <D:principal-URL xmlns:ns4="http://apple.com/ns/ical/">
     <D:href>/calendar/dav/wangjian/user/</D:href>
    </D:principal-URL>
   </D:prop>
   <D:status>HTTP/1.1 200 OK</D:status>
  </D:propstat>
  <D:propstat>
   <D:prop>
    <A:current-user-principal xmlns:A="DAV:"/>
   </D:prop>
   <D:status>HTTP/1.1 404 Not Found</D:status>
  </D:propstat>
 </D:response>
</D:multistatus>
    '''
    return HttpResponse(r)
  