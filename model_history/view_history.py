#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
import threading
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'
c = threading.RLock()

def showActionFlag(flag):
    if flag == ADDITION:
        return u'新增'
    elif flag == CHANGE:
        return u'修改'
    elif flag == DELETION:
        return u'删除'
    else:
        return u'未知操作'

def log2dict(log):
    return {'id': log.pk, 'action_time': log.action_time.strftime("%Y-%m-%d %H:%M:%S"), 'username': log.user.username,
                      'nickname': log.user.first_name, 'action_flag': showActionFlag(log.action_flag), 'object_id':log.object_id,
                      'object_type':log.content_type.model_class()._meta.verbose_name, 'object_type_id':log.content_type_id,
                      'actionflag': log.action_flag, 'object_repr': log.object_repr, 'change_message':log.change_message}



@client_login_required
def getHistory(request):
    content_type_id = request.REQUEST.get('object_type', None)
    object_id = request.REQUEST.get('object_id',None)
    uid = request.REQUEST.get('uid', None)
    logquery = LogEntry.objects.all().order_by('-id')

    start = request.REQUEST.get('start', None)
    end = request.REQUEST.get('end', None)
    if start and end:
        with c:
            startdate = datetime.datetime.strptime(start, "%Y/%m/%d")
            enddate = datetime.datetime.strptime(end, "%Y/%m/%d") + datetime.timedelta(days=1)
        logquery = logquery.filter(action_time__lt=enddate, action_time__gte=startdate)
    elif content_type_id and object_id:
        logquery = logquery.filter(object_id=object_id)
    else:
        return getResult(False,u'请提供查询范围')

    if content_type_id:
        logquery=logquery.filter(content_type=content_type_id)
    if object_id:
        logquery = logquery.filter(object_id=object_id)
    if uid:
        logquery = logquery.filter(user=uid)
    l = []
    for log in logquery:
        l.append(log2dict(log))
    return getResult(True,u'获取到日志',l)
