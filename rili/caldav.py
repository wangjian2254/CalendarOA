#coding=utf-8
#author:u'王健'
#Date: 14-3-28
#Time: 下午10:49
import base64
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from CalendarOA.settings import MEDIA_ROOT

__author__ = u'王健'

caldavlogin = u'''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav" xmlns:CS="http://calendarserver.org/ns/">
  <response>
    <href>%s</href>
    <propstat>
      <prop>
         <displayname>%s</displayname>
    <caldav:calendar-user-address-set>
     <href>%s</href>
    </caldav:calendar-user-address-set>
    <principal-collection-set>
          <href>%s</href>
        </principal-collection-set>
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
</multistatus>'''

loginresult='''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
  <response>
    <href>%s</href>
    <propstat>
      <prop>
        <current-user-principal>
          <href>%s</href>
        </current-user-principal>
        <principal-URL>
          <href>%s</href>
        </principal-URL>
        <resourcetype>
          <C:calendar />
          <collection />
        </resourcetype>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
  </response>
</multistatus>'''

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
        user = authenticate(username=user,password=password)
        login(request,user)
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
        print loginresult%(request.path,'/calendar/%s/user/'%user,'/calendar/%s/user/'%user)
        # r = HttpResponse(caldavlogin%(request.path,'王健的日历','/calendar/%s/user/'%user,'/calendar/%s/user/'%user,'/calendar/%s/user/'%user,'/principals/'))
        r = HttpResponse(loginresult%(request.path,'/calendar/%s/user/'%user,'/calendar/%s/user/'%user))
        r['Content-Type']='text/xml'
        r['DAV']='1, 2, 3, calendar-access, addressbook, extended-mkcol'
        r.status_code = 207
        return r

    else:
        # Radicale - Password Required
        res = HttpResponse("Unauthorized")
        res.status_code = 401
        res['WWW-Authenticate']='Basic realm=\"%s\"'%('Radicale - Password Required',)
        return res


def usercal(request,user):
    authorization = request.environ.get("HTTP_AUTHORIZATION", None)
    print authorization
    if request.method == 'PROPFIND':
        r = HttpResponse(caldavlogin%(request.path,u'王健的日历','/calendar/%s/user/'%user,'/calendar/%s/user/'%user,'/calendar/%s/user/'%user,'/calendar/%s/user/'%user,'/principals/'))

        r['Content-Type']='text/xml'
        r['DAV']='1, 2, 3, calendar-access, addressbook, extended-mkcol'
        r.status_code = 207
        return r
    else:

        r = HttpResponse(loginresult%(request.path,'/calendar/%s/user/'%user,'/calendar/%s/user/'%user))
        r['Allow']='DELETE, HEAD, GET, MKCALENDAR, MKCOL, MOVE,OPTIONS, PROPFIND, PROPPATCH, PUT, REPORT'
        r['Content-Type']='text/xml'
        r['DAV']='1, 2, 3, calendar-access, addressbook, extended-mkcol'
        return r

def principals(request):
    r='''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
  <response>
    <href>/principals/</href>
    <propstat>
      <prop>
        <resourcetype>
          <C:calendar />
          <collection />
        </resourcetype>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
    <propstat>
      <prop>
        <current-user-principal>
          <unauthenticated />
        </current-user-principal>
        <principal-URL>
          <unauthenticated />
        </principal-URL>
      </prop>
      <status>HTTP/1.1 404 Not Found</status>
    </propstat>
  </response>
</multistatus>
    '''
    h= HttpResponse(r)
    h.status_code = 207
    return h
def know(request):
    # with open('%s/know.txt'%MEDIA_ROOT,'w') as f:
    #     f.write(request.body)
    r='''<?xml version="1.0"?>
<multistatus xmlns="DAV:" xmlns:C="urn:ietf:params:xml:ns:caldav">
  <response>
    <href>/.well-known/caldav</href>
    <propstat>
      <prop>
        <resourcetype>
          <C:calendar />
          <collection />
        </resourcetype>
      </prop>
      <status>HTTP/1.1 200 OK</status>
    </propstat>
    <propstat>
      <prop>
        <current-user-principal>
          <unauthenticated />
        </current-user-principal>
        <principal-URL>
          <unauthenticated />
        </principal-URL>
      </prop>
      <status>HTTP/1.1 404 Not Found</status>
    </propstat>
  </response>
</multistatus>
    '''
    h= HttpResponse(r)
    h.status_code = 207
    return h
  