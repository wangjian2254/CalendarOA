#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from datetime import datetime ,timedelta
import urllib
import urllib2
from django.db import transaction
from django.http import HttpResponse
import re
from CalendarOA import settings
from CalendarOA.settings import ZENTAO_HOST, DEFAULT_WARNINGTYPE, DEFAULT_WARNINGTIME
from rili.models import  Schedule,Task, Person, Group, RiLiWarning
from rili.warningtools import adjustRiLiWarning
from django.core.cache import cache
import json
from util.rtxtools import send_rtxmsg

dateformat='%Y-%m-%d'
timeformat='%Y-%m-%d %H:%M:%S'
reobj = re.compile('(?i)<[/]{0,1}[\w]{1,5}[^>]*>')

__author__ = u'王健'
def issuccess(html):
    try:
        result = json.loads(html)
    except:
        return False
    if result.get('status')=='success':
        return result
    return False

def getObjFromData(html):
    result = issuccess(html)

    if result and result.has_key('data') :
        return json.loads(result.get('data'))
def sessionRight(sessiondata):
    html=urllib.urlopen('%s/index.php?m=my&f=todo&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    result = issuccess(html)
    if result:
        return True
    else:
        return False

def loginZentao(person):
    sessiondata = cache.get('zentao_%s'%person.zentao_account)
    if not sessiondata or sessionRight(sessiondata):
        html=urllib.urlopen('%s/index.php?m=api&f=getSessionID&t=json'%ZENTAO_HOST).read()
        result = getObjFromData(html)
        sessiondata = '&%s=%s'%(result.get('sessionName'),result.get('sessionID'))
        s = urllib.urlencode({'account': person.zentao_account, 'password': person.zentao_password, 'keepLogin[]':'on'})
        request = urllib2.Request('%s/index.php?m=user&f=login&t=json%s'%(ZENTAO_HOST,sessiondata),s)
        html = urllib2.urlopen(request).read()
        if issuccess(html):
            cache.set('zentao_%s'%person.zentao_account,sessiondata,20*1000)
            return sessiondata
        else:
            return False


def zentaoTaskFun(sessiondata,person):
    tome=urllib.urlopen('%s/index.php?m=my&f=task&type=assignedTo&orderBy=id_desc&recTotal=18&recPerPage=1000&pageID=1&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    # myclosed=urllib.urlopen('%s/index.php?m=my&f=task&type=closedBy&orderBy=id_desc&recTotal=18&recPerPage=1000&pageID=1&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    # mycanceled=urllib.urlopen('%s/index.php?m=my&f=task&type=canceledBy&orderBy=id_desc&recTotal=18&recPerPage=1000&pageID=1&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    result=[]
    tomeresult=getObjFromData(tome)
    if tomeresult:
        result.extend(tomeresult.get('tasks',[]))
    # tomeresult=getObjFromData(myclosed)
    # if tomeresult:
    #     for task in tomeresult.get('tasks',[]):
    #         closedids.append(task.get('id'))
    # tomeresult=getObjFromData(mycanceled)
    # if tomeresult:
    #     for task in tomeresult.get('tasks',[]):
    #         deleteids.append(task.get('id'))
    if not result:
        return
    with transaction.commit_on_success():
        group = Group.objects.filter(author=person.user,flag='zentao')[:1]
        if 0==len(group):
            group = Group()
            group.author=person.user
            group.flag='zentao'
            group.color=0x339933
            group.name =u'禅道日程'
            group.save()
        else:
            group=group[0]

        for task in result:
            if not task.get('lastEditedBy'):
                lastEditDate = datetime.strptime(str(task.get('assignedDate')),timeformat)
            else:
                lastEditDate = datetime.strptime(str(task.get('lastEditedDate')),timeformat)
            try:
                startTime = datetime.strptime(str(task.get('estStarted')),dateformat)
            except:
                startTime = datetime.strptime(str(task.get('assignedDate')).split(' ')[0],dateformat)
            try:
                endTime = datetime.strptime(str(task.get('deadline')),dateformat)
            except:
                endTime = datetime.strptime(str(task.get('assignedDate')).split(' ')[0],dateformat)
            # endTime = datetime.strptime(str(task.get('deadline')),dateformat)
            schedultTitle = task.get('name')
            schedultDesc = u'项目：%s\n需求：%s\n%s'%(task.get('projectName',u'无'),task.get('storyTitle') if task.get('storyTitle') else u'无',task.get('desc',u'无'))
            schedultDesc = reobj.sub(u'\n',schedultDesc)
            schedultDesc = '\n'.join(schedultDesc.split())
            #schedultDesc = u'\n'.join(re.findall('(?i)<p [^>]*>(.*?)</p>',schedultDesc.replace('&nbsp;',' ')))
            objid=task.get('id')
            if task.get('status')=='done':
                taskitemlist=Task.objects.filter(flag='Task',flagid=objid)[:1]
                if len(taskitemlist)==1:
                    taskitem=taskitemlist[0]
                else:
                    taskitem=Task()
                    taskitem.flag='Task'
                    taskitem.flagid=objid
                    taskitem.color = 0x339933
                if not taskitem.pk or taskitem.lastUpdateTime<lastEditDate:
                    taskitem.author = person.user
                    taskitem.desc = schedultDesc
                    taskitem.enddate = endTime
                    taskitem.startdate = startTime
                    taskitem.title =schedultTitle
                    taskitem.desc = schedultDesc
                    taskitem.status = False
                    taskitem.warning_type = ','.join(DEFAULT_WARNINGTYPE)
                    taskitem.warning_time = ','.join(DEFAULT_WARNINGTIME)
                    taskitem.save(lastUpdateTime=lastEditDate)
                    if person.rtxnum:
                        taskitem.sendRTX(person.rtxnum)
            elif task.get('status') in ('wait','doing'):
                schedultlist=Schedule.objects.filter(flag='Task',flagid=objid)[:1]
                if len(schedultlist)==1:
                    schedult=schedultlist[0]
                else:
                    schedult=Schedule()
                    schedult.color = 0x339933
                    schedult.flag='Task'
                    schedult.flagid=objid
                if not schedult.pk or schedult.lastUpdateTime<lastEditDate:
                    schedult.is_all_day=True
                    schedult.repeat_type = 'daily'
                    schedult.repeat_date = ','.join(['0','1','2','3','4'])
                    schedult.author=person.user
                    schedult.group = group
                    schedult.startdate=startTime
                    schedult.enddate=endTime
                    schedult.title=schedultTitle
                    schedult.desc=schedultDesc
                    schedult.warning_type = ','.join(DEFAULT_WARNINGTYPE)
                    schedult.warning_time = ','.join(DEFAULT_WARNINGTIME)
                    schedult.save(lastUpdateTime=lastEditDate)
                    if person.rtxnum:
                        schedult.sendRTX(person.rtxnum)

                taskitemlist=Task.objects.filter(flag='Task',flagid=objid)[:1]
                if len(taskitemlist)==1:
                    taskitem=taskitemlist[0]
                else:
                    taskitem=Task()
                    taskitem.flag='Task'
                    taskitem.flagid=objid
                    taskitem.color = 0x339933
                if not taskitem.pk or taskitem.lastUpdateTime<lastEditDate:
                    taskitem.author = person.user
                    taskitem.desc = schedultDesc
                    taskitem.enddate = None
                    taskitem.startdate = endTime
                    taskitem.title =schedultTitle
                    taskitem.desc = schedultDesc
                    taskitem.status = False
                    taskitem.warning_type = ','.join(DEFAULT_WARNINGTYPE)
                    taskitem.warning_time = ','.join(DEFAULT_WARNINGTIME)
                    taskitem.save(lastUpdateTime=lastEditDate)



def zentaoBugFun(sessiondata,person):
    tome=urllib.urlopen('%s/index.php?m=my&f=bug&type=assignedTo&orderBy=id_desc&recTotal=6&recPerPage=1000&pageID=1&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    # myclosed=urllib.urlopen('%s/index.php?m=my&f=bug&type=closedBy&orderBy=id_desc&recTotal=6&recPerPage=1000&pageID=1&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    # mycanceled=urllib.urlopen('%s/index.php?m=my&f=bug&type=resolvedBy&orderBy=id_desc&recTotal=6&recPerPage=1000&pageID=1&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
    result=[]
    tomeresult=getObjFromData(tome)
    if tomeresult:
        result.extend(tomeresult.get('bugs',[]))
    # tomeresult=getObjFromData(myclosed)
    # if tomeresult:
    #     for task in tomeresult.get('bugs',[]):
    #         closedids.append(task.get('id'))
    # tomeresult=getObjFromData(mycanceled)
    # if tomeresult:
    #     for task in tomeresult.get('bugs',[]):
    #         deleteids.append(task.get('id'))
    if not result:
        return
    with transaction.commit_on_success():
        for task in result:
            if not task.get('lastEditedBy'):
                lastEditDate = datetime.strptime(str(task.get('assignedDate')),timeformat)
            else:
                lastEditDate = datetime.strptime(str(task.get('lastEditedDate')),timeformat)
            startTime = datetime.strptime(str(task.get('assignedDate').split(' ')[0]),dateformat)
            endTime = None
            if task.get('status')=='resolved':
                schedultTitle = u'待确认 Bug_%s'%task.get('title')
                schedultDesc = u'Bug 已修复，需要确认'
            else:
                schedultTitle = u'Bug_%s'%task.get('title')
                schedultDesc = u'发现Bug, 请尽快修复，详情请到禅道界面浏览。'

            objid=task.get('id')
            if task.get('status') in ('active','resolved'):
                taskitemlist=Task.objects.filter(flag='Bug',flagid=objid)[:1]
                if len(taskitemlist)==1:
                    taskitem=taskitemlist[0]
                else:
                    taskitem=Task()
                    taskitem.flag='Bug'
                    taskitem.flagid=objid
                    taskitem.color = 0xff0000
                if not taskitem.pk or taskitem.lastUpdateTime<lastEditDate:
                    taskitem.author = person.user
                    taskitem.enddate = endTime
                    taskitem.startdate = startTime
                    taskitem.title =schedultTitle
                    taskitem.desc = schedultDesc
                    taskitem.status = False
                    taskitem.warning_type = ','.join(DEFAULT_WARNINGTYPE)
                    taskitem.warning_time = ','.join(DEFAULT_WARNINGTIME)
                    taskitem.save(lastUpdateTime=lastEditDate)
                    if person.rtxnum:
                        taskitem.sendRTX(person.rtxnum)




def zentaoTask(request):
    successlist=[]
    errorlist=[]
    nosynclist=[]

    for person in Person.objects.filter(user__is_active=True):
        if person.zentao_account and person.zentao_password:
            try:
                sessiondata = loginZentao(person)
                if not sessiondata:
                    continue
                zentaoTaskFun(sessiondata,person)
                zentaoBugFun(sessiondata,person)
                successlist.append('%s:%s'%(person.user.username,person.user.first_name))
            except Exception,e:
                errorlist.append('%s:%s'%(person.user.username,person.user.first_name))

        else:
            nosynclist.append('%s:%s'%(person.user.username,person.user.first_name))
    return HttpResponse(u'<p><b>同步错误用户：</b></p><p>%s</p>'%'</p><p>'.join(errorlist))



def zentaoStatusTask(request):
    successlist=[]
    errorlist=[]
    nosynclist=[]
    for person in Person.objects.filter(user__is_active=True):
        if person.zentao_account and person.zentao_password:
            try:
                sessiondata = loginZentao(person)
                if not sessiondata:
                    continue
                for task in Task.objects.filter(author=person.user,status=False,flag='Task').order_by('lastUpdateTime'):
                    with transaction.commit_on_success():
                        tome=urllib.urlopen('%s/index.php?m=task&f=view&taskID=%s&t=json%s'%(ZENTAO_HOST,task.flagid,sessiondata)).read()
                        item=getObjFromData(tome)
                        if item.get('task').get('status')=='closed':
                            task.status=True
                            task.save()
                        elif item.get('task').get('status')=='cancel':
                            task.delete()
                successlist.append('%s:%s'%(person.user.username,person.user.first_name))
            except Exception,e:
                errorlist.append('%s:%s'%(person.user.username,person.user.first_name))

        else:
            nosynclist.append('%s:%s'%(person.user.username,person.user.first_name))
    return HttpResponse(u'<p><b>同步错误用户：</b></p><p>%s</p>'%'</p><p>'.join(errorlist))

def zentaoStatusBug(request):
    successlist=[]
    errorlist=[]
    nosynclist=[]
    for person in Person.objects.filter(user__is_active=True):
        if person.zentao_account and person.zentao_password:
            try:
                sessiondata = loginZentao(person)
                if not sessiondata:
                    continue
                for task in Task.objects.filter(author=person.user,status=False,flag='Bug').order_by('lastUpdateTime'):
                    with transaction.commit_on_success():
                        tome=urllib.urlopen('%s/index.php?m=bug&f=view&bugID=%s&t=json%s'%(ZENTAO_HOST,task.flagid,sessiondata)).read()
                        item=getObjFromData(tome)
                        if item.get('bug').get('status')=='closed':
                            task.status=True
                            task.save()
                successlist.append('%s:%s'%(person.user.username,person.user.first_name))
            except Exception,e:
                errorlist.append('%s:%s'%(person.user.username,person.user.first_name))

        else:
            nosynclist.append('%s:%s'%(person.user.username,person.user.first_name))
    return HttpResponse(u'<p><b>同步错误用户：</b></p><p>%s</p>'%'</p><p>'.join(errorlist))