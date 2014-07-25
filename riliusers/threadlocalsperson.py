#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_person():
    return getattr(_thread_locals, 'person', None)

def get_current_org():
    return getattr(_thread_locals, 'org', None)


class ThreadLocals(object):
    def process_request(self, request):
        _thread_locals.person = getattr(request.session, 'person', None)
        _thread_locals.org = getattr(request.session, 'org', None)
