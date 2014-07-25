# coding=utf-8
#Date:2014/7/10
#Email:wangjian2254@gmail.com
import logging
import sys
from django.conf import settings
from util.jsonresult import getResult


__author__ = u'王健'

class ExceptionMiddleware(object):
    """Middleware that gets various objects from the
    request object and saves them in thread local storage."""
    def process_exception(self, request,e):
        import time
        errorid = time.time()
        log=logging.getLogger()
        s = [u'错误码:%s'%errorid]
        s.append(u'%s:%s'%(request.method,request.path))
        user = getattr(request, 'user', None)
        if user.username:
            s.append(u'用户：%s'%user.username)
        else:
            s.append(u'未登录用户')
        s.append(u'出现以下错误：')
        etype, value, tb = sys.exc_info()
        s.append(value.message)
        s.append(u'错误代码位置如下：')
        while tb is not None:
            f = tb.tb_frame
            lineno = tb.tb_lineno
            co = f.f_code
            filename = co.co_filename
            name = co.co_name
            s.append(u'File "%s", line %d, in %s' % (filename, lineno, name))
            tb = tb.tb_next
        if not settings.DEBUG:
            log.error('\n    '.join(s))
            return getResult(False,u'服务器端错误,请联系管理员,错误标记码：%s'%errorid)
        else:
            m = '\n    '.join(s)
            log.error(m)
            return getResult(False,u'服务器端错误,错误如下：\n%s'%(m))