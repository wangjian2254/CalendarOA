#coding=utf-8
#author:u'王健'
#Date: 14-4-1
#Time: 上午7:04
import datetime
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from rili.models import Task, RiLiWarning
from util.jsonresult import getResult
from util.loginrequired import client_login_required

__author__ = u'王健'



@client_login_required
def getTaskByDate(request):
    '''
    date 的格式为 yyyymmdd
    如果没有则返回空
    获取日期间的任务
    '''
    startdatestr = request.REQUEST.get('startdate', '')
    enddatestr = request.REQUEST.get('enddate', '')
    if startdatestr and enddatestr:
        user = request.user
        startdate = datetime.datetime.strptime(startdatestr, "%Y%m%d")
        enddate = datetime.datetime.strptime(enddatestr, "%Y%m%d")

        result = {}
        taskdict = {}
        taskpkset = set()
        for task in Task.objects.filter(Q(author=user) | Q(users=user) ).filter(
                                                Q(startdate__lte=startdate, enddate__gte=enddate) | Q(
                                                startdate__lte=startdate, enddate__gte=startdate) | Q(
                                        startdate__gte=startdate, enddate__lte=enddate) | Q(startdate__lte=enddate,
                                                                                            enddate__gte=enddate) | Q(
                        startdate__lte=enddate, enddate=None)).order_by('time_start'):
            if task.pk in taskpkset:
                continue
            taskpkset.add(task.pk)

            if not taskdict.has_key('%s' % task.pk):
                s = {'id': task.pk, 'title': task.title, 'desc': task.desc,
                        'author':task.author.username, 'authornickname':task.author.first_name,
                     'startdate': task.startdate.strftime('%Y%m%d'),
                     'color': task.color,
                     'users': [{'username': u.username, 'nickname': u.first_name} for u in
                               task.users.all()]}
                s['enddate'] = task.enddate.strftime('%Y%m%d')

                s['warningkind']=set()
                s['warningtime']=set()
                for warning in RiLiWarning.objects.filter(type='Task',fatherid=task.pk).order_by('type'):
                    s['warningkind'].add(warning.warning_type)
                    if len(s['warningkind'])==0 or (len(s['warningkind'])==1 and warning.warning_type in s['warningkind']):
                        s['warningtime'].add(warning.timenum)
                s['warningkind']=list(s['warningkind'])
                s['warningtime']=list(s['warningtime'])
                s['warningtime'].sort()
                s['warningtime'].reverse()
                taskdict['%s' % task.pk] = s
            result.append(str(task.pk))
        return getResult(True, '', {"taskmap":taskdict,'tasklist':result})
    else:
        return getResult(False, '', None)



@client_login_required
@transaction.commit_on_success
def updateTask(request):
    id = request.REQUEST.get('id', '')
    title = request.REQUEST.get('title', '')
    desc = request.REQUEST.get('desc', '')
    startdate = request.REQUEST.get('startdate', '')
    enddate = request.REQUEST.get('enddate', '')

    color = request.REQUEST.get('color', '')
    users = request.REQUEST.getlist('users')

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
    else:
        task = Task()
    task.title = title
    task.desc = desc
    task.startdate = datetime.datetime.strptime(startdate, "%Y%m%d")
    task.enddate = datetime.datetime.strptime(enddate, "%Y%m%d")


    task.color = int(color)
    task.author = request.user
    task.save()
    task.users = User.objects.filter(username__in=users)
    task.save()

    RiLiWarning.objects.filter(warning_type__in=wl).filter(type='Task', fatherid=task.pk).delete()

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
    if   task.status:
        pass
        #adjustRiLiWarning(schedule.id)
    return getResult(True, u'保存成功', task.pk)


@client_login_required
@transaction.commit_on_success
def delTask(request):
    id = request.REQUEST.get('id', '')
    schedule = Task.objects.get(pk=id)
    RiLiWarning.objects.filter(type='Task', fatherid=schedule.pk).delete()
    schedule.delete()
    return getResult(True, u'删除成功', id)
  