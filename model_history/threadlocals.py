#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28

__author__ = u'王健'
try:
    from threading import local
except ImportError:
    from django.utils._threading_local import local

_thread_locals = local()
def get_current_user():
    return getattr(_thread_locals, 'user', None)

def set_log_entry(key,log):
    _thread_locals.logs[key]=log

def get_log_entry(key):
    return _thread_locals.logs.get(key,None)

def get_pre_entry(key):
    return _thread_locals.entrys.get(key,None)

def set_pre_entry(key,entry):
    _thread_locals.entrys[key]=entry

class ThreadLocals(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_request(self, request):
        _thread_locals.user = getattr(request, 'user', None)
        _thread_locals.logs = {}
        _thread_locals.entrys = {}