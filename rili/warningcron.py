#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from datetime import datetime ,timedelta
from django.http import HttpResponse
from rili.models import RiLiWarning, Schedule
from rili.warningtools import adjustRiLiWarning

from django.template import loader
from util.emailtools import send_mail
from util.rtxtools import send_rtxmsg

__author__ = u'王健'

def warningTask(request):
    nowdate = datetime.now()
    startdate = nowdate + timedelta(minutes=-15)
    for warning in RiLiWarning.objects.filter(time__lt=startdate,is_ok=False,is_repeat=True):
        if warning.type == 'Schedule':
            warning.is_ok = True
            warning.save()
            adjustRiLiWarning(warning.fatherid)

    for warning in RiLiWarning.objects.filter(time__gte=startdate,time__lte=nowdate,is_ok=False,warning_type__in=['email','rtx']):

        if warning.type == 'Schedule':

            schedule = Schedule.objects.get(pk=warning.fatherid)
            subject = u'日程提醒_%s'%schedule.title

            if warning.warning_type == 'email':
                to_mail_list = set()
                if schedule.author.email:
                    to_mail_list.add(schedule.author.email)
                for user in schedule.users.all():
                    if user.email:
                        to_mail_list.add(user.email)
                body = loader.render_to_string('schedul_email.html',
                {'schedule':schedule,'subject':subject, 'today':warning.time+timedelta(minutes=0-warning.timenum) }
                )

                send_mail(subject,body,to_mail_list,html="text/html")
            if warning.warning_type == 'rtx':
                to_rtx_list = set()
                joinuserlist = set()
                joinuserlist.add(schedule.author.first_name)
                for user in schedule.author.person_set.all():
                    to_rtx_list.add(user.rtxnum)
                for user in schedule.users.all():
                    joinuserlist.add(user.first_name)
                    if hasattr(user,'person'):
                        to_rtx_list.add(user.person.rtxnum)

                startstr = (warning.time+timedelta(minutes=0-warning.timenum)).strftime('%m月%d日 %H:%M').decode('utf-8')

                body = u'日程：%s\n开始时间：%s\n参与人：%s\n内容：%s'%(schedule.title,startstr,u'、'.join(joinuserlist),schedule.desc)

                send_rtxmsg(to_rtx_list,body.encode('gbk'),subject.encode('gbk'))
            warning.is_ok = True
            warning.save()
            adjustRiLiWarning(warning.fatherid)
    return HttpResponse('')