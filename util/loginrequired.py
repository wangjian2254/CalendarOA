#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from util.jsonresult import getResult

__author__ = u'王健'

def client_login_required(func=None):
    def test(request, *args, **kwargs):
        if not request.user.is_anonymous():
            if  request.user.is_active:
                return func(request, *args, **kwargs)
            else:
                return getResult(False,u'用户已被禁用。', None,400)
        else:
            return getResult(False,u'', None,400)
    return test
