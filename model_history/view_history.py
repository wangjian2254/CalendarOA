#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'


def showActionFlag(flag):
    if flag == ADDITION:
        return u'新增'
    elif flag == CHANGE:
        return u'修改'
    elif flag == DELETION:
        return u'删除'
    else:
        return u'未知操作'


@client_login_required
def getMyHistory(request):
    start = request.REQUEST.get('start', None)
    end = request.REQUEST.get('end', None)
    if start and end:
        startdate = datetime.datetime.strptime(start, "%Y/%m/%d")
        enddate = datetime.datetime.strptime(end, "%Y/%m/%d") + datetime.timedelta(days=1)
        loglist = LogEntry.objects.filter(user=request.user, action_time__lt=enddate, action_time__gte=startdate)

        l = []
        for log in loglist:
            l.append({'id': log.pk, 'action_time': log.action_time.strftime("%Y-%m-%d %H:%M:%S"), 'username': log.user.username,
                      'nickname': log.user.first_name, 'action_flag': showActionFlag(log.action_flag),
                      'actionflag': log.action_flag, 'object_repr': log.object_repr})
        return getResult(True,u'获取到日志',l)
    else:
        return getResult(False, u'请提供查询范围')