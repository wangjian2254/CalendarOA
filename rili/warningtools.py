#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
import datetime
import threading
from rili.models import  Schedule, REPEAT_TYPE, Task, RiLiWarning
c = threading.RLock()
__author__ = u'王健'

def dateisright(date,schedule):

    if not hasattr(schedule,'repeat_type'):
        return True
    if schedule.repeat_type == REPEAT_TYPE[0][0] or (schedule.repeat_type == REPEAT_TYPE[1][0] and str(date.weekday()) in schedule.repeat_date.split(',') ) or ( schedule.repeat_type == REPEAT_TYPE[2][0] and str(date.day) in schedule.repeat_date.split(',')) or (schedule.repeat_type == REPEAT_TYPE[3][0] and date.strftime('%m%d') == schedule.startdate.strftime('%m%d')):
        return True
    return False


def dateinrange(date,schedule):
    if (schedule.startdate<=date and schedule.enddate == None) or schedule.startdate <= date <=schedule.enddate:
        return True
    if not hasattr(schedule,'repeat_type') and schedule.startdate<=date:
        return True
    return False


def adjustRiLiWarning(id,type='Schedule',wid=0):
    wquery = RiLiWarning.objects.filter(type=type,fatherid=id)
    if wid:
        wquery=wquery.filter(id=wid)
    # if 0 == wquery.count():
    #     return
    if type =='Schedule':
        obj = Schedule.objects.get(pk=id)
    elif type == 'Task':
        obj = Task.objects.get(pk=id)
    if hasattr(obj,'is_all_day') and  not obj.is_all_day:
        with c:
            currentdate = datetime.datetime.strptime('%s %s'%(obj.startdate.strftime('%Y%m%d'),obj.time_start.strftime('%H%M')),'%Y%m%d %H%M')

    else:
        currentdate = obj.startdate

    ds = currentdate.strftime('%Y%m%d%H%M')
    nowdate = datetime.datetime.now()
    with c:
        nowday = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y%m%d'),'%Y%m%d')

    for warning in wquery:
        if type == 'Task' and obj.status:
            warning.delete()
            continue
        time = datetime.timedelta(minutes=warning.timenum)
        if warning.time:
            tempdate = warning.time + datetime.timedelta(minutes=0-warning.timenum)
        else:
            with c:
                tempdate = datetime.datetime.strptime(ds,'%Y%m%d%H%M')
        if not obj.enddate or obj.enddate >= nowday:
            while time+tempdate < nowdate or ((time + tempdate > nowdate and  dateinrange(tempdate,obj)) and not dateisright(tempdate,obj)):
                if hasattr(obj,'repeat_type') and obj.repeat_type == 'yearly':
                    tempdate +=datetime.timedelta(days=365)
                else:
                    tempdate +=datetime.timedelta(days=1)
                #while time+tempdate < nowdate or ((time + tempdate > nowdate and  dateinrange(tempdate,obj)) and not dateisright(tempdate,obj)):
                #    tempdate +=datetime.timedelta(days=1)

        warning.time = time+tempdate
        if time+tempdate>nowdate and dateinrange(tempdate,obj):
            warning.is_repeat = True
            warning.is_ok = False
            warning.save()
        else:
            warning.delete()
