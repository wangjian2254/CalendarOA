#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
from rili.models import RiLiWarning, Schedule, REPEAT_TYPE

__author__ = u'王健'

def dateisright(date,schedule):
    if schedule.startdate <= date <=schedule.enddate or (schedule.startdate<=date and schedule.enddate == None):
        if schedule.repeat_type == REPEAT_TYPE[0][0] or (schedule.repeat_type == REPEAT_TYPE[1][0] and str(date.weekday()) in schedule.repeat_date.split(',') ) or ( schedule.repeat_type == REPEAT_TYPE[2][0] and str(date.day) in schedule.repeat_date.split(',')) or (schedule.repeat_type == REPEAT_TYPE[3][0] and date.strftime('%m%d') == schedule.startdate.strftime('%m%d')):
            return True
    return False


def adjustRiLiWarning(id):
    wquery = RiLiWarning.objects.filter(type='Schedule',fatherid=id,is_repeat=True,is_ok=True)
    if 0 == wquery.count():
        return
    schedule = Schedule.objects.get(pk=id)
    if not schedule.is_all_day:
        currentdate = datetime.datetime.strptime('%s %s'%(schedule.startdate.strftime('%Y%m%d'),schedule.time_start.strftime('%H%M')),'%Y%m%d %H%M')
        if schedule.enddate:
            enddate = datetime.datetime.strptime('%s %s'%(schedule.enddate.strftime('%Y%m%d'),schedule.time_start.strftime('%H%M')),'%Y%m%d %H%M')
        else:
            enddate = None
    else:
        currentdate = datetime.datetime.strptime(schedule.startdate.strftime('%Y%m%d'),'%Y%m%d')
        if schedule.enddate:
            enddate = datetime.datetime.strptime(schedule.enddate.strftime('%Y%m%d'),'%Y%m%d')
        else:
            enddate = None
    ds = currentdate.strftime('%Y%m%d%H%M')
    nowdate = datetime.datetime.now()

    for warning in wquery:
        time = datetime.timedelta(minutes=warning.timenum)
        if warning.time:
            tempdate = warning.time + datetime.timedelta(minutes=0-warning.timenum)
        else:
            tempdate = datetime.datetime.strptime(ds,'%Y%m%d%H%M')
        while time+tempdate < nowdate or not dateisright(tempdate,schedule):
            if schedule.repeat_type == 'yearly':
                tempdate +=datetime.timedelta(days=365)
            else:
                tempdate +=datetime.timedelta(days=1)
            while not dateisright(tempdate,schedule):
                tempdate +=datetime.timedelta(days=1)

            # if (enddate and tempdate>enddate) or( time+tempdate > nowdate):
            #     break

        warning.time = time+tempdate
        if time+tempdate>nowdate:
            warning.is_repeat = True
            warning.is_ok = False
        else:
            warning.is_repeat = False
            warning.is_ok = True
        warning.save()