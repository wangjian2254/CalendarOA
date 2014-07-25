# coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from riliusers.threadlocalsperson import get_current_person, get_current_org
from util.jsonresult import getResult

__author__ = u'王健'


def client_login_required(func=None):
    def test(request, *args, **kwargs):
        if not request.user.is_anonymous():
            if request.user.is_active:
                return func(request, *args, **kwargs)
            else:
                return getResult(False, u'用户已被禁用。', None, 401)
        else:
            return getResult(False, u'请先登录', None, 404)

    return test


def client_login_org_required(func=None):
    @client_login_required
    def test(request, *args, **kwargs):
        if get_current_person() and get_current_org():
            if get_current_person().is_active:
                return func(request, *args, **kwargs)
            else:
                return getResult(False, u'您已经离开了 %s。' % get_current_org(), None, 402)
        else:
            return getResult(False, u'请先选择当前工作的组织或公司', None, 403)

    return test

def login_org_is_active_required(func=None):
    @client_login_org_required
    def test(request, *args, **kwargs):
        if get_current_org():
            if get_current_org().is_active:
                return func(request, *args, **kwargs)
            else:
                return getResult(False, u'%s 的可使用额度不足，请续费后继续使用。' % get_current_org(), None, 400)
        else:
            return getResult(False, u'请先选择当前工作的组织或公司', None, 403)

    return test