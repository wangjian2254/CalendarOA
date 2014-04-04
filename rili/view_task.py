#coding=utf-8
#author:u'王健'
#Date: 14-4-1
#Time: 上午7:04
import datetime
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rili.models import Task, RiLiWarning
from rili.warningtools import adjustRiLiWarning
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'



@client_login_required
def getTaskByStatus(request):
    '''
    date 的格式为 yyyymmdd
    如果没有则返回空
    获取日期间的任务
    '''
    status = request.REQUEST.get('status', 'false')
    today = request.REQUEST.get('today', 'false')
    user = request.user
    if status=='false':
        status=False
    else:
        status=True
    if today=='false':
        today=False
    else:
        today=True

    result = []
    taskdict = {}
    taskpkset = set()
    tquery =Task.objects.filter(author=user)
    if today:
        tquery = tquery.filter(status=status)
    else:
        n=datetime.datetime.strptime(datetime.datetime.now().strftime('%Y%m%d'), "%Y%m%d")
        tquery = tquery.filter(Q(status=status)|Q(startdate__lte=n, enddate__gte=n))
    for task in tquery.order_by('startdate'):
        if task.pk in taskpkset:
            continue
        taskpkset.add(task.pk)

        if not taskdict.has_key('%s' % task.pk):
            s = {'id': task.pk, 'title': task.title, 'desc': task.desc, 'type': 'task', 'author': task.author.username,
                 'authornickname': task.author.first_name, 'startdate': task.startdate.strftime('%Y%m%d'),
                 'color': task.color,  'zentaourl':task.getZentaoUrl(),
                 'warningkind': set(), 'warningtime': set(), 'status':task.status}
            if task.enddate:
                s['enddate'] = task.enddate.strftime('%Y%m%d')

            for warning in RiLiWarning.objects.filter(type='Task',fatherid=task.pk).order_by('type'):
                s['warningkind'].add(warning.warning_type)
                if len(s['warningkind'])==0 or (len(s['warningkind'])==1 and warning.warning_type in s['warningkind']):
                    s['warningtime'].add(warning.timenum)
            s['warningkind']=list(s['warningkind'])
            s['warningtime']=list(s['warningtime'])
            s['warningtime'].sort()
            s['warningtime'].reverse()
            result.append(s)
    return getResult(True, '', result)




@client_login_required
@transaction.commit_on_success
def updateTask(request):
    id = request.REQUEST.get('id', '')
    title = request.REQUEST.get('title', '')
    desc = request.REQUEST.get('desc', '')
    startdate = request.REQUEST.get('startdate', '')
    enddate = request.REQUEST.get('enddate', '')

    color = request.REQUEST.get('color', '')

    warning_email = request.REQUEST.get('warning_email', '')
    warning_sms = request.REQUEST.get('warning_sms', '')
    warning_rtx = request.REQUEST.get('warning_rtx', '')
    wl = []
    if warning_email.lower() == 'true':
        wl.append('email')
    if warning_rtx.lower() == 'true':
        wl.append('rtx')
    if warning_sms.lower() == 'true':
        wl.append('sms')
    warning_time1 = request.REQUEST.get('warning_time1', '')
    warning_time2 = request.REQUEST.get('warning_time2', '')
    wtl = [warning_time1, warning_time2]


    if not title or not startdate :
        return getResult(False, u'请完善信息', None)
    if id:
        task = Task.objects.get(pk=id)
        RiLiWarning.objects.filter(warning_type__in=wl).filter(type='Task', fatherid=task.pk).delete()
    else:
        task = Task()
    task.title = title
    task.desc = desc
    task.startdate = datetime.datetime.strptime(startdate, "%Y%m%d")
    task.enddate = datetime.datetime.strptime(enddate, "%Y%m%d")


    task.color = int(color)
    task.author = request.user
    task.save()




    for wt in wl:
        for w in wtl:
            if w:
                rw = RiLiWarning()
                rw.fatherid = task.pk
                rw.type = 'Task'
                rw.warning_type = wt
                rw.timenum = int(w)
                rw.is_repeat = True
                rw.is_ok = True
                rw.save()
    task.save()
    return getResult(True, u'保存成功', task.pk)


@client_login_required
@transaction.commit_on_success
def delTask(request):
    id = request.REQUEST.get('id', '')
    schedule = Task.objects.get(pk=id)
    schedule.delete()
    return getResult(True, u'删除成功', id)

@client_login_required
@transaction.commit_on_success
def doTask(request):
    id = request.REQUEST.get('id', '')
    do = request.REQUEST.get('do', '')
    schedule = Task.objects.get(pk=id)
    if do=='true':
        schedule.status=True
    else:
        schedule.status=False
    schedule.save()
    return getResult(True, u'删除成功', id)
