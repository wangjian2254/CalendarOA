#coding=utf-8
#author:u'王健'
#Date: 14-3-28
#Time: 下午10:49
import base64
from django.http import HttpResponse
from CalendarOA.settings import MEDIA_ROOT

__author__ = u'王健'

def decode( text, environ):
        """Try to magically decode ``text`` according to given ``environ``."""
        # List of charsets to try
        charsets = []

        # First append content charset given in the request
        content_type = environ.get("CONTENT_TYPE")
        if content_type and "charset=" in content_type:
            charsets.append(content_type.split("charset=")[1].strip())
        # Then append default Radicale charset
        # charsets.append(self.encoding)
        # Then append various fallbacks
        charsets.append("utf-8")
        charsets.append("iso8859-1")

        # Try to decode
        for charset in charsets:
            try:
                return text.decode(charset)
            except UnicodeDecodeError:
                pass
        raise UnicodeDecodeError

def davuser(request,user):
    authorization = request.environ.get("HTTP_AUTHORIZATION", None)

    if authorization:
        authorization = authorization.lstrip("Basic").strip()
        user, password = decode(base64.b64decode(
            authorization.encode("ascii")), request.environ).split(":", 1)

    else:
        res = HttpResponse("Unauthorized")
        res.status_code = 401
        return res
#     with open('%s/davuser.txt'%MEDIA_ROOT,'w') as f:
#         f.write(request.body)
    r='''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:CS="http://calendarserver.org/ns/">
  <response>
    <href>%s</href>
    <propstat>
      <prop>
         <displayname>%s</displayname>
    <caldav:calendar-user-address-set>
     <href>%s</href>
    </caldav:calendar-user-address-set>

    <caldav:schedule-inbox-URL>
     <href>%s/inbox/</href>
    </caldav:schedule-inbox-URL>
    <caldav:schedule-outbox-URL>
     <href>%s/outbox/</href>
    </caldav:schedule-outbox-URL>
    <principal-URL>
     <href>%s</href>
    </principal-URL>

      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
    <propstat>
      <prop>
        <C:calendar-home-set />
        <current-user-principal>
          <unauthenticated />
        </current-user-principal>
        <CS:dropbox-home-URL />
        <CS:email-address-set />
        <CS:notification-URL />
        <principal-URL>
          <unauthenticated />
        </principal-URL>
        <resource-id />
        <C:schedule-inbox-URL />
        <C:schedule-outbox-URL />
      </prop>
      <status>HTTP/1.1 404 Not Found</status>
    </propstat>
  </response>
</multistatus>
    '''
#     return HttpResponse(r)

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
  