#coding=utf-8
#Date: 11-12-8
#Time: 下午10:28
from datetime import datetime ,timedelta
import urllib
import urllib2
from django.http import HttpResponse
from CalendarOA import settings
from CalendarOA.settings import ZENTAO_HOST
from rili.models import  Schedule,Task, Person
from rili.warningtools import adjustRiLiWarning
from django.core.cache import cache
import json


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
    # /index.php?m=my&f=todo
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

def zentaoTask(request):
    for person in Person.objects.filter(user__is_active=True):
        if person.zentao_account and person.zentao_password:
            try:
                sessiondata = loginZentao(person)
                if not sessiondata:
                    continue
                html=urllib.urlopen('%s/index.php?m=my&f=task&t=json%s'%(ZENTAO_HOST,sessiondata)).read()
                result=getObjFromData(html)
                pass
            except:
                pass


    return HttpResponse('')
'''
account=wangjian&password=05992254wj&keepLogin%5B%5D=on&referer=http%3A%2F%2Fpms.zxxsbook.com%2Findex.php%3Fm%3Dmy%26f%3Dtask
'''