#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import threading
import uuid
import datetime
from django.contrib.auth.models import User
from CalendarOA.settings import APP_HOST
from rili.models import Group, Schedule

c = threading.RLock()
__author__ = u'王健'

def regAMB(person):

    if 0 == Group.objects.filter(flag='system_amb').count():
        systemuser = User()
        systemuser.username = 'system'
        systemuser.set_password('admin')
        systemuser.is_active = False
        systemuser.first_name = u'系统'
        systemuser.save()
        group = Group()
        group.author = systemuser
        group.name = u'阿米巴日志'
        group.color = 0x3366FF
        group.flag = 'system_amb'
        group.save()
        schedule = Schedule()
        schedule.title = u'阿米巴日志'
        schedule.desc = u'请及时填写阿米巴日志:\n[阿米巴日志|http://www.szhtkj.com.cn/amb/login.aspx]\n如需修改请访问：[日程管理|%s]'%(APP_HOST,)
        schedule.author = systemuser
        schedule.group = group
        schedule.color = 0x3366ff
        schedule.repeat_type = 'weekly'
        schedule.repeat_date =','.join(['0','1','2','3','4'])
        schedule.startdate = datetime.datetime.now()
        schedule.enddate = None

        with c:
            schedule.time_start = datetime.datetime.strptime('1700','%H%M')
            schedule.time_end = datetime.datetime.strptime('1730','%H%M')
        schedule.warning_type =','.join(['rtx'])
        schedule.warning_time =','.join(['0','-480'])
        schedule.save()
        schedule = Schedule()
        schedule.title = u'目标卡'
        schedule.desc = u'月初了，请及时填写目标卡\n[目标卡|http://www.szhtkj.com.cn/hwglxt/]\n 如需修改请访问：[日程管理|%s]'%(APP_HOST,)
        schedule.author = systemuser
        schedule.group = group
        schedule.color = 0x3366ff
        schedule.repeat_type = 'monthly'
        schedule.repeat_date =','.join(['1','2','3'])
        schedule.startdate = datetime.datetime.now()
        schedule.enddate = None
        with c:
            schedule.time_start = datetime.datetime.strptime('0900','%H%M')
            schedule.time_end = datetime.datetime.strptime('0930','%H%M')
        schedule.warning_type =','.join(['rtx','email'])
        schedule.warning_time =','.join(['0','-10'])
        schedule.save()

    else:
        group = Group.objects.filter(flag='system_amb')[0]
    if person.rtxnum:
        if  0==group.observers.filter(username=person.user.username).count():
            group.observers.add(person.user)
            group.save()
    else:
        if  0!=group.observers.filter(username=person.user.username).count():
            group.observers.remove(person.user)
            group.save()